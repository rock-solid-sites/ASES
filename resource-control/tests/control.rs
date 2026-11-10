use ases_resource_control::{archive::verify_archive, now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::catalog::{Account,CatalogImport};
use std::path::{Path, PathBuf};
use std::sync::{Arc, Barrier};
use std::thread;
use tempfile::TempDir;

fn meter(id:&str,limit:u64)->Meter {
    Meter {
        id:id.into(), account:"acct-a".into(),provider:"github".into(),product:"codespaces".into(),
        period:"2026-11".into(),unit:"core_minutes".into(),limit,guard:0,
        observed_at:now(),ttl_seconds:3600,source:"synthetic:test".into(),
        period_start:None,period_end:None,price_per_unit_micros:0,price_currency:None,chargeable:false
    }
}
fn environment(slots:u32)->Environment {
    Environment{id:"codespace".into(),account:"acct-a".into(),provider:"github".into(),max_parallel:slots,
                observed_at:now(),ttl_seconds:3600,source:"synthetic:test".into()}
}
fn proposal(id:&str,amount:u64)->Proposal{
    Proposal{job_id:id.into(),account_id:"acct-a".into(),project_id:"project-a".into(),environment_id:"codespace".into(),
             estimated_wall_seconds:45*60,claims:if amount==0 {vec![]} else {
                 vec![Claim{meter_id:"core".into(),amount}] },
             paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:Some(serde_json::json!({
               "estimated_minutes":45,"cores":2,"origin":"pre-execution forecast"
             }))}
}
fn setup(limit:u64,slots:u32)->(TempDir,PathBuf,Store) {
    let dir=tempfile::tempdir().unwrap();
    let path=dir.path().join("control.sqlite");
    let mut s=Store::open(&path).unwrap();
    s.register_account(&Account{
        id:"acct-a".into(),provider:"github".into(),payer_ref:"payer-a".into(),
        registration_status:"verified".into(),credential_status:"working".into(),
        entitlement_status:"active".into(),allowed_projects:vec!["project-a".into()],
        source:"synthetic-account-confirmation".into(),observed_at:now(),ttl_seconds:3600
    }).unwrap();
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
    s.register_account(&Account{
        id:"acct-b".into(),provider:"github".into(),payer_ref:"payer-b".into(),
        registration_status:"verified".into(),credential_status:"working".into(),
        entitlement_status:"active".into(),allowed_projects:vec!["project-a".into()],
        source:"synthetic".into(),observed_at:now(),ttl_seconds:3600
    }).unwrap();
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
    let (dir,path,initial)=setup(90,10);
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
fn launch_intent_is_one_use_durable_and_observations_are_idempotent() {
    use ases_resource_control::{BeginLaunchResult,LaunchObservation,ProcessIdentity,RecordLaunchObservationResult};
    let (_d,_p,mut s)=setup(100,1);
    let p=proposal("intent",40);
    reserve(&mut s,&p);
    let revision=s.catalog_version().unwrap();
    s.acknowledge("intent","ack-intent",revision,now()).unwrap();
    assert_error_contains(s.begin_launch("intent","wrong-revision",revision+1,now()),"catalog revision stale");
    assert_eq!(s.job("intent").unwrap()["state"],"AUTHORIZED");
    let first=s.begin_launch("intent","launch-intent",revision,now()).unwrap();
    match first {
        BeginLaunchResult::DispatchGranted(permit)=>{
            assert_eq!(permit.job_id(),"intent");assert_eq!(permit.launch_id(),"launch-intent");
        }
        other=>panic!("first begin must grant dispatch exactly once: {other:?}"),
    }
    assert_eq!(s.job("intent").unwrap()["state"],"LAUNCHING");
    assert_eq!(balance(&mut s).active_reserved_remaining,40);
    assert_error_contains(s.reserve(&proposal("slot-contender",10),revision,now()),"concurrency exhausted");
    assert_eq!(s.begin_launch("intent","launch-intent",revision,now()).unwrap(),
        BeginLaunchResult::PendingObservation{job_id:"intent".into(),launch_id:"launch-intent".into()});
    assert_error_contains(s.begin_launch("intent","different-launch",revision,now()),"conflicts");
    assert_error_contains(s.finalize("intent","cancelled",now()),"outcome unknown");
    assert_eq!(s.expire_unlaunched(now()+10_000).unwrap(),0);
    assert_eq!(balance(&mut s).active_reserved_remaining,40);
    let mut env=environment(1);env.source="catalog-changed-after-intent".into();
    s.register_environment(&env).unwrap();
    assert_eq!(s.begin_launch("intent","launch-intent",revision,now()).unwrap(),
        BeginLaunchResult::PendingObservation{job_id:"intent".into(),launch_id:"launch-intent".into()});

    let started=LaunchObservation::Started{process:ProcessIdentity{pid:1234,start_token:"start-abc".into()}};
    assert_eq!(s.observe_launch("intent","launch-intent",&started,now()).unwrap(),RecordLaunchObservationResult::Started);
    assert_eq!(s.observe_launch("intent","launch-intent",&started,now()).unwrap(),RecordLaunchObservationResult::Replay);
    assert_eq!(s.begin_launch("intent","launch-intent",revision,now()).unwrap(),
        BeginLaunchResult::RunningObservation{job_id:"intent".into(),launch_id:"launch-intent".into()});
    let contradiction=LaunchObservation::DefinitelyNotCreated{error_kind:"NotFound".into(),detail:"contradiction".into()};
    assert_error_contains(s.observe_launch("intent","launch-intent",&contradiction,now()),"conflicts");
    assert_eq!(s.begin_launch("intent","launch-intent",revision,now()).unwrap(),
        BeginLaunchResult::RunningObservation{job_id:"intent".into(),launch_id:"launch-intent".into()});
    s.finalize("intent","completed",now()).unwrap();
    reserve(&mut s,&proposal("after-intent",100));
}

#[test]
fn mock_launch_profile_is_not_misreported_as_a_durable_intent() {
    let (_d,_p,mut s)=setup(100,1);
    let p=proposal("mock-profile",20);
    running(&mut s,&p);
    let revision=s.catalog_version().unwrap();
    assert_error_contains(s.begin_launch("mock-profile","launch1",revision,now()),"another launch profile");
    assert_eq!(s.job("mock-profile").unwrap()["state"],"RUNNING");
    assert_eq!(s.launch_mock("mock-profile","launch1",now()).unwrap(),"RUNNING_REPLAY");
}

#[test]
fn definite_noncreation_releases_slot_and_stale_catalog_blocks_intent() {
    use ases_resource_control::{LaunchObservation,RecordLaunchObservationResult};
    let (_d,_p,mut s)=setup(100,1);
    let p=proposal("not-created",100);
    reserve(&mut s,&p);
    let revision=s.catalog_version().unwrap();
    s.acknowledge("not-created","ack",revision,now()).unwrap();
    s.begin_launch("not-created","launch",revision,now()).unwrap();
    let failed=LaunchObservation::DefinitelyNotCreated{
        error_kind:"PermissionDenied".into(),detail:"fixed worker spawn returned an OS error".into()};
    assert_eq!(s.observe_launch("not-created","launch",&failed,now()).unwrap(),
        RecordLaunchObservationResult::DefinitelyNotCreated);
    assert_eq!(s.job("not-created").unwrap()["state"],"CLOSED");
    assert_eq!(balance(&mut s).active_reserved_remaining,0);
    reserve(&mut s,&proposal("after-failure",100));

    let revision=s.catalog_version().unwrap();
    s.acknowledge("after-failure","ack",revision,now()).unwrap();
    let mut env=environment(1);env.source="refreshed-current-catalog".into();
    s.register_environment(&env).unwrap();
    assert_error_contains(s.begin_launch("after-failure","stale-launch",revision,now()),"catalog revision stale");
    assert_eq!(s.job("after-failure").unwrap()["state"],"AUTHORIZED");
}

#[test]
fn independent_begin_launch_contenders_receive_one_dispatch_capability() {
    use ases_resource_control::BeginLaunchResult;
    let (_d,path,mut initial)=setup(100,1);
    let p=proposal("contended-launch",50);
    reserve(&mut initial,&p);
    let revision=initial.catalog_version().unwrap();
    initial.acknowledge("contended-launch","ack",revision,now()).unwrap();
    drop(initial);
    let barrier=Arc::new(Barrier::new(5));
    let mut tasks=Vec::new();
    for _ in 0..4 {
        let path=path.clone();let barrier=barrier.clone();
        tasks.push(thread::spawn(move||{
            let mut store=Store::open(&path).unwrap();
            barrier.wait();
            store.begin_launch("contended-launch","same-launch",revision,now()).unwrap()
        }));
    }
    barrier.wait();
    let results:Vec<_>=tasks.into_iter().map(|task|task.join().unwrap()).collect();
    assert_eq!(results.iter().filter(|r|matches!(r,BeginLaunchResult::DispatchGranted(_))).count(),1);
    assert_eq!(results.iter().filter(|r|matches!(r,BeginLaunchResult::PendingObservation{..})).count(),3);
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
fn expiry_is_terminal_and_cannot_be_rewritten_by_finalization() {
    let mut histories=Vec::new();
    let mut valid=true;
    for outcome in ["completed","failed","cancelled","interrupted"] {
        let (_dir,_path,mut s)=setup(100,1);
        let revision=s.catalog_version().unwrap();
        s.reserve(&proposal("terminal-expiry",80),revision,now()).unwrap();
        assert_eq!(s.expire_unlaunched(now()+951).unwrap(),1);
        let before_job=s.job("terminal-expiry").unwrap();
        let before_events=s.event_log(Some("terminal-expiry")).unwrap();
        let before_view=serde_json::to_value(s.resume_view("terminal-expiry").unwrap()).unwrap();
        let result=s.finalize("terminal-expiry",outcome,now()+952);
        let refused=result.is_err();
        let result_json=match result {
            Ok(value)=>serde_json::json!({"ok":value}),
            Err(error)=>serde_json::json!({"error":error.to_string()}),
        };
        let after_job=s.job("terminal-expiry").unwrap();
        let after_events=s.event_log(Some("terminal-expiry")).unwrap();
        let after_view=match s.resume_view("terminal-expiry") {
            Ok(view)=>serde_json::json!({"ok":view}),
            Err(error)=>serde_json::json!({"error":error.to_string()}),
        };
        let unchanged=before_job==after_job && before_events==after_events
            && after_view.get("ok")==Some(&before_view);
        let repeated_expiry=s.expire_unlaunched(now()+953).unwrap();
        let available=balance(&mut s).available;
        valid &= refused && unchanged && repeated_expiry==0 && available==100;
        histories.push(serde_json::json!({"requested_outcome":outcome,
            "before_job":before_job,"before_events":before_events,"before_view":before_view,
            "finalize_result":result_json,"after_job":after_job,"after_events":after_events,
            "after_view":after_view,"unchanged":unchanged,"available":available,
            "repeat_expire_count":repeated_expiry}));
    }
    // Positive neighbor: a still-reserved job can explicitly cancel as before.
    let (_dir,_path,mut s)=setup(100,1);
    let revision=s.catalog_version().unwrap();
    s.reserve(&proposal("valid-cancel",80),revision,now()).unwrap();
    assert_eq!(s.finalize("valid-cancel","cancelled",now()).unwrap(),"CLOSED");
    assert_eq!(s.finalize("valid-cancel","cancelled",now()).unwrap(),"CLOSED_REPLAY");
    assert_eq!(balance(&mut s).available,100);
    let evidence=serde_json::json!({"parent_source":"9fb8a525c32b56b9191d3f33df9925939636dc9a",
        "histories":histories,"positive_cancel":s.job("valid-cancel").unwrap(),
        "positive_view":s.resume_view("valid-cancel").unwrap()});
    if let Some(root)=std::env::var_os("ASES_EXPIRY_EVIDENCE_DIR") {
        let root=PathBuf::from(root);
        std::fs::create_dir_all(&root).unwrap();
        std::fs::write(root.join("expiry-histories.json"),serde_json::to_vec_pretty(&evidence).unwrap()).unwrap();
    }
    println!("{}",serde_json::to_string(&evidence).unwrap());
    assert!(valid,"expired state was rewritten, or finalization changed its retained history/view");
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
    expensive.price_currency=Some("USD".into());
    s.register_meter(&expensive).unwrap();
    let mut p=proposal("cash",20);
    p.paid_spend_cap_currency=Some("USD".into());
    assert!(!s.quote(&p,now()).unwrap().eligible);
    assert_error_contains(s.reserve(&p,s.catalog_version().unwrap(),now()),"spend cap");
    p.paid_spend_cap_micros=Some(19999);
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
    let (_d,path,s)=setup(100,2);
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
    assert_eq!(s.catalog_version().unwrap(),3);
}


#[test]
fn accounts_have_explicit_provenance_and_project_grants() {
    let (_d,_p,mut s)=setup(100,2);
    assert_eq!(s.accounts().unwrap().len(),1);
    let acct=s.account("acct-a").unwrap();
    assert_eq!(acct.registration_status,"verified");
    assert!(acct.fresh(now()));
    let mut p=proposal("project-b",10);
    p.project_id="project-b".into();
    assert_error_contains(s.reserve(&p,s.catalog_version().unwrap(),now()),"no explicit entitlement grant");
    p.project_id="project-a".into();
    assert!(s.quote(&p,now()).unwrap().eligible);
}
#[test]
fn account_reporting_is_not_credential_verification() {
    let (_d,_p,mut s)=setup(100,2);
    let mut account=s.account("acct-a").unwrap();
    account.registration_status="reported".into();
    account.credential_status="untested".into();
    account.entitlement_status="unknown".into();
    s.register_account(&account).unwrap();
    assert_error_contains(s.reserve(&proposal("unverified",10),s.catalog_version().unwrap(),now()),
                         "account entitlement unverified");
    account.registration_status="verified".into();
    account.credential_status="working".into();
    account.entitlement_status="active".into();
    s.register_account(&account).unwrap();
    assert!(s.quote(&proposal("verified",10),now()).unwrap().eligible);
}
#[test]
fn account_identity_is_immutable_without_new_id() {
    let (_d,_p,mut s)=setup(100,2);
    let mut account=s.account("acct-a").unwrap();
    account.provider="other-provider".into();
    assert_error_contains(s.register_account(&account),"cannot silently change");
    assert_eq!(s.account("acct-a").unwrap().provider,"github");
}
#[test]
fn dormant_or_expired_account_does_not_become_a_free_allowance() {
    let (_d,_p,mut s)=setup(100,2);
    let mut account=s.account("acct-a").unwrap();
    account.observed_at=now()-7200;
    s.register_account(&account).unwrap();
    assert!(!s.quote(&proposal("expired-account",10),now()).unwrap().eligible);
    account.observed_at=now();
    account.entitlement_status="exhausted".into();
    s.register_account(&account).unwrap();
    assert!(!s.quote(&proposal("exhausted-account",10),now()).unwrap().eligible);
}
fn sample_catalog(models:&[&str])->CatalogImport {
    CatalogImport {
        provider:"opencode-zen".into(),
        source_url:"https://opencode.ai/zen/v1/models".into(),
        retrieved_at:now(),
        payload:serde_json::json!({"object":"list",
            "data":models.iter().map(|id|serde_json::json!({"id":id,"cost":"unknown"}))
                .collect::<Vec<_>>()})
    }
}
#[test]
fn passive_catalog_has_versioned_diff_and_does_not_imply_account_access() {
    let (_d,_p,mut s)=setup(100,2);
    let initial=s.catalog_version().unwrap();
    let c=sample_catalog(&["alpha","beta"]);
    let first=s.import_catalog(&c).unwrap();
    assert!(first.changed);
    assert_eq!(first.added_ids,vec!["alpha","beta"]);
    assert_eq!(first.catalog_version,initial+1);
    let second=s.import_catalog(&c).unwrap();
    assert!(!second.changed);
    assert_eq!(second.catalog_version,initial+1);
    let more=s.import_catalog(&sample_catalog(&["beta","gamma"])).unwrap();
    assert_eq!(more.added_ids,vec!["gamma"]);
    assert_eq!(more.removed_ids,vec!["alpha"]);
    assert!(s.catalog_states(now(),3600).unwrap()[0]["fresh"].as_bool().unwrap());
    assert_eq!(s.catalog_states(now(),3600).unwrap()[0]["catalog_presence_not_account_access"],true);
    assert_eq!(s.catalog_payload("opencode-zen").unwrap()["data"].as_array().unwrap().len(),2);
}
#[test]
fn catalog_failure_preserves_last_known_models_and_reports_stale() {
    let (_d,_p,mut s)=setup(100,2);
    s.import_catalog(&sample_catalog(&["still-known"])).unwrap();
    s.catalog_failure("opencode-zen","timeout",now()).unwrap();
    assert_eq!(s.catalog_payload("opencode-zen").unwrap()["data"][0]["id"],"still-known");
    let state=s.catalog_states(now()+10000,60).unwrap();
    assert_eq!(state[0]["fresh"],false);
    assert_eq!(state[0]["last_error"],"timeout");
    assert_eq!(state[0]["digest"].as_str().unwrap().len(),64);
}
#[test]
fn catalog_input_is_qualified_and_rejects_invalid_neighbors() {
    let (_d,_p,mut s)=setup(100,2);
    let mut c=sample_catalog(&["valid"]);
    assert!(s.import_catalog(&c).is_ok());
    c.source_url="http://insecure.example/models".into();
    assert_error_contains(s.import_catalog(&c),"HTTPS");
    c.source_url="https://opencode.ai/zen/v1/models".into();
    c.payload=serde_json::json!({"data":[{"id":"same"},{"id":"same"}]});
    assert_error_contains(s.import_catalog(&c),"duplicate");
    c.payload=serde_json::json!({"data":[{"price":0}]});
    assert_error_contains(s.import_catalog(&c),"without identifier");
    c.payload=serde_json::json!({"not_a_model_list":[]});
    assert_error_contains(s.import_catalog(&c),"requires");
}
#[test]
fn model_catalog_change_invalidates_inflight_resource_acknowledgement() {
    let (_d,_p,mut s)=setup(100,2);
    let revision=s.catalog_version().unwrap();
    s.reserve(&proposal("catalog-drift",40),revision,now()).unwrap();
    s.import_catalog(&sample_catalog(&["model-new"])).unwrap();
    assert_error_contains(s.acknowledge("catalog-drift","ack",revision,now()),"catalog changed");
}
#[test]
fn manual_attribution_is_append_only_and_cannot_change_financial_amounts() {
    let (_d,_p,mut s)=setup(100,2);
    running(&mut s,&proposal("annotation",30));
    let t=now();
    s.observe_usage("obs",Some("annotation"),"core",20,t,"provider").unwrap();
    let before=balance(&mut s).available;
    s.annotate("note-1","obs:obs","agent-a","time split due to setup, not verified provider outage",t).unwrap();
    assert_eq!(balance(&mut s).available,before);
    let events=s.event_log(None).unwrap();
    assert_eq!(events.last().unwrap()["kind"],"MANUAL_INTERPRETATION");
    assert_eq!(events.last().unwrap()["payload"]["authority_not_authenticated"],true);
    assert_error_contains(s.annotate("bad","missing","agent-a","guess",t),"unknown source");
}


#[test]
fn billing_period_must_cover_estimated_run_and_valid_neighbor_passes() {
    let (_d,_p,mut s)=setup(100,2);
    let current=now();
    let mut m=meter("core",100);
    m.period_start=Some(current-60);
    m.period_end=Some(current+60*60);
    s.register_meter(&m).unwrap();
    assert!(s.quote(&proposal("within",10),current).unwrap().eligible);
    m.period_end=Some(current+20*60);
    s.register_meter(&m).unwrap();
    assert!(!s.quote(&proposal("crosses-reset",10),current).unwrap().eligible);
    assert_error_contains(s.reserve(&proposal("crosses-reset",10),s.catalog_version().unwrap(),current),"split reservation");
    m.period_start=Some(current+1);
    m.period_end=Some(current+10000);
    s.register_meter(&m).unwrap();
    assert!(!s.quote(&proposal("future-period",10),current).unwrap().eligible);
    m.period_start=Some(current-60);
    m.period_end=Some(current+2700);
    s.register_meter(&m).unwrap();
    assert!(s.quote(&proposal("exact-end",10),current).unwrap().eligible);
}
#[test]
fn multi_meter_failure_is_atomic_and_valid_neighbor_is_admitted() {
    let (_d,_p,mut s)=setup(100,3);
    let mut storage=meter("storage",20);
    storage.unit="GB_hours".into();
    s.register_meter(&storage).unwrap();
    let mut rejected=proposal("multi-rejected",50);
    rejected.claims.push(Claim{meter_id:"storage".into(),amount:21});
    let rev=s.catalog_version().unwrap();
    assert_error_contains(s.reserve(&rejected,rev,now()),"insufficient storage");
    assert_eq!(balance(&mut s).available,100);
    assert_eq!(s.balances(now()).unwrap().into_iter().find(|b|b.meter_id=="storage").unwrap().available,20);
    let mut accepted=proposal("multi-valid",50);
    accepted.claims.push(Claim{meter_id:"storage".into(),amount:20});
    reserve(&mut s,&accepted);
    assert_eq!(balance(&mut s).available,50);
    assert_eq!(s.balances(now()).unwrap().into_iter().find(|b|b.meter_id=="storage").unwrap().available,0);
    s.finalize("multi-valid","cancelled",now()).unwrap();
    assert_eq!(balance(&mut s).available,100);
}
#[test]
fn malformed_billing_window_rejected_with_valid_neighbor() {
    let (_d,_p,mut s)=setup(100,2);
    let mut m=meter("bad-window",100);
    m.period_start=Some(120);
    m.period_end=Some(119);
    assert_error_contains(s.register_meter(&m),"invalid billing period");
    m.period_end=Some(121);
    assert!(s.register_meter(&m).is_ok());
}
