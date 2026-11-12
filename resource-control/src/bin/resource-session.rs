//! Fresh-session bounded client for the trusted local resource gateway.
//! This binary carries selectors only; authority comes from the Unix peer UID.
use serde_json::{json, Value};
use std::io::{Read, Write};
use std::os::fd::FromRawFd;
use std::os::unix::ffi::OsStrExt;
use std::os::unix::net::UnixStream;
use std::path::Path;
use std::time::{Duration, Instant};

const MAX_RESPONSE: usize = 8 * 1024;
const CONNECT_TIMEOUT_MS: i32 = 2_000;
const IO_TIMEOUT: Duration = Duration::from_secs(3);

#[derive(Debug)]
enum ClientError {
    Invalid(String),
    Unknown(String),
}

fn valid_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 160
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || b"-_.:/".contains(&byte))
}

fn usage() -> &'static str {
    "usage: resource-session SOCKET resume JOB LAUNCH | launch JOB LAUNCH EXPECTED_CATALOG | poll JOB LAUNCH | stop JOB LAUNCH STOP_ID | stop-graceful JOB LAUNCH STOP_ID GRACE_MS | finalize JOB LAUNCH OUTCOME | cancel-unlaunched JOB"
}

fn request(args: &[String]) -> Result<(String, Value), ClientError> {
    if args.len() < 3 {
        return Err(ClientError::Invalid(usage().into()));
    }
    let socket = &args[0];
    let path = Path::new(socket);
    let bytes = path.as_os_str().as_bytes();
    if !path.is_absolute() || bytes.is_empty() || bytes.len() >= 108 || bytes.contains(&0) {
        return Err(ClientError::Invalid(
            "SOCKET must be an absolute Unix socket path shorter than 108 bytes".into(),
        ));
    }
    let action = &args[1];
    let request = match action.as_str() {
        "resume" if args.len() == 4 && valid_id(&args[2]) && valid_id(&args[3]) => {
            json!({"op":"local_resume","job_id":args[2],"launch_id":args[3]})
        }
        "launch" if args.len() == 5 && valid_id(&args[2]) && valid_id(&args[3]) => {
            let revision = args[4].parse::<i64>().map_err(|_| {
                ClientError::Invalid("EXPECTED_CATALOG must be a nonnegative integer".into())
            })?;
            if revision < 0 {
                return Err(ClientError::Invalid(
                    "EXPECTED_CATALOG must be a nonnegative integer".into(),
                ));
            }
            json!({"op":"local_launch","job_id":args[2],"launch_id":args[3],"expected_catalog":revision})
        }
        "poll" if args.len() == 4 && valid_id(&args[2]) && valid_id(&args[3]) => {
            json!({"op":"local_poll","job_id":args[2],"launch_id":args[3]})
        }
        "stop" if args.len() == 5 && valid_id(&args[2]) && valid_id(&args[3]) && valid_id(&args[4]) => {
            json!({"op":"local_stop","job_id":args[2],"launch_id":args[3],"stop_id":args[4]})
        }
        "stop-graceful" if args.len() == 6 && valid_id(&args[2]) && valid_id(&args[3]) && valid_id(&args[4]) => {
            let grace_ms=args[5].parse::<u64>().map_err(|_|ClientError::Invalid("GRACE_MS must be an integer from 1 through 2000".into()))?;
            if !(1..=2000).contains(&grace_ms){return Err(ClientError::Invalid("GRACE_MS must be an integer from 1 through 2000".into()));}
            json!({"op":"local_stop_graceful","job_id":args[2],"launch_id":args[3],"stop_id":args[4],"grace_ms":grace_ms})
        }
        "finalize" if args.len() == 5
            && valid_id(&args[2])
            && valid_id(&args[3])
            && ["completed", "failed", "cancelled", "interrupted"].contains(&args[4].as_str()) =>
        {
            json!({"op":"local_finalize","job_id":args[2],"launch_id":args[3],"outcome":args[4]})
        }
        "cancel-unlaunched" if args.len()==3&&valid_id(&args[2])=>{
            json!({"op":"local_cancel_unlaunched","job_id":args[2]})
        }
        _ => return Err(ClientError::Invalid(usage().into())),
    };
    Ok((socket.clone(), request))
}

