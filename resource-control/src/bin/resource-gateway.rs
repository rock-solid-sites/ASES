//! Restricted Linux Unix-socket gateway. No shell execution, no model inference,
//! no unscoped admin operation exposed to orchestrator peers.
#[cfg(not(target_os="linux"))]
compile_error!("resource-gateway currently requires Linux SO_PEERCRED");

use ases_resource_control::{access::Policy, now, Store};
use serde_json::{json, Value};
use std::fs;
use std::io::{Read, Write};
use std::os::fd::AsRawFd;
use std::os::unix::fs::PermissionsExt;
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;

const MAX_MESSAGE: u64 = 1024 * 1024;

fn peer_uid(stream:&UnixStream)->std::io::Result<u32>{
    let mut credentials=std::mem::MaybeUninit::<libc::ucred>::uninit();
    let mut len=std::mem::size_of::<libc::ucred>() as libc::socklen_t;
    // SAFETY: Linux SO_PEERCRED writes precisely libc::ucred into a buffer
    // whose size is explicitly supplied. The file descriptor is owned by stream.
    let rc=unsafe {
        libc::getsockopt(
            stream.as_raw_fd(),libc::SOL_SOCKET,libc::SO_PEERCRED,
            credentials.as_mut_ptr().cast(),&mut len
        )
    };
    if rc!=0 {return Err(std::io::Error::last_os_error());}
    if len as usize != std::mem::size_of::<libc::ucred>() {
        return Err(std::io::Error::new(std::io::ErrorKind::InvalidData,"bad SO_PEERCRED length"));
    }
    // SAFETY: getsockopt succeeded and confirmed the output buffer length.
    Ok(unsafe {credentials.assume_init()}.uid)
}
fn handle(mut conn:UnixStream,db:&Path,policy:&Policy,controller:&Path)->std::io::Result<()> {
    conn.set_read_timeout(Some(Duration::from_secs(4)))?;
    conn.set_write_timeout(Some(Duration::from_secs(4)))?;
    let answer=(||->Result<Value,Box<dyn std::error::Error>>{
        let uid=peer_uid(&conn)?;
        let mut input=Vec::new();
        std::io::Read::by_ref(&mut conn).take(MAX_MESSAGE+1).read_to_end(&mut input)?;
        if input.len() as u64>MAX_MESSAGE {
            return Err("request exceeds 1 MiB".into());
        }
        let message:Value=serde_json::from_slice(&input)?;
        let store=Store::open(db)?;
        let grant=policy.authorize(uid,&message,&store)?;
        let op=message.get("op").and_then(Value::as_str).ok_or("operation missing")?;
        let mut child=Command::new(controller)
            .arg(db).arg("request").arg("-")
            .stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped())
            .spawn()?;
        child.stdin.take().ok_or("controller stdin missing")?
            .write_all(&input)?;
        let output=child.wait_with_output()?;
        if !output.status.success() {
            return Err(format!("controller rejected authorized request: {}",
                String::from_utf8_lossy(&output.stderr).chars().take(350).collect::<String>()).into());
        }
        let response:Value=serde_json::from_slice(&output.stdout)?;
        Ok(policy.filter_result(&grant,op,response))
    })();
    let out=match answer {
        Ok(v)=>v,
        Err(e)=>{
            eprintln!("gateway rejected request at {}: {}",now(),e);
            json!({"ok":false,"error":e.to_string()})
        }
    };
    conn.write_all(serde_json::to_string(&out)?.as_bytes())?;
    conn.write_all(b"\n")?;
    conn.flush()
}
fn main()->Result<(),Box<dyn std::error::Error>> {
    let mut args=std::env::args_os().skip(1);
    let db=PathBuf::from(args.next().ok_or("usage: resource-gateway DB SOCKET POLICY CONTROLLER_BINARY")?);
    let socket=PathBuf::from(args.next().ok_or("missing socket")?);
    let policy_path=PathBuf::from(args.next().ok_or("missing policy")?);
    let controller=PathBuf::from(args.next().ok_or("missing trusted controller binary")?);
    if args.next().is_some() {return Err("unexpected arguments".into());}
    if !controller.is_absolute() {return Err("controller binary must be an absolute path".into());}
    if socket.exists() {return Err("socket already exists; remove only after confirming no server owns it".into());}
    // Restrict SQLite WAL and database file creation to this privileged account.
    // SAFETY: the process is a dedicated launcher; changing umask is intended
    // before opening the database or creating the socket.
    unsafe {libc::umask(0o077);}
    let _:Store=Store::open(&db)?;
    let policy:Policy=serde_json::from_slice(&fs::read(&policy_path)?)?;
    if policy.administrators.is_empty() && policy.callers.is_empty() {
        return Err("gateway policy contains no authorized principals".into());
    }
    let listener=UnixListener::bind(&socket)?;
    fs::set_permissions(&socket,fs::Permissions::from_mode(0o660))?;
    eprintln!("ASES restricted resource gateway listening at {}",socket.display());
    for stream in listener.incoming() {
        match stream {
            Ok(stream)=>{if let Err(e)=handle(stream,&db,&policy,&controller) {
                eprintln!("gateway I/O error at {}: {}",now(),e);
            }}
            Err(e)=>eprintln!("gateway accept error: {e}"),
        }
    }
    Ok(())
}
