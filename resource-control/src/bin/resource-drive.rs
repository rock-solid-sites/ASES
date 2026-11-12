//! Bounded drive over the fixed sibling resource-session client.
use serde_json::{json, Value};
use std::io::Read;
use std::path::Path;
use std::process::{Command, Stdio};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

const MAX_SOCKET_BYTES: usize = 107;
const MAX_CLIENT_STDOUT: usize = 8 * 1024 + 1;
const MAX_CLIENT_STDERR: usize = 4 * 1024;
const CLIENT_CALL_BOUND: Duration = Duration::from_secs(8);
const POLL_INTERVAL: Duration = Duration::from_millis(100);

struct Args {
    socket: String,
    job: String,
    launch: String,
    revision: i64,
    outcome: String,
    budget: Duration,
}
struct CancelArgs {
    socket: String,
    job: String,
    launch: String,
    stop_id: String,
    grace_ms: u64,
}
struct ClientResult {
    status: Option<i32>,
    reply: Option<Value>,
    failure: Option<&'static str>,
}
struct Capture {
    bytes: Vec<u8>,
    overflow: bool,
    failed: bool,
}
enum DriveError {
    Recovery {
        reason: &'static str,
        last_action: &'static str,
        poll_count: u32,
        client_status: Option<i32>,
        client_reply: Option<Value>,
        launch_response: Option<Value>,
        exit_observation: Option<Value>,
    },
}

