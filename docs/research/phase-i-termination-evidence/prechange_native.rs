//! Fixed-child comparator compiled against immutable pre-termination source.
use ases_resource_control::{now, BeginLaunchResult, Claim, Environment, LaunchObservation,
    Meter, ProcessIdentity, Proposal, RecordLaunchObservationResult, Store};
use ases_resource_control::catalog::Account;
use serde::{Deserialize, Serialize};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Clone, Debug, Serialize, Deserialize)]
struct ChildEvidence { pid: u32, start_token: String }

fn start_token(pid:u32)->String{
    fs::read_to_string(format!("/proc/{pid}/stat")).unwrap().rsplit_once(") ").unwrap()
        .1.split_whitespace().nth(19).unwrap().to_string()
}
fn is_live(identity:&ChildEvidence)->bool{
    let Ok(stat)=fs::read_to_string(format!("/proc/{}/stat",identity.pid)) else{return false};
    let Some((_,tail))=stat.rsplit_once(") ") else{return false};
    let mut fields=tail.split_whitespace();
    let Some(state)=fields.next().and_then(|s|s.chars().next()) else{return false};
    let Some(token)=fields.nth(18) else{return false};
    matches!(state,'R'|'S') && token==identity.start_token
}
fn wait_file(path:&Path){
    let end=Instant::now()+Duration::from_secs(10);
    while Instant::now()<end {if path.exists(){return} thread::sleep(Duration::from_millis(10));}
    panic!("worker marker timeout");
}
fn child(marker:&Path,release:&Path)->Child{
    Command::new(std::env::current_exe().unwrap())
        .args(["--exact","comparator_fixed_worker","--nocapture"])
        .env("ASES_PRECHANGE_WORKER","1").env("ASES_PRECHANGE_MARKER",marker)
        .env("ASES_PRECHANGE_RELEASE",release).stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap()
}
fn setup(store:&mut Store,job:&str)->i64{
    store.register_account(&Account{id:"legacy-account".into(),provider:"local".into(),payer_ref:"local".into(),
        registration_status:"verified".into(),credential_status:"working".into(),entitlement_status:"active".into(),
        allowed_projects:vec!["legacy-project".into()],source:"legacy-native-comparator".into(),observed_at:now(),ttl_seconds:3600}).unwrap();
    store.register_meter(&Meter{id:"legacy-meter".into(),account:"legacy-account".into(),provider:"local".into(),product:"fixed-child".into(),
        period:"legacy-test".into(),unit:"slots".into(),limit:100,guard:0,observed_at:now(),ttl_seconds:3600,
        source:"legacy-native-comparator".into(),period_start:None,period_end:None,price_per_unit_micros:0,price_currency:None,chargeable:false}).unwrap();
    store.register_environment(&Environment{id:"legacy-env".into(),account:"legacy-account".into(),provider:"local".into(),
        max_parallel:1,observed_at:now(),ttl_seconds:3600,source:"legacy-native-comparator".into()}).unwrap();
    let revision=store.catalog_version().unwrap();
    let p=Proposal{job_id:job.into(),account_id:"legacy-account".into(),project_id:"legacy-project".into(),environment_id:"legacy-env".into(),
        estimated_wall_seconds:300,claims:vec![Claim{meter_id:"legacy-meter".into(),amount:50}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None};
    store.reserve(&p,revision,now()).unwrap();
    store.acknowledge(job,"legacy-ack",revision,now()).unwrap();
    revision
}
fn persist(name:&str,value:serde_json::Value){
    let dir=PathBuf::from(std::env::var_os("ASES_PRECHANGE_EVIDENCE_DIR").unwrap());
    fs::create_dir_all(&dir).unwrap();
    fs::write(dir.join(name),serde_json::to_vec_pretty(&value).unwrap()).unwrap();
}

#[test]
fn comparator_fixed_worker(){
    if std::env::var("ASES_PRECHANGE_WORKER").as_deref()!=Ok("1"){return;}
    let marker=PathBuf::from(std::env::var_os("ASES_PRECHANGE_MARKER").unwrap());
    let release=PathBuf::from(std::env::var_os("ASES_PRECHANGE_RELEASE").unwrap());
    let record=ChildEvidence{pid:std::process::id(),start_token:start_token(std::process::id())};
    let mut file=OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file,&record).unwrap();file.write_all(b"\n").unwrap();file.sync_all().unwrap();
    let until=Instant::now()+Duration::from_secs(20);
    while !release.exists() && Instant::now()<until{thread::sleep(Duration::from_millis(10));}
}

