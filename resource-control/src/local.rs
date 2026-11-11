//! Optional, profile-bound local process supervisor used only by the trusted gateway.
use crate::{BeginLaunchResult, LaunchDispatch, LaunchExitObservation, LaunchObservation,
    ProcessExitStatus, ProcessIdentity, RecordLaunchExitResult, RecordLaunchObservationResult,
    Result, Store, Error};
use rusqlite::{params, OptionalExtension, TransactionBehavior};
use sha2::{Digest, Sha256};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::os::unix::process::ExitStatusExt;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::os::unix::process::CommandExt;

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LocalProfile {
    pub program: PathBuf,
    pub args: Vec<String>,
    pub cwd: PathBuf,
    pub env: std::collections::BTreeMap<String, String>,
    pub account_id: String,
    pub project_id: String,
    pub environment_id: String,
}
impl LocalProfile {
    pub fn validate(&self) -> Result<()> {
        if !self.program.is_absolute() || !self.cwd.is_absolute() {
            return Err(Error::Invalid("local profile program and cwd must be absolute".into()));
        }
        if self.args.len() > 128 || self.args.iter().any(|v| v.len() > 4096) ||
            self.env.len() > 128 || self.env.iter().any(|(k,v)| k.is_empty() || k.contains('=') || k.as_bytes().contains(&0) || v.as_bytes().contains(&0) || k.len()+v.len()>8192) {
            return Err(Error::Invalid("local profile arguments or environment exceed bounds".into()));
        }
        if self.args.iter().any(|v|v.as_bytes().contains(&0)) {
            return Err(Error::Invalid("local profile argument contains NUL".into()));
        }
        for (value, label) in [(&self.account_id,"account"),(&self.project_id,"project"),(&self.environment_id,"environment")] {
            if value.is_empty() || value.len()>160 { return Err(Error::Invalid(format!("local profile {label} is invalid"))); }
        }
        Ok(())
    }
}

#[derive(Debug)]
struct OwnedChild { child: Child, process: Option<ProcessIdentity>, started_recorded: bool, exited: Option<ProcessExitStatus> }
#[derive(Default)]
pub struct LocalSupervisor { children: HashMap<(String,String),OwnedChild> }

