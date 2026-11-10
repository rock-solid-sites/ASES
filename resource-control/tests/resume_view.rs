use ases_resource_control::{
    now, AdvisoryNextStep, BeginLaunchResult, Claim, Environment, LaunchObservation, Meter,
    PresentLiveness, ProcessIdentity, Proposal, RecordedJobState, ResumeLaunchProfile,
    Store,
};
use ases_resource_control::catalog::Account;
use rusqlite::Connection;
use serde_json::json;
use sha2::{Digest, Sha256};
use std::path::Path;

fn account(id:&str,project:&str)->Account{
    Account{id:id.into(),provider:"local".into(),payer_ref:"local-test".into(),
        registration_status:"verified".into(),credential_status:"working".into(),
        entitlement_status:"active".into(),allowed_projects:vec![project.into()],
        source:"synthetic-resume-test".into(),observed_at:now(),ttl_seconds:3600}
}
fn environment(id:&str,account_id:&str)->Environment{
    Environment{id:id.into(),account:account_id.into(),provider:"local".into(),max_parallel:2,
        observed_at:now(),ttl_seconds:3600,source:"synthetic-resume-test".into()}
}
fn meter(account_id:&str)->Meter{
    Meter{id:"meter-resume".into(),account:account_id.into(),provider:"local".into(),
        product:"test".into(),period:"2026-11".into(),unit:"work".into(),limit:100,
        guard:0,observed_at:now(),ttl_seconds:3600,source:"synthetic-resume-test".into(),
        period_start:None,period_end:None,price_per_unit_micros:0,price_currency:None,chargeable:false}
}
fn proposal(job:&str,account_id:&str,project:&str,env:&str)->Proposal{
    Proposal{job_id:job.into(),account_id:account_id.into(),project_id:project.into(),
        environment_id:env.into(),estimated_wall_seconds:120,
        claims:vec![Claim{meter_id:"meter-resume".into(),amount:30}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None}
}
fn setup(dir:&Path)->(Store,i64){
    let mut store=Store::open(dir.join("resume.sqlite")).unwrap();
    store.register_account(&account("acct-resume","project-resume")).unwrap();
    store.register_meter(&meter("acct-resume")).unwrap();
    store.register_environment(&environment("env-resume","acct-resume")).unwrap();
    let revision=store.catalog_version().unwrap();
    (store,revision)
}
fn reserve_authorize(store:&mut Store,p:&Proposal,revision:i64){
    store.reserve(p,revision,now()).unwrap();
    store.acknowledge(&p.job_id,"ack-resume",revision,now()).unwrap();
}
fn start_intent(store:&mut Store,p:&Proposal,revision:i64,launch:&str){
    reserve_authorize(store,p,revision);
    assert!(matches!(store.begin_launch(&p.job_id,launch,revision,now()).unwrap(),
        BeginLaunchResult::DispatchGranted(_)));
}

#[test]
fn view_is_compact_typed_and_stale_catalog_is_advisory_only(){
    let dir=tempfile::tempdir().unwrap();
    let (mut store,revision)=setup(dir.path());
    let p=proposal("resume-auth","acct-resume","project-resume","env-resume");
    reserve_authorize(&mut store,&p,revision);
    let first=store.resume_view("resume-auth").unwrap();
    assert_eq!(first.state,RecordedJobState::Authorized);
    assert_eq!(first.profile,ResumeLaunchProfile::Unlaunched);
    assert_eq!(first.advisory_next_step,AdvisoryNextStep::BeginLaunch);
    assert_eq!(first.present_liveness,PresentLiveness::Unknown);
    assert!(first.evidence.launch.is_none() && first.evidence.outcome.is_none());
    let old_snapshot=serde_json::to_vec(&first).unwrap();

    let mut changed=environment("env-resume","acct-resume");
    changed.source="catalog-revision-changed".into();
    store.register_environment(&changed).unwrap();
    let stale=store.resume_view("resume-auth").unwrap();
    assert_eq!(stale.job_catalog_revision,revision);
    assert_eq!(stale.current_catalog_revision,revision+1);
    assert_eq!(stale.advisory_next_step,AdvisoryNextStep::ReconcileAdmission);
    assert_eq!(serde_json::from_slice::<serde_json::Value>(&old_snapshot).unwrap()["currentCatalogRevision"],revision);
    assert!(store.begin_launch("resume-auth","late-launch",first.job_catalog_revision,now()).is_err(),
        "old serialized view metadata cannot bypass begin_launch current checks");
    assert_eq!(store.job("resume-auth").unwrap()["state"],"AUTHORIZED");

    let view=store.resume_view("resume-auth").unwrap();
    let encoded=serde_json::to_vec(&view).unwrap();
    assert!(encoded.len()<=2048,"{} bytes",encoded.len());
    assert_eq!(view.job_id,"resume-auth");
    assert!(!String::from_utf8(encoded).unwrap().contains("forecast_context"));
}

#[test]
fn large_forecast_context_is_retained_but_never_projected(){
    let dir=tempfile::tempdir().unwrap();
    let (mut store,revision)=setup(dir.path());
    let mut p=proposal("large-context","acct-resume","project-resume","env-resume");
    p.forecast_context=Some(json!({"transcript":"x".repeat(256*1024)}));
    reserve_authorize(&mut store,&p,revision);
    let view=store.resume_view("large-context").unwrap();
    let bytes=serde_json::to_vec(&view).unwrap();
    assert!(bytes.len()<=2048,"compact projection is {} bytes",bytes.len());
    println!("retained forecast bytes: {}; compact projection bytes: {}",256*1024,bytes.len());
    assert!(!String::from_utf8(bytes).unwrap().contains("transcript"));
    let retained:usize=store.job("large-context").unwrap()["proposal"]["forecast_context"]["transcript"]
        .as_str().unwrap().len();
    assert_eq!(retained,256*1024,"original forecast evidence remains in the existing store");
}

#[test]
fn maximum_valid_identity_and_two_evidence_pointers_fit_under_two_kib(){
    let dir=tempfile::tempdir().unwrap();
    let account_id="a".repeat(160);
    let project_id="p".repeat(160);
    let env_id="e".repeat(160);
    let job_id="j".repeat(160);
    let launch_id="l".repeat(160);
    let mut store=Store::open(dir.path().join("max.sqlite")).unwrap();
    store.register_account(&account(&account_id,&project_id)).unwrap();
    store.register_meter(&meter(&account_id)).unwrap();
    store.register_environment(&environment(&env_id,&account_id)).unwrap();
    let revision=store.catalog_version().unwrap();
    let p=proposal(&job_id,&account_id,&project_id,&env_id);
    start_intent(&mut store,&p,revision,&launch_id);
    let started=LaunchObservation::Started{process:ProcessIdentity{pid:88,start_token:"test-start-token".into()}};
    store.observe_launch(&job_id,&launch_id,&started,now()).unwrap();
    store.finalize(&job_id,"completed",now()).unwrap();
    let view=store.resume_view(&job_id).unwrap();
    let bytes=serde_json::to_vec(&view).unwrap();
    assert!(bytes.len()<=2048,"max-ID terminal projection is {} bytes",bytes.len());
    println!("maximum-valid-ID compact resume view: {} bytes",bytes.len());
    assert_eq!(view.state,RecordedJobState::Closed);
    assert!(view.evidence.launch.is_some() && view.evidence.outcome.is_some());
}

#[test]
fn intent_mock_and_missing_evidence_are_not_conflated(){
    let dir=tempfile::tempdir().unwrap();
    let (mut store,revision)=setup(dir.path());
    let mock=proposal("resume-mock","acct-resume","project-resume","env-resume");
    reserve_authorize(&mut store,&mock,revision);
    store.launch_mock(&mock.job_id,"mock-launch",now()).unwrap();
    let mock_view=store.resume_view(&mock.job_id).unwrap();
    assert_eq!(mock_view.profile,ResumeLaunchProfile::Mock);
    assert_eq!(mock_view.state,RecordedJobState::Running);
    assert_eq!(mock_view.advisory_next_step,AdvisoryNextStep::ObserveMockLifecycle);
    assert_eq!(mock_view.present_liveness,PresentLiveness::Unknown);
    assert_eq!(mock_view.evidence.launch.as_ref().unwrap().kind,"MOCK_LAUNCH");

    let intent=proposal("resume-intent","acct-resume","project-resume","env-resume");
    start_intent(&mut store,&intent,revision,"intent-launch");
    let pending=store.resume_view(&intent.job_id).unwrap();
    assert_eq!(pending.profile,ResumeLaunchProfile::Intent);
    assert_eq!(pending.state,RecordedJobState::Launching);
    assert_eq!(pending.advisory_next_step,AdvisoryNextStep::ObserveOrReconcileLaunch);
    assert_eq!(pending.evidence.launch.as_ref().unwrap().kind,"LAUNCH_INTENT");

    let conn=Connection::open(dir.path().join("resume.sqlite")).unwrap();
    conn.execute("INSERT INTO events(id,job_id,kind,at,payload) VALUES (?1,?2,'MOCK_LAUNCH',?3,?4)",
        ("conflicting-mock".to_string(),intent.job_id.clone(),now(),
         r#"{"launch_id":"intent-launch","external_provider_launch":false}"#)).unwrap();
    assert!(store.resume_view(&intent.job_id).is_err(),"conflicting intent and mock evidence must refuse");
    conn.execute("DELETE FROM events WHERE id='conflicting-mock'",[]).unwrap();
    conn.execute("DELETE FROM events WHERE id=?1",[format!("launch-intent:{}",intent.job_id)]).unwrap();
    assert!(store.resume_view(&intent.job_id).is_err(),"missing intent evidence must refuse interpretation");
    conn.execute("DELETE FROM events WHERE id=?1",[format!("{}:launch:mock-launch",mock.job_id)]).unwrap();
    assert!(store.resume_view(&mock.job_id).is_err(),"missing mock evidence must refuse interpretation");
}

#[test]
fn terminal_and_expired_views_have_no_dispatch_advice_and_digest_exact_payload(){
    let dir=tempfile::tempdir().unwrap();
    let (mut store,revision)=setup(dir.path());
    let p=proposal("resume-finished","acct-resume","project-resume","env-resume");
    start_intent(&mut store,&p,revision,"finished-launch");
    let started=LaunchObservation::Started{process:ProcessIdentity{pid:77,start_token:"worker-token".into()}};
    store.observe_launch(&p.job_id,"finished-launch",&started,now()).unwrap();
    store.finalize(&p.job_id,"completed",now()).unwrap();
    let view=store.resume_view(&p.job_id).unwrap();
    assert_eq!(view.advisory_next_step,AdvisoryNextStep::NoNewDispatch);
    let pointer=view.evidence.outcome.unwrap();
    assert_eq!(pointer.kind,"FINALIZED");
    let raw:String=Connection::open(dir.path().join("resume.sqlite")).unwrap().query_row(
        "SELECT payload FROM events WHERE id=?1",[pointer.event_id.as_str()],|r|r.get(0)).unwrap();
    assert_eq!(pointer.payload_sha256,format!("{:x}",Sha256::digest(raw.as_bytes())));

    let conn=Connection::open(dir.path().join("resume.sqlite")).unwrap();
    conn.execute("UPDATE events SET payload=?1 WHERE id=?2",
        (r#"{"outcome":"failed"}"#,pointer.event_id.as_str())).unwrap();
    assert!(store.resume_view(&p.job_id).is_err(),"contradictory terminal evidence must refuse");
    conn.execute("DELETE FROM events WHERE id=?1",[pointer.event_id]).unwrap();
    assert!(store.resume_view(&p.job_id).is_err(),"missing outcome evidence must refuse");

    let expiring=proposal("resume-expired","acct-resume","project-resume","env-resume");
    store.reserve(&expiring,revision,now()).unwrap();
    assert_eq!(store.expire_unlaunched(now()+1000).unwrap(),1);
    let expired=store.resume_view(&expiring.job_id).unwrap();
    assert_eq!(expired.state,RecordedJobState::Expired);
    assert_eq!(expired.advisory_next_step,AdvisoryNextStep::NoNewDispatch);

    let unsupported=proposal("unsupported-unlaunched-terminal","acct-resume","project-resume","env-resume");
    store.reserve(&unsupported,revision,now()).unwrap();
    let conn=Connection::open(dir.path().join("resume.sqlite")).unwrap();
    conn.execute("UPDATE jobs SET state='CLOSED',outcome='completed' WHERE id=?1",[&unsupported.job_id]).unwrap();
    conn.execute("INSERT INTO events(id,job_id,kind,at,payload) VALUES (?1,?2,'FINALIZED',?3,?4)",
        (format!("{}:final:completed",unsupported.job_id),unsupported.job_id,now(),r#"{"outcome":"completed"}"#)).unwrap();
    assert!(store.resume_view("unsupported-unlaunched-terminal").is_err(),
        "matching terminal label cannot make unlaunched work completed");
}