#[test]
fn prechange_finalize_cancelled_releases_while_exact_child_is_live(){
    let dir=tempfile::tempdir().unwrap();
    let db=dir.path().join("legacy.sqlite");
    let mut store=Store::open(&db).unwrap();
    let revision=setup(&mut store,"legacy-running");
    assert!(matches!(store.begin_launch("legacy-running","legacy-launch",revision,now()).unwrap(),
        BeginLaunchResult::DispatchGranted(_)));
    let marker=dir.path().join("child.json");let release=dir.path().join("child.release");
    let mut owned_child=child(&marker,&release);wait_file(&marker);
    let child:ChildEvidence=serde_json::from_slice(&fs::read(&marker).unwrap()).unwrap();
    let process=ProcessIdentity{pid:child.pid,start_token:child.start_token.clone()};
    assert_eq!(store.observe_launch("legacy-running","legacy-launch",&LaunchObservation::Started{process},now()).unwrap(),
        RecordLaunchObservationResult::Started);
    let events_before=store.event_log(Some("legacy-running")).unwrap();
    let balances_before=store.balances(now()).unwrap();
    assert!(is_live(&child));assert!(owned_child.try_wait().unwrap().is_none());
    let finalized=store.finalize("legacy-running","cancelled",now()).unwrap();
    let job_after=store.job("legacy-running").unwrap();
    let balances_after=store.balances(now()).unwrap();
    let events_after=store.event_log(Some("legacy-running")).unwrap();
    assert_eq!(finalized,"CLOSED");
    assert!(is_live(&child),"actual child remains live after cancelled finalization");
    assert!(owned_child.try_wait().unwrap().is_none(),"owned Child handle confirms no exit yet");
    assert_eq!(job_after["state"],"CLOSED");
    assert!(balances_after[0].active_reserved_remaining<balances_before[0].active_reserved_remaining,
        "pre-change finalize released the reservation");
    assert_eq!(events_after.len(),events_before.len()+1);
    let contender=Proposal{job_id:"legacy-contender".into(),account_id:"legacy-account".into(),project_id:"legacy-project".into(),
        environment_id:"legacy-env".into(),estimated_wall_seconds:30,
        claims:vec![Claim{meter_id:"legacy-meter".into(),amount:50}],paid_spend_cap_micros:None,
        paid_spend_cap_currency:None,forecast_context:None};
    store.reserve(&contender,revision,now()).unwrap();
    let manifest=PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let source_sha=format!("{:x}",Sha256::digest(fs::read(manifest.join("src/lib.rs")).unwrap()));
    persist("prechange-live-finalize.json",json!({
        "source_commit":"9fb8a525c32b56b9191d3f33df9925939636dc9a",
        "source_lib_sha256":source_sha,"child":child,"child_live_after_finalize":true,
        "owned_child_try_wait_after_finalize":null,"finalize_result":finalized,
        "job_after":job_after,"balances_before":balances_before,"balances_after":balances_after,
        "events_before":events_before,"events_after":events_after,
        "second_reservation":"RESERVED","exact_child_handle_wait_after_evidence":true
    }));
    fs::write(release,b"release\n").unwrap();
    assert_eq!(owned_child.wait().unwrap().code(),Some(0));
}