fn connect_bounded(path: &str) -> std::io::Result<UnixStream> {
    let path_bytes = Path::new(path).as_os_str().as_bytes();
    // The caller validated an absolute, NUL-free path shorter than sun_path.
    let fd = unsafe {
        libc::socket(
            libc::AF_UNIX,
            libc::SOCK_STREAM | libc::SOCK_CLOEXEC | libc::SOCK_NONBLOCK,
            0,
        )
    };
    if fd < 0 {
        return Err(std::io::Error::last_os_error());
    }
    let mut address: libc::sockaddr_un = unsafe { std::mem::zeroed() };
    address.sun_family = libc::AF_UNIX as libc::sa_family_t;
    for (slot, byte) in address.sun_path.iter_mut().zip(path_bytes.iter().copied()) {
        *slot = byte as libc::c_char;
    }
    let address_len = (std::mem::size_of::<libc::sa_family_t>() + path_bytes.len() + 1)
        as libc::socklen_t;
    let connect_result = unsafe {
        libc::connect(
            fd,
            (&address as *const libc::sockaddr_un).cast::<libc::sockaddr>(),
            address_len,
        )
    };
    if connect_result != 0 {
        let error = std::io::Error::last_os_error();
        if error.raw_os_error() != Some(libc::EINPROGRESS)
            && error.raw_os_error() != Some(libc::EAGAIN)
        {
            unsafe { libc::close(fd) };
            return Err(error);
        }
        let mut poll_fd = libc::pollfd { fd, events: libc::POLLOUT, revents: 0 };
        let polled = unsafe { libc::poll(&mut poll_fd, 1, CONNECT_TIMEOUT_MS) };
        if polled <= 0 {
            let error = if polled == 0 {
                std::io::Error::new(std::io::ErrorKind::TimedOut, "Unix socket connect timed out")
            } else {
                std::io::Error::last_os_error()
            };
            unsafe { libc::close(fd) };
            return Err(error);
        }
        let mut socket_error: libc::c_int = 0;
        let mut error_len = std::mem::size_of::<libc::c_int>() as libc::socklen_t;
        let getsockopt = unsafe {
            libc::getsockopt(
                fd,
                libc::SOL_SOCKET,
                libc::SO_ERROR,
                (&mut socket_error as *mut libc::c_int).cast(),
                &mut error_len,
            )
        };
        if getsockopt != 0 || socket_error != 0 {
            let error = if getsockopt != 0 {
                std::io::Error::last_os_error()
            } else {
                std::io::Error::from_raw_os_error(socket_error)
            };
            unsafe { libc::close(fd) };
            return Err(error);
        }
    }
    // SAFETY: fd is an open socket and ownership transfers to UnixStream here.
    let stream = unsafe { UnixStream::from_raw_fd(fd) };
    stream.set_nonblocking(false)?;
    stream.set_read_timeout(Some(IO_TIMEOUT))?;
    stream.set_write_timeout(Some(IO_TIMEOUT))?;
    Ok(stream)
}

fn exchange(path: &str, request: &Value) -> Result<Value, ClientError> {
    let mut stream = connect_bounded(path)
        .map_err(|_| ClientError::Unknown("connection or request outcome is unknown".into()))?;
    let bytes = serde_json::to_vec(request)
        .map_err(|_| ClientError::Invalid("request serialization failed".into()))?;
    stream
        .write_all(&bytes)
        .map_err(|_| ClientError::Unknown("request may have been applied; response was not confirmed".into()))?;
    stream
        .shutdown(std::net::Shutdown::Write)
        .map_err(|_| ClientError::Unknown("request may have been applied; response was not confirmed".into()))?;
    let mut response = Vec::new();
    let mut chunk = [0u8; 1024];
    let deadline = Instant::now() + IO_TIMEOUT;
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            return Err(ClientError::Unknown("response timed out".into()));
        }
        stream
            .set_read_timeout(Some(remaining))
            .map_err(|_| ClientError::Unknown("response read deadline could not be enforced".into()))?;
        let read = stream
            .read(&mut chunk)
            .map_err(|_| ClientError::Unknown("response was interrupted or timed out".into()))?;
        if read == 0 {
            break;
        }
        if response.len() + read > MAX_RESPONSE {
            return Err(ClientError::Unknown("response exceeded the 8 KiB limit".into()));
        }
        response.extend_from_slice(&chunk[..read]);
    }
    let decoded: Value = serde_json::from_slice(&response)
        .map_err(|_| ClientError::Unknown("response was empty, malformed, or truncated".into()))?;
    let valid_gateway_reply = match decoded.get("ok") {
        Some(Value::Bool(true)) => decoded.get("result").is_some_and(Value::is_object),
        Some(Value::Bool(false)) => decoded.get("error").is_some_and(Value::is_string),
        _ => false,
    };
    if !decoded.is_object() || !valid_gateway_reply {
        return Err(ClientError::Unknown("response did not match the gateway reply shape".into()));
    }
    Ok(decoded)
}

fn run() -> Result<Value, ClientError> {
    let args: Result<Vec<String>, _> = std::env::args_os()
        .skip(1)
        .map(|value| value.into_string().map_err(|_| ()))
        .collect();
    let args = args.map_err(|_| ClientError::Invalid("arguments must be valid UTF-8".into()))?;
    let (socket, request) = request(&args)?;
    exchange(&socket, &request)
}

fn main() {
    match run() {
        Ok(response) => {
            println!("{}", serde_json::to_string(&response).unwrap_or_else(|_| "{}".into()));
            if response.get("ok") == Some(&Value::Bool(false)) {
                std::process::exit(3);
            }
        }
        Err(ClientError::Invalid(message)) => {
            println!("{}", json!({"ok":false,"outcome":"invalid_input","error":message}));
            std::process::exit(2);
        }
        Err(ClientError::Unknown(message)) => {
            println!("{}", json!({"ok":false,"outcome":"outcome_unknown","error":message}));
            std::process::exit(4);
        }
    }
}