fn process_identity(pid:u32)->Result<ProcessIdentity>{
    let raw=std::fs::read_to_string(format!("/proc/{pid}/stat"))?;
    let close=raw.rfind(')').ok_or_else(||Error::Invalid("cannot parse child process identity".into()))?;
    let fields:Vec<&str>=raw[close+1..].split_whitespace().collect();
    // /proc stat field 22 (starttime); after comm, fields begins at field 3.
    let start=fields.get(19).ok_or_else(||Error::Invalid("child process start token missing".into()))?;
    Ok(ProcessIdentity{pid,start_token:(*start).into()})
}
fn exit_status(status:std::process::ExitStatus)->Result<ProcessExitStatus>{
    if let Some(code)=status.code(){Ok(ProcessExitStatus::Code{code})}
    else if let Some(signal)=status.signal(){Ok(ProcessExitStatus::Signal{signal})}
    else {Err(Error::Invalid("child wait returned no code or signal".into()))}
}
fn validate_launch(store:&Store,job:&str,launch:&str)->Result<Value>{
    let value=store.job(job)?;
    if value.get("launch_id").and_then(Value::as_str)!=Some(launch) {
        return Err(Error::Conflict("local operation launch selector does not match stored job".into()));
    }
    let view=store.resume_view(job)?;
    if view.profile!=crate::ResumeLaunchProfile::Intent || view.launch_id.as_deref()!=Some(launch) {
        return Err(Error::Conflict("local operation requires matching native launch intent".into()));
    }
    Ok(value)
}
fn validate_profile_scope(profile:&LocalProfile,job:&Value)->Result<()> {
    let proposal=job.get("proposal").ok_or_else(||Error::Invalid("job proposal missing".into()))?;
    if proposal.get("account_id").and_then(Value::as_str)!=Some(profile.account_id.as_str()) ||
       proposal.get("project_id").and_then(Value::as_str)!=Some(profile.project_id.as_str()) ||
       proposal.get("environment_id").and_then(Value::as_str)!=Some(profile.environment_id.as_str()) {
        return Err(Error::Conflict("job scope does not match trusted local profile".into()));
    }
    Ok(())
}
impl LocalSupervisor {
    pub fn launch(&mut self,store:&mut Store,profile:&LocalProfile,job:&str,launch:&str,expected_catalog:i64,at:i64)->Result<Value>{
        profile.validate()?;
        let before=store.job(job)?;
        validate_profile_scope(profile,&before)?;
        match store.begin_launch(job,launch,expected_catalog,at)? {
            BeginLaunchResult::DispatchGranted(grant)=>{
                if grant.job_id()!=job || grant.launch_id()!=launch {return Err(Error::Conflict("dispatch grant identity mismatch".into()));}
                self.spawn(store,profile,grant,at)
            }
            BeginLaunchResult::PendingObservation{..}|BeginLaunchResult::RunningObservation{..}=>{
                // Replays are observations only. A retained child may have exited
                // since the previous request, so refresh through the exact Child.
                self.poll(store,job,launch,at)
            }
        }
    }
    fn spawn(&mut self,store:&mut Store,profile:&LocalProfile,grant:LaunchDispatch,at:i64)->Result<Value>{
        let job=grant.job_id().to_string(); let launch=grant.launch_id().to_string();
        let mut command=Command::new(&profile.program);
        command.args(&profile.args).current_dir(&profile.cwd).env_clear().envs(&profile.env)
            .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null());
        // Set a hard CPU ceiling and disable core dumps for this fixed local worker.
        unsafe { command.pre_exec(|| {
            let cpu=libc::rlimit{rlim_cur:5,rlim_max:5};
            if libc::setrlimit(libc::RLIMIT_CPU,&cpu)!=0 {return Err(std::io::Error::last_os_error());}
            let memory=libc::rlimit{rlim_cur:256*1024*1024,rlim_max:256*1024*1024};
            if libc::setrlimit(libc::RLIMIT_AS,&memory)!=0 {return Err(std::io::Error::last_os_error());}
            let files=libc::rlimit{rlim_cur:64,rlim_max:64};
            if libc::setrlimit(libc::RLIMIT_NOFILE,&files)!=0 {return Err(std::io::Error::last_os_error());}
            let core=libc::rlimit{rlim_cur:0,rlim_max:0};
            if libc::setrlimit(libc::RLIMIT_CORE,&core)!=0 {return Err(std::io::Error::last_os_error());}
            if libc::prctl(libc::PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0 {return Err(std::io::Error::last_os_error());}
            Ok(())
        }); }
        match command.spawn(){
            Ok(child)=>{
                let pid=child.id();
                let process=process_identity(pid).ok();
                self.children.insert((job.clone(),launch.clone()),OwnedChild{child,process:process.clone(),started_recorded:false,exited:None});
                if let Some(process)=process {
                    store.observe_launch(&job,&launch,&LaunchObservation::Started{process},at)?;
                    if let Some(owned)=self.children.get_mut(&(job.clone(),launch.clone())){owned.started_recorded=true;}
                    Ok(json!({"state":"running","job_id":job,"launch_id":launch}))
                } else {
                    Ok(json!({"state":"unknown","job_id":job,"launch_id":launch}))
                }
            }
            Err(error)=>{
                // After durable intent, a spawn error can be ambiguous (for
                // example, the child may have been created before an I/O error).
                // Preserve unknown liveness and held capacity; never infer absence.
                Err(Error::Io(error))
            }
        }
    }
    pub fn poll(&mut self,store:&mut Store,job:&str,launch:&str,at:i64)->Result<Value>{
        validate_launch(store,job,launch)?;
        let key=(job.to_string(),launch.to_string());
        let Some(owned)=self.children.get_mut(&key) else{return Ok(json!({"state":"unknown","job_id":job,"launch_id":launch,"exit":null}))};
        if owned.process.is_none(){owned.process=process_identity(owned.child.id()).ok();}
        if !owned.started_recorded { if let Some(process)=owned.process.clone(){store.observe_launch(job,launch,&LaunchObservation::Started{process},at)?;owned.started_recorded=true;} }
        if let Some(status)=owned.child.try_wait()? {
            let status=exit_status(status)?;
            owned.exited=Some(status.clone());
        }
        if let (Some(process),Some(status))=(&owned.process,&owned.exited){
            let observation=LaunchExitObservation{process:process.clone(),status:status.clone()};
            store.observe_launch_exit(job,launch,&observation,at)?;
            Ok(json!({"state":"exit_observed","job_id":job,"launch_id":launch,"exit":status_json(status)}))
        } else {
            Ok(json!({"state":"running","job_id":job,"launch_id":launch,"exit":null}))
        }
    }
    pub fn stop(&mut self,store:&mut Store,job:&str,launch:&str,stop_id:&str,at:i64)->Result<Value>{
        validate_launch(store,job,launch)?;
        let replay=store.record_local_stop(job,launch,stop_id,at)?;
        let key=(job.to_string(),launch.to_string());
        let Some(owned)=self.children.get_mut(&key) else{return Ok(json!({"state":"unknown","job_id":job,"launch_id":launch,"stop_id":stop_id,"replayed":replay}))};
        if owned.process.is_none(){owned.process=process_identity(owned.child.id()).ok();}
        if !owned.started_recorded { if let Some(process)=owned.process.clone(){store.observe_launch(job,launch,&LaunchObservation::Started{process},at)?;owned.started_recorded=true;} }
        if owned.exited.is_none(){
            match owned.child.try_wait()? {
                Some(status)=>owned.exited=Some(exit_status(status)?),
                None=>{owned.child.kill()?;owned.exited=Some(exit_status(owned.child.wait()?)?);}
            }
        }
        if let (Some(process),Some(status))=(&owned.process,&owned.exited){
            store.observe_launch_exit(job,launch,&LaunchExitObservation{process:process.clone(),status:status.clone()},at)?;
            Ok(json!({"state":"exit_observed","job_id":job,"launch_id":launch,"stop_id":stop_id,"replayed":replay,"exit":status_json(status)}))
        } else { Ok(json!({"state":"unknown","job_id":job,"launch_id":launch,"stop_id":stop_id,"replayed":replay}) ) }
    }
    pub fn resume(&self,store:&Store,job:&str,launch:&str)->Result<Value>{
        validate_launch(store,job,launch)?;
        let view=store.resume_view(job)?;
        let key=(job.to_string(),launch.to_string());
        let local_state=if let Some(owned)=self.children.get(&key){if owned.exited.is_some(){"exit_observed"}else{"owned_child_unobserved"}}else{"unknown"};
        let stop_row:Option<(String,i64,String)>=store.db.query_row(
            "SELECT id,at,payload FROM events WHERE id=?1 AND job_id=?2 AND kind='LOCAL_STOP_REQUESTED'",
            params![format!("local-stop:{job}"),job],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
        let stop=stop_row.map(|(event_id,recorded_at,payload)|json!({
            "event_id":event_id,"kind":"LOCAL_STOP_REQUESTED","recorded_at":recorded_at,
            "payload_sha256":format!("{:x}",Sha256::digest(payload.as_bytes()))
        }));
        let result=json!({"resume_view":view,"local_state":local_state,"stop":stop});
        if serde_json::to_vec(&result)?.len()>4096 {return Err(Error::Conflict("local resume result exceeds 4 KiB bound".into()));}
        Ok(result)
    }
    pub fn finalize(&mut self,store:&mut Store,job:&str,launch:&str,outcome:&str,at:i64)->Result<Value>{
        validate_launch(store,job,launch)?;
        // The existing finalizer itself requires exact process exit evidence.
        let result=store.finalize(job,outcome,at)?;
        self.children.remove(&(job.to_string(),launch.to_string()));
        Ok(json!({"finalization":result,"job_id":job,"launch_id":launch,"outcome":outcome}))
    }
}
fn status_json(status:&ProcessExitStatus)->Value{match status{ProcessExitStatus::Code{code}=>json!({"code":code}),ProcessExitStatus::Signal{signal}=>json!({"signal":signal})}}

impl Store {
    /// Persist one bounded stop request in the existing lifecycle event owner.
    pub fn record_local_stop(&mut self,job:&str,launch:&str,stop_id:&str,at:i64)->Result<bool>{
        super::check_id(job,"job")?;super::check_id(launch,"launch")?;super::check_id(stop_id,"stop")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let row:Option<(String,Option<String>)>=tx.query_row("SELECT state,launch_id FROM jobs WHERE id=?1",[job],|r|Ok((r.get(0)?,r.get(1)?))).optional()?;
        let (state,stored_launch)=row.ok_or_else(||Error::Invalid("unknown job".into()))?;
        if stored_launch.as_deref()!=Some(launch) || !Self::has_launch_intent(&tx,job,launch)? {
            return Err(Error::Conflict("stop request does not match native launch intent".into()));
        }
        let id=format!("local-stop:{job}");
        let prior:Option<(String,String)>=tx.query_row("SELECT kind,payload FROM events WHERE id=?1",[&id],|r|Ok((r.get(0)?,r.get(1)?))).optional()?;
        let payload=json!({"launch_id":launch,"stop_id":stop_id});
        if let Some((kind,raw))=prior{
            if kind=="LOCAL_STOP_REQUESTED" && serde_json::from_str::<Value>(&raw)?==payload {
                tx.commit()?;return Ok(true);
            }
            return Err(Error::Conflict("stop request conflicts with prior stop selector".into()));
        }
        if !matches!(state.as_str(),"LAUNCHING"|"RUNNING") {return Err(Error::Conflict(format!("stop forbidden from state {state}")));}
        Self::log(&tx,&id,Some(job),"LOCAL_STOP_REQUESTED",at,payload)?;
        tx.commit()?;Ok(false)
    }
}