fn valid_id(value: &str) -> bool {
    !value.is_empty() && value.len() <= 160 &&
        value.bytes().all(|b| b.is_ascii_alphanumeric() || b"-_.:/".contains(&b))
}
fn parse_args(args: Vec<String>) -> Result<Args, String> {
    if args.len() != 6 {
        return Err("usage: resource-drive SOCKET JOB LAUNCH EXPECTED_CATALOG OUTCOME BUDGET_MS".into());
    }
    let socket = &args[0];
    let path = Path::new(socket);
    if !path.is_absolute() || socket.as_bytes().is_empty() || socket.as_bytes().len() > MAX_SOCKET_BYTES || socket.as_bytes().contains(&0) {
        return Err("SOCKET must be an absolute Unix socket path shorter than 108 bytes".into());
    }
    if !valid_id(&args[1]) || !valid_id(&args[2]) {
        return Err("JOB and LAUNCH must be valid resource identifiers".into());
    }
    let revision = args[3].parse::<i64>().map_err(|_| "EXPECTED_CATALOG must be a nonnegative integer")?;
    if revision < 0 { return Err("EXPECTED_CATALOG must be a nonnegative integer".into()); }
    if !["completed", "failed", "cancelled", "interrupted"].contains(&args[4].as_str()) {
        return Err("OUTCOME must be completed, failed, cancelled, or interrupted".into());
    }
    let budget_ms = args[5].parse::<u64>().map_err(|_| "BUDGET_MS must be an integer from 100 through 10000")?;
    if !(100..=10_000).contains(&budget_ms) { return Err("BUDGET_MS must be an integer from 100 through 10000".into()); }
    Ok(Args { socket:socket.clone(),job:args[1].clone(),launch:args[2].clone(),revision,
        outcome:args[4].clone(),budget:Duration::from_millis(budget_ms) })
}
fn parse_cancel_args(args: Vec<String>) -> Result<CancelArgs, String> {
    if args.len() != 5 {
        return Err("usage: resource-drive cancel SOCKET JOB LAUNCH STOP_ID GRACE_MS".into());
    }
    let socket=&args[0];
    let path=Path::new(socket);
    if !path.is_absolute()||socket.as_bytes().is_empty()||socket.as_bytes().len()>MAX_SOCKET_BYTES||socket.as_bytes().contains(&0){
        return Err("SOCKET must be an absolute Unix socket path shorter than 108 bytes".into());
    }
    if !valid_id(&args[1])||!valid_id(&args[2])||!valid_id(&args[3]){
        return Err("JOB, LAUNCH, and STOP_ID must be valid resource identifiers".into());
    }
    let grace_ms=args[4].parse::<u64>().map_err(|_|"GRACE_MS must be an integer from 1 through 2000")?;
    if !(1..=2000).contains(&grace_ms){return Err("GRACE_MS must be an integer from 1 through 2000".into());}
    Ok(CancelArgs{socket:socket.clone(),job:args[1].clone(),launch:args[2].clone(),stop_id:args[3].clone(),grace_ms})
}
fn read_capped<R: Read>(reader: R, max: usize) -> Capture {
    let mut reader=reader.take(max as u64+1);
    let mut bytes=Vec::with_capacity(max.min(4096));
    let failed=reader.read_to_end(&mut bytes).is_err();
    let overflow=bytes.len()>max;
    Capture{bytes,overflow,failed}
}
fn join_capture(thread:JoinHandle<Capture>)->Capture {
    thread.join().unwrap_or(Capture{bytes:Vec::new(),overflow:false,failed:true})
}
fn parse_reply(capture:&Capture)->Option<Value>{
    if capture.overflow||capture.failed{return None;}
    serde_json::from_slice(&capture.bytes).ok()
}
fn reply_success_shape(reply:&Value)->bool {
    reply.is_object() && reply.get("ok")==Some(&Value::Bool(true)) && reply.get("result").is_some_and(Value::is_object)
}
fn reply_server_error_shape(reply:&Value)->bool {
    reply.is_object() && reply.get("ok")==Some(&Value::Bool(false)) && reply.get("error").is_some_and(Value::is_string)
}
fn reply_unknown_shape(reply:&Value)->bool {
    reply_server_error_shape(reply) && reply.get("outcome")==Some(&Value::String("outcome_unknown".into()))
}
fn invoke_client(client:&Path,args:&[String])->ClientResult {
    let mut child=match Command::new(client).args(args).env_clear().stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped()).spawn(){
        Ok(child)=>child,
        Err(_)=>return ClientResult{status:None,reply:None,failure:Some("client_unavailable")},
    };
    let Some(stdout)=child.stdout.take() else {let _=child.kill();let _=child.wait();return ClientResult{status:None,reply:None,failure:Some("unsupported_reply")};};
    let Some(stderr)=child.stderr.take() else {let _=child.kill();let _=child.wait();return ClientResult{status:None,reply:None,failure:Some("unsupported_reply")};};
    let stdout_reader=thread::spawn(move||read_capped(stdout,MAX_CLIENT_STDOUT));
    let stderr_reader=thread::spawn(move||read_capped(stderr,MAX_CLIENT_STDERR));
    let deadline=Instant::now()+CLIENT_CALL_BOUND;
    let mut timed_out=false;
    let status=loop {
        match child.try_wait(){
            Ok(Some(status))=>break Some(status),
            Ok(None)=>(),
            Err(_)=>{let _=child.kill();break child.wait().ok();}
        }
        if Instant::now()>=deadline {timed_out=true;let _=child.kill();break child.wait().ok();}
        thread::sleep(Duration::from_millis(5));
    };
    let out=join_capture(stdout_reader);let err=join_capture(stderr_reader);
    let code=status.as_ref().and_then(std::process::ExitStatus::code);
    if timed_out || out.overflow || err.overflow || out.failed || err.failed {
        return ClientResult{status:code,reply:parse_reply(&out),failure:Some(if timed_out{"client_call_timeout"}else{"unsupported_reply"})};
    }
    let Some(reply)=parse_reply(&out) else{return ClientResult{status:code,reply:None,failure:Some("unsupported_reply")};};
    let failure=match code {
        Some(0) if reply_success_shape(&reply)=>None,
        Some(3) if reply_server_error_shape(&reply)=>Some("server_error"),
        Some(4) if reply_unknown_shape(&reply)=>Some("client_outcome_unknown"),
        _=>Some("unsupported_reply"),
    };
    ClientResult{status:code,reply:Some(reply),failure}
}
fn result<'a>(reply:&'a Value,job:&str,launch:&str)->Option<&'a Value>{
    let r=reply.get("result")?;
    if r.get("job_id").and_then(Value::as_str)!=Some(job)||r.get("launch_id").and_then(Value::as_str)!=Some(launch){return None;}
    Some(r)
}
fn valid_exit(value:&Value)->bool{
    let Some(object)=value.as_object()else{return false};
    if object.len()!=1{return false;}
    object.get("code").and_then(Value::as_i64).is_some_and(|code|(0..=255).contains(&code))||
        object.get("signal").and_then(Value::as_i64).is_some_and(|sig|(1..=64).contains(&sig))
}
fn action_state(reply:&Value,job:&str,launch:&str,action:&str)->Option<&'static str>{
    let r=result(reply,job,launch)?;
    let state=r.get("state")?.as_str()?;
    match (action,state){
        ("launch","running")|("poll","running") if r.get("exit").is_none_or(Value::is_null)=>Some("running"),
        ("launch","unknown")|("poll","unknown") if r.get("exit").is_none_or(Value::is_null)=>Some("unknown"),
        ("launch","exit_observed")|("poll","exit_observed") if r.get("exit").is_some_and(valid_exit)=>Some("exit_observed"),
        _=>None,
    }
}
fn recovery(args:&Args,error:DriveError)->(Value,i32){
    match error {
        DriveError::Recovery{reason,last_action,poll_count,client_status,client_reply,launch_response,exit_observation}=>(json!({
            "ok":false,"outcome":"recovery_needed","reason":reason,"job_id":args.job,"launch_id":args.launch,
            "selected_outcome":args.outcome,"last_action":last_action,"poll_count":poll_count,
            "client_status":client_status,"client_reply":client_reply,
            "launch_response":launch_response,"exit_observation":exit_observation
        }),3),
    }
}
fn recovery_for(args:&Args,reason:&'static str,last_action:&'static str,poll_count:u32,client:Option<ClientResult>,launch_response:Option<Value>,exit_observation:Option<Value>)->(Value,i32){
    let (status,reply)=client.map(|c|(c.status,c.reply)).unwrap_or((None,None));
    recovery(args,DriveError::Recovery{reason,last_action,poll_count,client_status:status,client_reply:reply,launch_response,exit_observation})
}
fn run_client_action(args:&Args,action:&str)->Vec<String>{
    let mut argv=vec![args.socket.clone(),action.into(),args.job.clone(),args.launch.clone()];
    match action{"launch"=>argv.push(args.revision.to_string()),"finalize"=>argv.push(args.outcome.clone()),_=>()}
    argv
}
fn cancel_client_action(args:&CancelArgs,action:&str)->Vec<String>{
    let mut argv=vec![args.socket.clone(),action.into(),args.job.clone(),args.launch.clone()];
    match action{
        "stop-graceful"=>{argv.push(args.stop_id.clone());argv.push(args.grace_ms.to_string());},
        "finalize"=>argv.push("cancelled".into()),
        _=>(),
    }
    argv
}
fn cancel_result<'a>(reply:&'a Value,args:&CancelArgs)->Option<&'a Value>{
    let r=result(reply,&args.job,&args.launch)?;
    if r.get("stop_id").and_then(Value::as_str)!=Some(args.stop_id.as_str())||
       r.get("mode").and_then(Value::as_str)!=Some("term_then_kill")||
       r.get("grace_ms").and_then(Value::as_u64)!=Some(args.grace_ms)||
       !r.get("replayed").is_some_and(Value::is_boolean){return None;}
    Some(r)
}
fn cancel_recovery(args:&CancelArgs,phase:&'static str,reason:&'static str,client:Option<ClientResult>,
    stop_response:Option<Value>,exit_observation:Option<Value>,finalization:Option<Value>)->(Value,i32){
    let (client_status,client_reply)=client.map(|c|(c.status,c.reply)).unwrap_or((None,None));
    (json!({"ok":false,"outcome":"recovery_needed","reason":reason,"action":"cancel",
        "phase":phase,"last_action":phase,"selected_outcome":"cancelled","job_id":args.job,"launch_id":args.launch,
        "stop_id":args.stop_id,"mode":"term_then_kill","grace_ms":args.grace_ms,
        "client_status":client_status,"client_reply":client_reply,"stop_response":stop_response,
        "exit_observation":exit_observation,"finalization":finalization}),3)
}
fn cancel_drive(args:CancelArgs)->(Value,i32){
    let executable=match std::env::current_exe(){Ok(p)=>p,Err(_)=>return cancel_recovery(&args,"stop-graceful","client_unavailable",None,None,None,None)};
    let Some(parent)=executable.parent().filter(|p|p.is_absolute())else{return cancel_recovery(&args,"stop-graceful","client_unavailable",None,None,None,None)};
    let client=parent.join("resource-session");

    // The 8-second child-call bound limits this driver's wait. It is not a hard
    // wall quiescence guarantee: the gateway may still be handling a stop when
    // a client timeout or lost response forces recovery.
    let stop_call=invoke_client(&client,&cancel_client_action(&args,"stop-graceful"));
    if let Some(reason)=stop_call.failure{
        let response=stop_call.reply.clone();
        return cancel_recovery(&args,"stop-graceful",reason,Some(stop_call),response,None,None);
    }
    let stop_response=stop_call.reply.unwrap();
    let Some(stop)=cancel_result(&stop_response,&args)else{
        return cancel_recovery(&args,"stop-graceful","unsupported_reply",
            Some(ClientResult{status:Some(0),reply:Some(stop_response.clone()),failure:None}),Some(stop_response),None,None);
    };
    let state=stop.get("state").and_then(Value::as_str);
    if state==Some("unknown"){
        if stop.get("exit").is_some_and(|value|!value.is_null()){
            return cancel_recovery(&args,"stop-graceful","unsupported_reply",
                Some(ClientResult{status:Some(0),reply:Some(stop_response.clone()),failure:None}),Some(stop_response),None,None);
        }
        return cancel_recovery(&args,"stop-graceful","unknown_custody",
            Some(ClientResult{status:Some(0),reply:Some(stop_response.clone()),failure:None}),Some(stop_response),None,None);
    }
    if state!=Some("exit_observed")||!stop.get("exit").is_some_and(valid_exit){
        return cancel_recovery(&args,"stop-graceful","unsupported_reply",
            Some(ClientResult{status:Some(0),reply:Some(stop_response.clone()),failure:None}),Some(stop_response),None,None);
    }
    let exit_observation=stop_response.clone();

    // This is the sole finalization attempt. A lost or malformed reply leaves
    // the durable job state unknown to this driver; it must not retry.
    let finalize_call=invoke_client(&client,&cancel_client_action(&args,"finalize"));
    if let Some(reason)=finalize_call.failure{
        let response=finalize_call.reply.clone();
        return cancel_recovery(&args,"finalize",reason,Some(finalize_call),Some(stop_response),Some(exit_observation),response);
    }
    let final_reply=finalize_call.reply.unwrap();
    let Some(final_result)=result(&final_reply,&args.job,&args.launch)else{
        return cancel_recovery(&args,"finalize","unsupported_reply",
            Some(ClientResult{status:Some(0),reply:Some(final_reply.clone()),failure:None}),Some(stop_response),Some(exit_observation),Some(final_reply));
    };
    if final_result.get("finalization").and_then(Value::as_str).is_none_or(|s|!matches!(s,"CLOSED"|"CLOSED_REPLAY"))||
       final_result.get("outcome").and_then(Value::as_str)!=Some("cancelled"){
        return cancel_recovery(&args,"finalize","unsupported_reply",
            Some(ClientResult{status:Some(0),reply:Some(final_reply.clone()),failure:None}),Some(stop_response),Some(exit_observation),Some(final_reply));
    }
    (json!({"ok":true,"outcome":"finalized","action":"cancel","selected_outcome":"cancelled",
        "job_id":args.job,"launch_id":args.launch,"stop_id":args.stop_id,"mode":"term_then_kill",
        "grace_ms":args.grace_ms,"stop_client_status":0,"stop_response":stop_response,
        "exit_observation":exit_observation,"finalize_client_status":0,"finalization":final_reply}),0)
}
fn drive(args:Args)->(Value,i32){
    let executable=match std::env::current_exe(){Ok(p)=>p,Err(_)=>return recovery_for(&args,"client_unavailable","launch",0,None,None,None)};
    let Some(parent)=executable.parent().filter(|p|p.is_absolute())else{return recovery_for(&args,"client_unavailable","launch",0,None,None,None)};
    let client=parent.join("resource-session");
    let launch_call=invoke_client(&client,&run_client_action(&args,"launch"));
    if let Some(reason)=launch_call.failure{return recovery_for(&args,reason,"launch",0,Some(launch_call),None,None);}
    let launch_response=launch_call.reply.unwrap();
    let Some(state)=action_state(&launch_response,&args.job,&args.launch,"launch")else{return recovery_for(&args,"unsupported_reply","launch",0,Some(ClientResult{status:Some(0),reply:Some(launch_response),failure:None}),None,None)};
    if state=="unknown"{return recovery_for(&args,"unknown_custody","launch",0,Some(ClientResult{status:Some(0),reply:Some(launch_response.clone()),failure:None}),Some(launch_response),None);}
    let mut poll_count=0u32;
    let mut last_poll:Option<(i32,Value)>=None;
    let exit_observation=if state=="exit_observed"{Some(launch_response.clone())}else{
        let deadline=Instant::now()+args.budget;
        loop {
            if Instant::now()>=deadline{
                let last=last_poll.take().map(|(status,reply)|ClientResult{status:Some(status),reply:Some(reply),failure:None});
                return recovery_for(&args,"budget_exhausted","poll",poll_count,last,Some(launch_response),None);
            }
            let poll_call=invoke_client(&client,&run_client_action(&args,"poll"));
            poll_count=poll_count.saturating_add(1);
            if let Some(reason)=poll_call.failure{return recovery_for(&args,reason,"poll",poll_count,Some(poll_call),Some(launch_response),None);}
            let poll_reply=poll_call.reply.unwrap();
            last_poll=Some((0,poll_reply.clone()));
            let Some(state)=action_state(&poll_reply,&args.job,&args.launch,"poll")else{return recovery_for(&args,"unsupported_reply","poll",poll_count,Some(ClientResult{status:Some(0),reply:Some(poll_reply),failure:None}),Some(launch_response),None)};
            if state=="unknown"{return recovery_for(&args,"unknown_custody","poll",poll_count,Some(ClientResult{status:Some(0),reply:Some(poll_reply),failure:None}),Some(launch_response),None);}
            if state=="exit_observed"{break Some(poll_reply);}
            if Instant::now()>=deadline{return recovery_for(&args,"budget_exhausted","poll",poll_count,Some(ClientResult{status:Some(0),reply:Some(poll_reply),failure:None}),Some(launch_response),None);}
            thread::sleep(POLL_INTERVAL.min(deadline.saturating_duration_since(Instant::now())));
        }
    };
    let exit_observation=exit_observation.unwrap();
    let finalize_call=invoke_client(&client,&run_client_action(&args,"finalize"));
    if let Some(reason)=finalize_call.failure{return recovery_for(&args,reason,"finalize",poll_count,Some(finalize_call),Some(launch_response),Some(exit_observation));}
    let final_reply=finalize_call.reply.unwrap();
    let Some(final_result)=result(&final_reply,&args.job,&args.launch)else{return recovery_for(&args,"unsupported_reply","finalize",poll_count,Some(ClientResult{status:Some(0),reply:Some(final_reply),failure:None}),Some(launch_response),Some(exit_observation));};
    if final_result.get("finalization").and_then(Value::as_str).is_none_or(|s|!matches!(s,"CLOSED"|"CLOSED_REPLAY"))||
       final_result.get("outcome").and_then(Value::as_str)!=Some(args.outcome.as_str()) {
        return recovery_for(&args,"unsupported_reply","finalize",poll_count,Some(ClientResult{status:Some(0),reply:Some(final_reply),failure:None}),Some(launch_response),Some(exit_observation));
    }
    let output=json!({"ok":true,"outcome":"finalized","job_id":args.job,"launch_id":args.launch,
        "selected_outcome":args.outcome,"poll_count":poll_count,
        "launch_client_status":0,"launch_response":launch_response,
        "exit_client_status":0,"exit_observation":exit_observation,
        "finalize_client_status":0,"finalization":final_reply});
    (output,0)
}
fn main(){
    let parsed:Result<Vec<String>,_>=std::env::args_os().skip(1).map(|v|v.into_string().map_err(|_|())).collect();
    let (output,status)=match parsed.map_err(|_|"arguments must be valid UTF-8".to_string()){
        Err(message)=>(json!({"ok":false,"outcome":"invalid_input","error":message}),2),
        Ok(mut args) if args.first().is_some_and(|mode|mode=="cancel")=>{
            args.remove(0);
            match parse_cancel_args(args){Ok(args)=>cancel_drive(args),Err(message)=>(json!({"ok":false,"outcome":"invalid_input","error":message}),2)}
        }
        Ok(args)=>match parse_args(args){Ok(args)=>drive(args),Err(message)=>(json!({"ok":false,"outcome":"invalid_input","error":message}),2)},
    };
    println!("{}",serde_json::to_string(&output).unwrap_or_else(|_|"{\"ok\":false,\"outcome\":\"recovery_needed\",\"reason\":\"unsupported_reply\"}".into()));
    std::process::exit(status);
}
