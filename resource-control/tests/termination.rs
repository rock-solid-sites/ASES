use ases_resource_control::catalog::Account;
use ases_resource_control::{now, AdvisoryNextStep, BeginLaunchResult, Claim, Environment,
    LaunchExitObservation, LaunchObservation, Meter, ProcessExitStatus, ProcessIdentity,
    RecordLaunchExitResult, Store};
use rusqlite::Connection;
use std::path::{Path, PathBuf};

fn setup(path:&Path)->(Store,i64){
    let mut store=Store::open(path).unwrap();
    store.register_account(&Account{id:"acct-exit".into(),provider:"local".into(),payer_ref:"payer".into(),
        registration_status:"verified".into(),credential_status:"working".into(),entitlement_status:"active".into(),
        allowed_projects:vec!["project-exit".into()],source:"synthetic".into(),observed_at:now(),ttl_seconds:3600}).unwrap();
    store.register_meter(&Meter{id:"meter-exit".into(),account:"acct-exit".into(),provider:"local".into(),product:"local".into(),
        period:"2026-11".into(),unit:"units".into(),limit:100,guard:0,observed_at:now(),ttl_seconds:3600,source:"synthetic".into(),
        period_start:None,period_end:None,price_per_unit_micros:0,price_currency:None,chargeable:false}).unwrap();
    store.register_environment(&Environment{id:"env-exit".into(),account:"acct-exit".into(),provider:"local".into(),
        max_parallel:1,observed_at:now(),ttl_seconds:3600,source:"synthetic".into()}).unwrap();
    let revision=store.catalog_version().unwrap();
    (store,revision)
}

