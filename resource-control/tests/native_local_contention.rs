//! Cross-gateway contention and lost-reply histories for the optional local supervisor.
//! Both gateways share the existing Store as the single dispatch arbiter; each
//! gateway retains only the Child it actually spawned.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::Policy;
use ases_resource_control::catalog::Account;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "contention-account";
const PROJECT: &str = "contention-project";
const ENVIRONMENT: &str = "contention-environment";

fn admin_policy() -> Policy { Policy { administrators: vec![unsafe {libc::geteuid()}], callers: vec![] } }
fn account() -> Account { Account { id:ACCOUNT.into(), provider:"local".into(), payer_ref:"test-only".into(),
    registration_status:"verified".into(), credential_status:"working".into(), entitlement_status:"active".into(),
    allowed_projects:vec![PROJECT.into()], source:"synthetic-native-local-contention".into(), observed_at:now(), ttl_seconds:3600 } }
fn meter() -> Meter { Meter { id:"contention-meter".into(), account:ACCOUNT.into(), provider:"local".into(),
    product:"fixed-contention-worker".into(), period:"contention-test".into(), unit:"units".into(), limit:100, guard:0,
    observed_at:now(), ttl_seconds:3600, source:"synthetic-native-local-contention".into(), period_start:None, period_end:None,
    price_per_unit_micros:0, price_currency:None, chargeable:false } }
fn environment() -> Environment { Environment { id:ENVIRONMENT.into(), account:ACCOUNT.into(), provider:"local".into(),
    max_parallel:1, observed_at:now(), ttl_seconds:3600, source:"synthetic-native-local-contention".into() } }
fn proposal(job:&str)->Proposal { Proposal { job_id:job.into(), account_id:ACCOUNT.into(), project_id:PROJECT.into(),
    environment_id:ENVIRONMENT.into(), estimated_wall_seconds:60, claims:vec![Claim{meter_id:"contention-meter".into(),amount:50}],
    paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None } }
fn setup(dir:&Path,job:&str)->(PathBuf,i64){
    let db=dir.join("control.sqlite");let mut store=Store::open(&db).unwrap();
    store.register_account(&account()).unwrap();store.register_meter(&meter()).unwrap();store.register_environment(&environment()).unwrap();
    let revision=store.catalog_version().unwrap();store.reserve(&proposal(job),revision,now()).unwrap();
    store.acknowledge(job,&format!("ack-{job}"),revision,now()).unwrap();(db,revision)
}
fn profile(marker:&Path,release:&Path)->Value{json!({
    "program":std::env::current_exe().unwrap(),"args":["--exact","contention_fixed_worker","--nocapture"],
    "cwd":std::env::current_dir().unwrap(),"env":{"ASES_CONTENTION_MARKER":marker,"ASES_CONTENTION_RELEASE":release},
    "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT
})}
struct Gateway{child:Child,socket:PathBuf}
impl Gateway{
    fn start(dir:&Path,name:&str,db:&Path,profile:&Value)->Self{
        let socket=dir.join(format!("{name}.sock"));let policy=dir.join(format!("{name}-policy.json"));let prof=dir.join(format!("{name}-profile.json"));
        fs::write(&policy,serde_json::to_vec(&admin_policy()).unwrap()).unwrap();fs::write(&prof,serde_json::to_vec(profile).unwrap()).unwrap();
        let child=Command::new(env!("CARGO_BIN_EXE_resource-gateway")).arg(db).arg(&socket).arg(policy)
            .arg(env!("CARGO_BIN_EXE_ases-resource-control")).arg(prof).stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap();
        let until=Instant::now()+Duration::from_secs(10);while Instant::now()<until{if socket.exists(){return Self{child,socket};}thread::sleep(Duration::from_millis(10));}
        panic!("gateway socket did not appear: {}",socket.display())
    }
    fn send(&self,request:Value)->Value{send_to(&self.socket,&request)}
}
impl Drop for Gateway{fn drop(&mut self){let _=self.child.kill();let _=self.child.wait();}}
fn send_to(socket:&Path,request:&Value)->Value{
    let mut stream=UnixStream::connect(socket).unwrap();stream.write_all(serde_json::to_string(request).unwrap().as_bytes()).unwrap();
    stream.shutdown(std::net::Shutdown::Write).unwrap();let mut bytes=Vec::new();stream.read_to_end(&mut bytes).unwrap();serde_json::from_slice(&bytes).unwrap()
}
struct Release(PathBuf);impl Drop for Release{fn drop(&mut self){let _=fs::write(&self.0,b"release\n");}}
fn wait_for(path:&Path){let until=Instant::now()+Duration::from_secs(10);while Instant::now()<until{if path.exists(){return}thread::sleep(Duration::from_millis(10));}panic!("worker did not reach marker {}",path.display())}
fn worker_lines(path:&Path)->Vec<Value>{fs::read_to_string(path).unwrap_or_default().lines().map(|s|serde_json::from_str(s).unwrap()).collect()}
fn worker_alive(pid:u32,token:&str)->bool{let Ok(stat)=fs::read_to_string(format!("/proc/{pid}/stat"))else{return false};let Some((_,tail))=stat.rsplit_once(") ")else{return false};let mut fields=tail.split_whitespace();let state=fields.next().and_then(|v|v.chars().next());let start=fields.nth(18);matches!(state,Some('R'|'S'))&&start==Some(token)}
fn events(db:&Path,job:&str)->Vec<Value>{Store::open(db).unwrap().event_log(Some(job)).unwrap()}
fn remaining(db:&Path)->i64{Store::open(db).unwrap().balances(now()).unwrap().into_iter().find(|b|b.meter_id=="contention-meter").unwrap().active_reserved_remaining}
fn persist(name:&str,value:Value){if let Some(path)=std::env::var_os("ASES_LOCAL_CONTENTION_EVIDENCE_DIR"){let path=PathBuf::from(path);fs::create_dir_all(&path).unwrap();fs::write(path.join(name),serde_json::to_vec_pretty(&value).unwrap()).unwrap();}}
fn source_hashes()->Value{let root=PathBuf::from(env!("CARGO_MANIFEST_DIR"));let mut out=serde_json::Map::new();for p in ["src/local.rs","src/bin/resource-gateway.rs","src/lib.rs","tests/native_local_contention.rs","../docs/research/phase-ii-local-execution/CONTENTION.md"]{if let Ok(b)=fs::read(root.join(p)){out.insert(p.into(),json!(format!("{:x}",Sha256::digest(b))));}}Value::Object(out)}

