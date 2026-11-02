use ases_resource_control::{archive::verify_archive, now, Claim, Environment, Meter, Proposal, Store};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Barrier};
use std::thread;
use tempfile::TempDir;

fn meter(id:&str,limit:u64)->Meter {
    Meter {
        id:id.into(), account:"acct-a".into(),provider:"github".into(),product:"codespaces".into(),
        period:"2026-11".into(),unit:"core_minutes".into(),limit,guard:0,
        observed_at:now(),ttl_seconds:3600,source:"synthetic:test".into(),
        price_per_unit_micros:0,chargeable:false
    }
}
fn environment(slots:u32)->Environment {
    Environment{id:"codespace".into(),account:"acct-a".into(),max_parallel:slots,
                observed_at:now(),ttl_seconds:3600,source:"synthetic:test".into()}
}
fn proposal(id:&str,amount:u64)->Proposal{
    Proposal{job_id:id.into(),account_id:"acct-a".into(),environment_id:"codespace".into(),
             estimated_wall_seconds:45*60,claims:if amount==0 {vec![]} else {
                 vec![Claim{meter_id:"core".into(),amount}] },
             paid_spend_cap_micros:None,forecast_context:Some(serde_json::json!({
               "estimated_minutes":45,"cores":2,"origin":"pre-execution forecast"
             }))}
}
fn setup(limit:u64,slots:u32)->(TempDir,PathBuf,Store) {
    let dir=tempfile::tempdir().unwrap();
    let path=dir.path().join("control.sqlite");
    let mut s=Store::open(&path).unwrap();
    s.register_meter(&meter("core",limit)).unwrap();
    s.register_environment(&environment(slots)).unwrap();
    (dir,path,s)
}
fn reserve(s:&mut Store,p:&Proposal){
    let rev=s.catalog_version().unwrap();
    assert!(s.quote(p,now()).unwrap().eligible);
    assert_eq!(s.reserve(p,rev,now()).unwrap().status,"RESERVED");
}
fn running(s:&mut Store,p:&Proposal){
    reserve(s,p);
    let rev=s.catalog_version().unwrap();
    assert_eq!(s.acknowledge(&p.job_id,"ack1",rev,now()).unwrap(),"AUTHORIZED");
    assert_eq!(s.launch_mock(&p.job_id,"launch1",now()).unwrap(),"MOCK_RUNNING");
}
fn balance(s:&mut Store)->ases_resource_control::Balance{
    s.balances(now()).unwrap().into_iter().find(|b|b.meter_id=="core").unwrap()
}
fn assert_error_contains<T>(r:ases_resource_control::Result<T>,needle:&str){
    match r {Ok(_)=>panic!("expected error containing {needle}"),Err(e)=>assert!(e.to_string().contains(needle),"unexpected error: {e}") }
}
#[test]
fn quote_is_advisory_without_a_reservation() {
    let (_dir,_path,mut s)=setup(100,2);
    let p=proposal("quote-only",90);
    let q=s.quote(&p,now()).unwrap();
    assert!(q.eligible);
    assert_eq!(q.estimated_cash_micros,0);
    assert_eq!(balance(&mut s).available,100);
    assert_error_contains(s.job("quote-only"),"unknown job");
}
#[test]
fn shorter_job_releases_unused_allocation_but_keeps_actual() {
    let (_d,_p,mut s)=setup(100,2);
    let p=proposal("short",90);
    running(&mut s,&p);
    assert_eq!(balance(&mut s).available,10);
    s.observe_usage("short-u",Some("short"),"core",60,now(),"mock-provider").unwrap();
    assert_eq!(balance(&mut s).available,10);
    assert_eq!(s.job("short").unwrap()["meters"][0]["unspent"],30);
    s.finalize("short","completed",now()).unwrap();
    assert_eq!(balance(&mut s).available,40);
    assert_eq!(s.job("short").unwrap()["meters"][0]["observed"],60);
}
#[test]
fn overrun_is_recorded_even_when_it_exceeds_reservation_and_limit() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("overrun",90));
    s.observe_usage("u-120",Some("overrun"),"core",120,now(),"synthetic-meter").unwrap();
    assert_eq!(s.job("overrun").unwrap()["meters"][0]["overrun"],30);
    assert_eq!(balance(&mut s).available,-20);
    assert_eq!(s.reconcile(now()).unwrap()["deficits"][0]["deficit"],20);
    assert!(!s.quote(&proposal("second",1),now()).unwrap().eligible);
    s.finalize("overrun","completed",now()).unwrap();
    assert_eq!(balance(&mut s).available,-20);
}
#[test]
fn environment_and_agent_lifetimes_are_independent() {
    let (_d,_p,mut s)=setup(400,1);
    running(&mut s,&proposal("idle",120));
    let t=now()-1800;
    for (id,kind,subject,offset) in [
        ("env-on","ENV_STARTED","host",0),
        ("agent-on","AGENT_STARTED","builder",600),
        ("agent-off","AGENT_STOPPED","builder",2400),
        ("env-off","ENV_STOPPED","host",3600),
    ]{
        s.observe_lifecycle(id,"idle",kind,t+offset,subject,serde_json::json!({})).unwrap();
    }
    let timeline=s.timeline("idle").unwrap();
    assert_eq!(timeline["observed_interval_seconds"]["environment"],3600);
    assert_eq!(timeline["observed_interval_seconds"]["agent"],1800);
    assert_eq!(timeline["incomplete_or_ambiguous"],false);
    s.observe_usage("runtime",Some("idle"),"core",120,now(),"metered-runtime").unwrap();
    s.finalize("idle","completed",now()).unwrap();
    assert_eq!(s.job("idle").unwrap()["meters"][0]["observed"],120);
}
#[test]
fn parallel_agents_do_not_partition_environment_lifetime() {
    let (_d,_p,mut s)=setup(1000,2);
    running(&mut s,&proposal("parallel",10));
    let t=now()-200;
    for (id,kind,subject,dt) in [
        ("e1","ENV_STARTED","host",0),("a1","AGENT_STARTED","a",0),
        ("b1","AGENT_STARTED","b",10),("a2","AGENT_STOPPED","a",70),
        ("b2","AGENT_STOPPED","b",90),("e2","ENV_STOPPED","host",100)
    ]{
        s.observe_lifecycle(id,"parallel",kind,t+dt,subject,serde_json::json!({})).unwrap();
    }
    let x=s.timeline("parallel").unwrap();
    assert_eq!(x["observed_interval_seconds"]["environment"],100);
    assert_eq!(x["observed_interval_seconds"]["agent"],150);
}
#[test]
fn missing_lifecycle_partner_remains_unknown() {
    let (_d,_p,mut s)=setup(100,1);
    running(&mut s,&proposal("partial",5));
    s.observe_lifecycle("start-only","partial","AGENT_STARTED",now(),"agent",serde_json::json!({})).unwrap();
    assert_eq!(s.timeline("partial").unwrap()["incomplete_or_ambiguous"],true);
}
#[test]
fn lifecycle_is_idempotent_and_rejects_conflicting_reuse() {
    let (_d,_p,mut s)=setup(100,1);
    running(&mut s,&proposal("life",5));
    assert_eq!(s.observe_lifecycle("eid","life","ENV_STARTED",100,"host",serde_json::json!({"x":1})).unwrap(),"LIFECYCLE_RECORDED");
    assert_eq!(s.observe_lifecycle("eid","life","ENV_STARTED",100,"host",serde_json::json!({"x":1})).unwrap(),"LIFECYCLE_REPLAY");
    assert_error_contains(s.observe_lifecycle("eid","life","ENV_STARTED",101,"host",serde_json::json!({"x":1})),"reused");
    assert_error_contains(s.observe_lifecycle("new","life","INVENTED_STATUS",100,"host",serde_json::json!({})),"unsupported");
}
#[test]
fn account_mismatch_rejected_for_environment_and_meter() {
    let (_d,_p,mut s)=setup(100,2);
    let mut p=proposal("wrong-account",20);
    p.account_id="acct-b".into();
    assert!(!s.quote(&p,now()).unwrap().eligible);
    assert_error_contains(s.reserve(&p,s.catalog_version().unwrap(),now()),"account mismatch");
    let mut other=meter("other-account",100);
    other.account="acct-b".into();
    s.register_meter(&other).unwrap();
    let mut p=proposal("wrong-meter",20);
    p.claims[0].meter_id="other-account".into();
    assert_error_contains(s.reserve(&p,s.catalog_version().unwrap(),now()),"meter account mismatch");
}
#[test]
fn meter_identity_cannot_be_rebound_to_another_period() {
    let (_d,_p,mut s)=setup(100,1);
    let mut changed=meter("core",100);
    changed.period="2026-12".into();
    assert_error_contains(s.register_meter(&changed),"identity cannot be rebound");
}
#[test]
fn zero_meter_claim_still_obeys_environment_admission() {
    let (_d,_p,mut s)=setup(100,1);
    running(&mut s,&proposal("free-no-meter",0));
    assert_eq!(balance(&mut s).available,100);
    assert!(!s.quote(&proposal("another",0),now()).unwrap().eligible);
    s.finalize("free-no-meter","completed",now()).unwrap();
    assert!(s.quote(&proposal("another",0),now()).unwrap().eligible);
}
#[test]
fn strict_authorization_order_and_single_launch() {
    let (_d,_p,mut s)=setup(100,2);
    let p=proposal("guard",10);
    assert_error_contains(s.launch_mock("guard","launch",now()),"unknown job");
    reserve(&mut s,&p);
    assert_error_contains(s.launch_mock("guard","launch",now()),"forbidden");
    assert_error_contains(s.finalize("guard","completed",now()),"unlaunched");
    let rev=s.catalog_version().unwrap();
    s.acknowledge("guard","ack",rev,now()).unwrap();
    assert_eq!(s.launch_mock("guard","launch",now()).unwrap(),"MOCK_RUNNING");
    assert_eq!(s.launch_mock("guard","launch",now()).unwrap(),"RUNNING_REPLAY");
    assert_error_contains(s.launch_mock("guard","different",now()),"forbidden");
    assert_eq!(s.acknowledge("guard","ack",rev,now()).unwrap(),"AUTHORIZED_REPLAY");
}
#[test]
fn catalog_drift_blocks_authorization_and_launch() {
    let (_d,_p,mut s)=setup(100,3);
    let p=proposal("drift",15);
    let rev=s.catalog_version().unwrap();
    s.reserve(&p,rev,now()).unwrap();
    s.register_meter(&meter("other",100)).unwrap();
    assert_error_contains(s.acknowledge("drift","ack",rev,now()),"catalog changed");
    s.finalize("drift","cancelled",now()).unwrap();
    let p=proposal("drift2",15);
    let rev=s.catalog_version().unwrap();
    s.reserve(&p,rev,now()).unwrap();
    s.acknowledge("drift2","ack",rev,now()).unwrap();
    s.register_meter(&meter("other2",100)).unwrap();
    assert_error_contains(s.launch_mock("drift2","launch",now()),"catalog revision stale");
}
#[test]
fn staleness_blocks_and_valid_neighbor_passes() {
    let (_d,_p,mut s)=setup(100,2);
    let mut old=meter("core",100);
    old.observed_at=now()-4000;
    s.register_meter(&old).unwrap();
    assert!(!s.quote(&proposal("old",10),now()).unwrap().eligible);
    s.register_meter(&meter("core",100)).unwrap();
    assert!(s.quote(&proposal("fresh",10),now()).unwrap().eligible);
}
#[test]
fn duplicate_reservation_is_idempotent_but_changed_forecast_is_not() {
    let (_d,_p,mut s)=setup(100,2);
    let p=proposal("dedup",20);
    let rev=s.catalog_version().unwrap();
    assert!(!s.reserve(&p,rev,now()).unwrap().replayed);
    assert!(s.reserve(&p,rev,now()).unwrap().replayed);
    let mut changed=p.clone();changed.estimated_wall_seconds+=60;
    assert_error_contains(s.reserve(&changed,rev,now()),"reused");
    assert_eq!(balance(&mut s).available,80);
}
#[test]
fn distinct_connections_compete_under_sqlite_transaction() {
    let (dir,path,mut initial)=setup(90,10);
    let rev=initial.catalog_version().unwrap();
    drop(initial);
    let barrier=Arc::new(Barrier::new(9));
    let mut tasks=Vec::new();
    for i in 0..8 {
        let path=path.clone();let barrier=barrier.clone();
        tasks.push(thread::spawn(move|| {
            let mut s=Store::open(&path).unwrap();
            barrier.wait();
            s.reserve(&proposal(&format!("compete-{i}"),90),rev,now()).is_ok()
        }));
    }
    barrier.wait();
    let accepted=tasks.into_iter().map(|h|h.join().unwrap() as u32).sum::<u32>();
    assert_eq!(accepted,1);
    let mut s=Store::open(&path).unwrap();
    assert_eq!(balance(&mut s).available,0);
    drop(dir);
}
#[test]
fn restart_preserves_reservation_ack_and_single_launch_id() {
    let (_d,path,mut s)=setup(100,2);
    let rev=s.catalog_version().unwrap();
    let p=proposal("recovery",30);
    s.reserve(&p,rev,now()).unwrap();
    drop(s);
    let mut s=Store::open(&path).unwrap();
    s.acknowledge("recovery","ack",rev,now()).unwrap();
    drop(s);
    let mut s=Store::open(&path).unwrap();
    assert_eq!(s.acknowledge("recovery","ack",rev,now()).unwrap(),"AUTHORIZED_REPLAY");
    s.launch_mock("recovery","launch",now()).unwrap();
    drop(s);
    let mut s=Store::open(&path).unwrap();
    assert_eq!(s.launch_mock("recovery","launch",now()).unwrap(),"RUNNING_REPLAY");
    assert_eq!(s.job("recovery").unwrap()["state"],"RUNNING");
    assert_eq!(balance(&mut s).available,70);
}
#[test]
fn expired_unlaunched_reservation_releases_capacity() {
    let (_d,_p,mut s)=setup(100,1);
    let rev=s.catalog_version().unwrap();
    s.reserve(&proposal("expire",100),rev,now()).unwrap();
    assert_eq!(s.expire_unlaunched(now()+951).unwrap(),1);
    assert_eq!(balance(&mut s).available,100);
    assert_error_contains(s.launch_mock("expire","too-late",now()),"forbidden");
}
#[test]
fn finalized_observation_can_arrive_later() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("late",50));
    s.finalize("late","completed",now()).unwrap();
    assert_eq!(balance(&mut s).available,100);
    s.observe_usage("late-bill",Some("late"),"core",70,now(),"provider-delayed").unwrap();
    assert_eq!(balance(&mut s).available,30);
    assert_eq!(s.job("late").unwrap()["meters"][0]["overrun"],20);
}
#[test]
fn duplicate_observation_is_idempotent_and_conflicting_reuse_is_rejected() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("obs",10));
    let t=now();
    assert_eq!(s.observe_usage("evt1",Some("obs"),"core",10,t,"test").unwrap(),"USAGE_RECORDED");
    assert_eq!(s.observe_usage("evt1",Some("obs"),"core",10,t,"test").unwrap(),"USAGE_REPLAY");
    assert_error_contains(s.observe_usage("evt1",Some("obs"),"core",11,t,"test"),"different");
    assert_eq!(balance(&mut s).available,90);
}
#[test]
fn provider_watermark_avoids_double_counting_local_usage() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("report",20));
    let t=now()-10;
    s.observe_usage("u-before",Some("report"),"core",10,t,"local").unwrap();
    s.provider_report("pr1","core",15,Some(t),t+1,"provider").unwrap();
    let b=balance(&mut s);
    assert_eq!(b.local_observed,10);
    assert_eq!(b.effective_consumed,15);
    assert_eq!(b.active_reserved_remaining,10);
    assert_eq!(b.available,75);
    s.observe_usage("u-after",Some("report"),"core",5,t+2,"local").unwrap();
    assert_eq!(balance(&mut s).effective_consumed,20);
    assert_eq!(balance(&mut s).available,75);
}
#[test]
fn unknown_report_coverage_is_conservative_not_zero() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("aggregate",20));
    let t=now()-10;
    s.observe_usage("u1",Some("aggregate"),"core",10,t,"local").unwrap();
    s.provider_report("pr1","core",15,None,t+1,"provider-aggregate").unwrap();
    assert_eq!(balance(&mut s).effective_consumed,25);
    assert_eq!(balance(&mut s).available,65);
}
#[test]
fn externally_consumed_credits_reduce_future_availability() {
    let (_d,_p,mut s)=setup(100,2);
    s.provider_report("external","core",55,Some(now()-1),now(),"provider").unwrap();
    assert_eq!(balance(&mut s).available,45);
    assert!(!s.quote(&proposal("too-big",46),now()).unwrap().eligible);
    assert!(s.quote(&proposal("fits",45),now()).unwrap().eligible);
}
#[test]
fn report_replay_and_decreasing_totals_are_safe() {
    let (_d,_p,mut s)=setup(100,2);
    let t=now()-10;
    assert_eq!(s.provider_report("pr","core",12,Some(t),t+1,"provider").unwrap(),"PROVIDER_RECORDED");
    assert_eq!(s.provider_report("pr","core",12,Some(t),t+1,"provider").unwrap(),"REPORT_REPLAY");
    assert_error_contains(s.provider_report("pr","core",13,Some(t),t+1,"provider"),"reused");
    assert_error_contains(s.provider_report("lower","core",11,Some(t),t+2,"provider"),"decreasing");
    assert_error_contains(s.provider_report("older","core",13,Some(t),t,"provider"),"stale");
}
#[test]
fn provider_usage_after_reservation_blocks_new_launch_when_overconsumed() {
    let (_d,_p,mut s)=setup(100,3);
    let rev=s.catalog_version().unwrap();
    s.reserve(&proposal("uncertain",90),rev,now()).unwrap();
    s.provider_report("late-external","core",30,Some(now()-1),now(),"provider").unwrap();
    assert_error_contains(s.acknowledge("uncertain","ack",rev,now()),"exceeds admitted");
}
#[test]
fn paid_claim_requires_explicit_cap_and_known_price() {
    let (_d,_p,mut s)=setup(200,3);
    let mut expensive=meter("core",200);
    expensive.price_per_unit_micros=1000;
    expensive.chargeable=true;
    s.register_meter(&expensive).unwrap();
    let p=proposal("cash",20);
    assert!(!s.quote(&p,now()).unwrap().eligible);
    assert_error_contains(s.reserve(&p,s.catalog_version().unwrap(),now()),"spend cap");
    let mut p=p;p.paid_spend_cap_micros=Some(19999);
    assert!(!s.quote(&p,now()).unwrap().eligible);
    p.paid_spend_cap_micros=Some(20000);
    assert_eq!(s.quote(&p,now()).unwrap().estimated_cash_micros,20000);
    reserve(&mut s,&p);
}
#[test]
fn limits_arithmetic_and_mutant_boundaries() {
    let (_d,_p,mut s)=setup(100,2);
    assert!(s.quote(&proposal("exact",100),now()).unwrap().eligible);
    assert!(!s.quote(&proposal("over",101),now()).unwrap().eligible);
    let mut bad=proposal("zero",0);bad.estimated_wall_seconds=0;
    assert!(!s.quote(&bad,now()).unwrap().eligible);
    let mut bad=proposal("duplicate",10);
    bad.claims.push(bad.claims[0].clone());
    assert!(!s.quote(&bad,now()).unwrap().eligible);
    let mut m=meter("negative-guard",100);m.guard=101;
    assert_error_contains(s.register_meter(&m),"guard exceeds");
    let mut m=meter("unknown-price",100);m.chargeable=true;
    assert_error_contains(s.register_meter(&m),"without verified");
    let mut m=meter("overflow",u64::MAX);m.guard=0;
    assert_error_contains(s.register_meter(&m),"exceeds SQLite integer");
}
#[test]
fn archive_roundtrip_verification_and_corruption_detection() {
    let (d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("archive",40));
    s.observe_usage("au",Some("archive"),"core",30,now(),"test").unwrap();
    s.finalize("archive","completed",now()).unwrap();
    let file=d.path().join("archive.jsonl.gz");
    let m=s.export_session("archive",&file).unwrap();
    assert!(m.records>=5);
    assert!(m.local_recovery_verified);
    assert!(!m.offsite_recovery_verified);
    assert_eq!(verify_archive(&file,&m.sha256,m.records).unwrap(),m.records);
    assert_error_contains(s.export_session("archive",&file),"never overwrite");
    let mut bytes=std::fs::read(&file).unwrap();
    bytes[0]^=0x01;
    std::fs::write(&file,bytes).unwrap();
    assert_error_contains(verify_archive(&file,&m.sha256,m.records),"digest mismatch");
}
#[test]
fn cancellations_and_replays_do_not_resurrect_finished_execution() {
    let (_d,_p,mut s)=setup(100,2);
    reserve(&mut s,&proposal("cancel",40));
    s.finalize("cancel","cancelled",now()).unwrap();
    assert_eq!(s.finalize("cancel","cancelled",now()).unwrap(),"CLOSED_REPLAY");
    assert_error_contains(s.finalize("cancel","completed",now()),"already recorded");
    assert_error_contains(s.launch_mock("cancel","launch",now()),"forbidden");
    assert_eq!(balance(&mut s).available,100);
}
#[test]
fn deterministic_multi_job_history_matches_ledger() {
    let (_d,_p,mut s)=setup(1000,25);
    let mut total=0;
    for i in 0..15 {
        let planned=(i+1)*7;
        let actual=planned+if i%3==0 {4} else {-3};
        let job=format!("series-{i}");
        let p=proposal(&job,planned as u64);
        running(&mut s,&p);
        s.observe_usage(&format!("obs-{i}"),Some(&job),"core",actual as u64,now(),"synthetic").unwrap();
        s.finalize(&job,"completed",now()).unwrap();
        total+=actual;
    }
    let b=balance(&mut s);
    assert_eq!(b.local_observed,total as i64);
    assert_eq!(b.available,1000-total as i64);
    assert_eq!(b.active_reserved_remaining,0);
}
#[test]
fn cli_launch_is_separate_process_and_recovers_state() {
    let (_d,path,mut s)=setup(100,2);
    let rev=s.catalog_version().unwrap();
    let p=proposal("cli",10);
    let req=serde_json::json!({"op":"reserve","proposal":p,"expected_catalog":rev}).to_string();
    drop(s);
    let exe=env!("CARGO_BIN_EXE_ases-resource-control");
    let call=|data:&str|{
        let x=std::process::Command::new(exe).arg(&path).arg("request").arg(data).output().unwrap();
        assert!(x.status.success(),"stderr: {}",String::from_utf8_lossy(&x.stderr));
        serde_json::from_slice::<serde_json::Value>(&x.stdout).unwrap()
    };
    assert_eq!(call(&req)["result"]["status"],"RESERVED");
    assert_eq!(call(&serde_json::json!({"op":"acknowledge","job_id":"cli",
               "acknowledgement_id":"ack","expected_catalog":rev}).to_string())["result"]["authorization"],"AUTHORIZED");
    assert_eq!(call(&serde_json::json!({"op":"launch_mock","job_id":"cli",
               "launch_id":"launch"}).to_string())["result"]["execution"],"MOCK_RUNNING");
    let mut s=Store::open(&path).unwrap();
    assert_eq!(s.job("cli").unwrap()["state"],"RUNNING");
    assert_eq!(balance(&mut s).available,90);
}
#[test]
fn tests_are_reproducible_from_fixture_path_not_external_services() {
    let (_d,path,s)=setup(100,1);
    assert!(Path::new(&path).exists());
    assert_eq!(s.catalog_version().unwrap(),2);
}