fn start(store:&mut Store,revision:i64,job:&str)->ProcessIdentity{
    let proposal=ases_resource_control::Proposal{job_id:job.into(),account_id:"acct-exit".into(),project_id:"project-exit".into(),
        environment_id:"env-exit".into(),estimated_wall_seconds:60,claims:vec![Claim{meter_id:"meter-exit".into(),amount:60}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None};
    store.reserve(&proposal,revision,now()).unwrap();
    store.acknowledge(job,&format!("ack-{job}"),revision,now()).unwrap();
    assert!(matches!(store.begin_launch(job,&format!("launch-{job}"),revision,now()).unwrap(),
        BeginLaunchResult::DispatchGranted(_)));
    let process=ProcessIdentity{pid:4242,start_token:format!("owned-{job}")};
    store.observe_launch(job,&format!("launch-{job}"),&LaunchObservation::Started{process:process.clone()},now()).unwrap();
    process
}

fn events(store:&Store,job:&str)->usize{store.event_log(Some(job)).unwrap().len()}
fn assert_error<T>(result:ases_resource_control::Result<T>,text:&str){
    match result{Ok(_)=>panic!("expected error containing {text}"),Err(e)=>assert!(e.to_string().contains(text),"unexpected error: {e}")}
}

#[test]
fn exact_wait_evidence_holds_capacity_until_finalization_and_replays_after_reopen(){
    let dir=tempfile::tempdir().unwrap();
    let path=dir.path().join("termination.sqlite");
    let (mut store,revision)=setup(&path);
    let process=start(&mut store,revision,"job-exit");
    let launch="launch-job-exit";
    let before=events(&store,"job-exit");
    assert_error(store.finalize("job-exit","completed",now()),"observed process exit");
    assert_eq!(events(&store,"job-exit"),before);
    let contender=ases_resource_control::Proposal{job_id:"contender".into(),account_id:"acct-exit".into(),project_id:"project-exit".into(),
        environment_id:"env-exit".into(),estimated_wall_seconds:60,claims:vec![Claim{meter_id:"meter-exit".into(),amount:10}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None};
    assert_error(store.reserve(&contender,revision,now()),"concurrency exhausted");

    let exit=LaunchExitObservation{process:process.clone(),status:ProcessExitStatus::Code{code:7}};
    assert_error(store.observe_launch_exit("job-exit","wrong-launch",&exit,now()),"durable launch intent");
    let wrong=LaunchExitObservation{process:ProcessIdentity{pid:process.pid+1,start_token:process.start_token.clone()},status:exit.status.clone()};
    assert_error(store.observe_launch_exit("job-exit",launch,&wrong,now()),"process identity conflicts");
    for status in [ProcessExitStatus::Code{code:-1},ProcessExitStatus::Code{code:256},
        ProcessExitStatus::Signal{signal:0},ProcessExitStatus::Signal{signal:65}] {
        assert_error(store.observe_launch_exit("job-exit",launch,&LaunchExitObservation{process:process.clone(),status},now()),"must be");
    }
    assert_eq!(events(&store,"job-exit"),before,"invalid evidence never appends");

    assert_eq!(store.observe_launch_exit("job-exit",launch,&exit,now()).unwrap(),RecordLaunchExitResult::Recorded);
    assert_eq!(store.job("job-exit").unwrap()["state"],"RUNNING");
    assert_error(store.reserve(&contender,revision,now()),"concurrency exhausted");
    let view=store.resume_view("job-exit").unwrap();
    assert_eq!(view.advisory_next_step,AdvisoryNextStep::FinalizeObservedExit);
    assert_eq!(view.evidence.outcome.as_ref().unwrap().kind,"LAUNCH_EXIT_OBSERVED");
    assert!(serde_json::to_vec(&view).unwrap().len()<=2048);
    drop(store);

    let (mut reopened,_)=setup_without_reinitializing(&path);
    assert_eq!(reopened.observe_launch_exit("job-exit",launch,&exit,now()).unwrap(),RecordLaunchExitResult::Replay);
    assert_eq!(events(&reopened,"job-exit"),before+1);
    assert_eq!(reopened.finalize("job-exit","completed",now()).unwrap(),"CLOSED");
    assert_eq!(reopened.observe_launch_exit("job-exit",launch,&exit,now()).unwrap(),RecordLaunchExitResult::Replay);
    let conflict=LaunchExitObservation{process:process.clone(),status:ProcessExitStatus::Code{code:8}};
    assert_error(reopened.observe_launch_exit("job-exit",launch,&conflict,now()),"conflicts with prior evidence");
    assert_eq!(reopened.finalize("job-exit","completed",now()).unwrap(),"CLOSED_REPLAY");
    assert_eq!(reopened.reserve(&contender,revision,now()).unwrap().status,"RESERVED");
}

fn setup_without_reinitializing(path:&Path)->(Store,i64){
    let store=Store::open(path).unwrap();
    let revision=store.catalog_version().unwrap();
    (store,revision)
}

#[test]
fn unsupported_mixed_profile_cannot_finalize_even_with_exit_evidence(){
    let dir=tempfile::tempdir().unwrap();
    let path:PathBuf=dir.path().join("mixed.sqlite");
    let (mut store,revision)=setup(&path);
    let process=start(&mut store,revision,"mixed-job");
    let launch="launch-mixed-job";
    let exit=LaunchExitObservation{process,status:ProcessExitStatus::Signal{signal:15}};
    store.observe_launch_exit("mixed-job",launch,&exit,now()).unwrap();
    let conn=Connection::open(&path).unwrap();
    conn.execute("INSERT INTO events(id,job_id,kind,at,payload) VALUES (?1,?2,'MOCK_LAUNCH',?3,?4)",
        ("injected-mock".to_string(),"mixed-job",now(),format!(r#"{{"launch_id":"{launch}","external_provider_launch":false}}"#))).unwrap();
    let before=events(&store,"mixed-job");
    assert_error(store.finalize("mixed-job","completed",now()),"mixed launch profile");
    assert_eq!(store.job("mixed-job").unwrap()["state"],"RUNNING");
    assert_eq!(events(&store,"mixed-job"),before,"refused finalization does not append");
    assert!(store.resume_view("mixed-job").is_err(),"projection also refuses mixed profile evidence");
}

#[test]
fn exit_observation_cannot_replace_pending_outcome_or_mock_profile(){
    let dir=tempfile::tempdir().unwrap();
    let path=dir.path().join("profiles.sqlite");
    let (mut store,revision)=setup(&path);
    let pending=ases_resource_control::Proposal{job_id:"pending-job".into(),account_id:"acct-exit".into(),project_id:"project-exit".into(),
        environment_id:"env-exit".into(),estimated_wall_seconds:60,claims:vec![Claim{meter_id:"meter-exit".into(),amount:20}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None};
    store.reserve(&pending,revision,now()).unwrap();
    store.acknowledge("pending-job","ack-pending",revision,now()).unwrap();
    store.begin_launch("pending-job","launch-pending",revision,now()).unwrap();
    let fake=LaunchExitObservation{process:ProcessIdentity{pid:44,start_token:"unobserved".into()},status:ProcessExitStatus::Code{code:0}};
    assert_error(store.observe_launch_exit("pending-job","launch-pending",&fake,now()),"started process evidence is missing");
    assert_error(store.finalize("pending-job","cancelled",now()),"outcome unknown");

    let mock_path=dir.path().join("mock.sqlite");
    let (mut mock_store,mock_revision)=setup(&mock_path);
    let mock=ases_resource_control::Proposal{job_id:"mock-job".into(),account_id:"acct-exit".into(),project_id:"project-exit".into(),
        environment_id:"env-exit".into(),estimated_wall_seconds:60,claims:vec![Claim{meter_id:"meter-exit".into(),amount:20}],
        paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None};
    mock_store.reserve(&mock,mock_revision,now()).unwrap();
    mock_store.acknowledge("mock-job","ack-mock",mock_revision,now()).unwrap();
    mock_store.launch_mock("mock-job","launch-mock",now()).unwrap();
    assert_error(mock_store.observe_launch_exit("mock-job","launch-mock",&fake,now()),"durable launch intent");
    assert_eq!(mock_store.finalize("mock-job","completed",now()).unwrap(),"CLOSED","mock behavior remains unchanged");
}