/// Fixed harmless process selected by the trusted profile; never accepts commands from requests.
#[test]
fn contention_fixed_worker(){let Some(marker)=std::env::var_os("ASES_CONTENTION_MARKER") else{return};let release=PathBuf::from(std::env::var_os("ASES_CONTENTION_RELEASE").unwrap());let pid=std::process::id();let stat=fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();let token=stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap();
    let mut file=OpenOptions::new().create(true).append(true).open(marker).unwrap();serde_json::to_writer(&mut file,&json!({"pid":pid,"start_token":token})).unwrap();file.write_all(b"\n").unwrap();file.sync_all().unwrap();
    let until=Instant::now()+Duration::from_secs(20);while !release.exists()&&Instant::now()<until{thread::sleep(Duration::from_millis(10));}std::process::exit(0);
}

#[test]
fn two_gateways_contend_for_one_dispatch_and_only_child_owner_can_stop(){
    let dir=tempfile::tempdir().unwrap();let(db,revision)=setup(dir.path(),"contended-job");let marker=dir.path().join("children.jsonl");let release=dir.path().join("release");let _release=Release(release.clone());let trusted=profile(&marker,&release);
    let first=Gateway::start(dir.path(),"gateway-a",&db,&trusted);let second=Gateway::start(dir.path(),"gateway-b",&db,&trusted);
    let request=json!({"op":"local_launch","job_id":"contended-job","launch_id":"contended-launch","expected_catalog":revision});
    let socket_a=first.socket.clone();let socket_b=second.socket.clone();let req_a=request.clone();let req_b=request.clone();
    let a=thread::spawn(move||send_to(&socket_a,&req_a));let b=thread::spawn(move||send_to(&socket_b,&req_b));let reply_a=a.join().unwrap();let reply_b=b.join().unwrap();wait_for(&marker);
    let children=worker_lines(&marker);assert_eq!(children.len(),1,"two gateways must consume one dispatch only");
    let (owner,loser,owner_reply,loser_reply)=if reply_a["result"]["state"]=="running"{(&first,&second,&reply_a,&reply_b)}else{(&second,&first,&reply_b,&reply_a)};
    assert_eq!(owner_reply["ok"],true);assert_eq!(owner_reply["result"]["state"],"running");assert_eq!(loser_reply["ok"],true);assert_eq!(loser_reply["result"]["state"],"unknown");
    let mut records=vec![json!({"phase":"concurrent-launch","request":request,"gateway_a":reply_a,"gateway_b":reply_b,"worker_count":children.len()})];
    let pid=children[0]["pid"].as_u64().unwrap();
    let caller_pid=json!({"op":"local_stop","job_id":"contended-job","launch_id":"contended-launch","stop_id":"shared-stop","pid":pid});
    let rejected=loser.send(caller_pid.clone());assert_eq!(rejected["ok"],false,"caller-supplied PID is rejected");
    let premature=json!({"op":"local_finalize","job_id":"contended-job","launch_id":"contended-launch","outcome":"cancelled"});
    let before_exit=loser.send(premature.clone());assert_eq!(before_exit["ok"],false,"losing gateway has no exact exit evidence");assert_eq!(remaining(&db),50);
    let unknown_stop=json!({"op":"local_stop","job_id":"contended-job","launch_id":"contended-launch","stop_id":"shared-stop"});let unknown_reply=loser.send(unknown_stop.clone());assert_eq!(unknown_reply["ok"],true);assert_eq!(unknown_reply["result"]["state"],"unknown");
    assert_eq!(worker_lines(&marker).len(),1,"loser cannot signal/adopt saved PID");
    assert!(worker_alive(pid.try_into().unwrap(),children[0]["start_token"].as_str().unwrap()),"rejected PID/loser stop must leave the worker alive");
    let resumed=owner.send(json!({"op":"local_resume","job_id":"contended-job","launch_id":"contended-launch"}));
    assert_eq!(resumed["ok"],true);assert_eq!(resumed["result"]["local_state"],"owned_child_unobserved");
    assert_eq!(resumed["result"]["stop"]["launch_id"],"contended-launch");assert_eq!(resumed["result"]["stop"]["stop_id"],"shared-stop");
    assert!(serde_json::to_vec(&resumed["result"]).unwrap().len()<=4096);
    let replay_stop=json!({"op":"local_stop","job_id":"contended-job","launch_id":resumed["result"]["stop"]["launch_id"],"stop_id":resumed["result"]["stop"]["stop_id"]});
    let owner_stop=owner.send(replay_stop);assert_eq!(owner_stop["ok"],true);assert_eq!(owner_stop["result"]["state"],"exit_observed");assert_eq!(owner_stop["result"]["replayed"],true);
    let after_stop=events(&db,"contended-job");assert_eq!(after_stop.iter().filter(|e|e["kind"]=="LOCAL_STOP_REQUESTED").count(),1);assert_eq!(after_stop.iter().filter(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").count(),1);assert_eq!(remaining(&db),50);
    let finalized=owner.send(premature.clone());assert_eq!(finalized["ok"],true);assert_eq!(remaining(&db),0);
    records.push(json!({"phase":"loser-cannot-signal-or-finalize-before-exit","request_pid":caller_pid,"pid_rejection":rejected,"premature_finalize":before_exit,"unknown_stop":unknown_reply,"owner_resume_with_stop_selector":resumed,"owner_stop":owner_stop,"finalize":finalized,"events":events(&db,"contended-job"),"remaining_after_exit":50,"remaining_after_finalize":remaining(&db)}));
    let connection=rusqlite::Connection::open(&db).unwrap();
    connection.execute("UPDATE events SET payload=?1 WHERE id=?2",rusqlite::params![r#"{"launch_id":"contended-launch","stop_id":"shared-stop","unexpected":true}"#,"local-stop:contended-job"]).unwrap();
    drop(connection);
    let malformed_resume=owner.send(json!({"op":"local_resume","job_id":"contended-job","launch_id":"contended-launch"}));
    assert_eq!(malformed_resume["ok"],false,"unknown retained stop payload fields must fail closed");
    assert!(malformed_resume["error"].as_str().unwrap().contains("unsupported"));
    records.push(json!({"phase":"malformed-stop-payload-fails-closed","response":malformed_resume}));
    persist("contention-history.json",json!({"source_sha256":source_hashes(),"records":records,"worker":children[0]}));
}

#[test]
fn lost_hot_gateway_reply_replay_observes_one_child_without_redispatch(){
    let dir=tempfile::tempdir().unwrap();let(db,revision)=setup(dir.path(),"lost-reply-job");let marker=dir.path().join("lost-children.jsonl");let release=dir.path().join("lost-release");let _release=Release(release.clone());let trusted=profile(&marker,&release);let gateway=Gateway::start(dir.path(),"gateway-lost-reply",&db,&trusted);
    let request=json!({"op":"local_launch","job_id":"lost-reply-job","launch_id":"lost-reply-launch","expected_catalog":revision});
    let mut stream=UnixStream::connect(&gateway.socket).unwrap();stream.write_all(serde_json::to_string(&request).unwrap().as_bytes()).unwrap();stream.shutdown(std::net::Shutdown::Write).unwrap();drop(stream);
    wait_for(&marker);let until=Instant::now()+Duration::from_secs(10);while Instant::now()<until{if events(&db,"lost-reply-job").iter().any(|e|e["kind"]=="LAUNCH_STARTED_OBSERVED"){break}thread::sleep(Duration::from_millis(10));}
    let first_events=events(&db,"lost-reply-job");assert!(first_events.iter().any(|e|e["kind"]=="LAUNCH_STARTED_OBSERVED"));assert_eq!(worker_lines(&marker).len(),1);
    let replay= gateway.send(request.clone());assert_eq!(replay["ok"],true);assert_eq!(replay["result"]["state"],"running");assert_eq!(worker_lines(&marker).len(),1,"lost reply replay cannot redispatch");
    let stop=json!({"op":"local_stop","job_id":"lost-reply-job","launch_id":"lost-reply-launch","stop_id":"lost-reply-stop"});let stopped=gateway.send(stop.clone());assert_eq!(stopped["ok"],true);let finalize=json!({"op":"local_finalize","job_id":"lost-reply-job","launch_id":"lost-reply-launch","outcome":"cancelled"});let closed=gateway.send(finalize.clone());assert_eq!(closed["ok"],true);
    persist("lost-reply-history.json",json!({"source_sha256":source_hashes(),"lost_reply_request":request,"durable_events_before_replay":first_events,"replay":replay,"stop":stopped,"finalize":closed,"worker_count":worker_lines(&marker).len()}));
}
