use ases_resource_control::{access::{Grant,Policy}, now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::catalog::Account;
use serde_json::json;
use std::fs;
use std::io::{Read,Write};
use std::os::unix::net::UnixStream;
use std::path::Path;
use std::process::{Command,Stdio};
use std::thread;
use std::time::Duration;

fn policy(uid:u32)->Policy {
    Policy{administrators:vec![],callers:vec![Grant{
        uid,role:"orchestrator".into(),accounts:vec!["acct-a".into()],
        projects:vec!["project-a".into()
    ]}]}
}
fn bootstrap(db:&Path){
    let mut s=Store::open(db).unwrap();
    s.register_account(&Account{
        id:"acct-a".into(),provider:"github".into(),payer_ref:"payer-a".into(),
        registration_status:"verified".into(),credential_status:"working".into(),
        entitlement_status:"active".into(),allowed_projects:vec!["project-a".into()],
        source:"synthetic".into(),observed_at:now(),ttl_seconds:3600,
    }).unwrap();
    s.register_meter(&Meter{
        id:"core".into(),account:"acct-a".into(),provider:"github".into(),
        product:"codespaces".into(),period:"2026-11".into(),unit:"core_minutes".into(),
        limit:100,guard:0,observed_at:now(),ttl_seconds:3600,
        source:"synthetic".into(),price_per_unit_micros:0,chargeable:false
    }).unwrap();
    s.register_environment(&Environment{
        id:"codespace".into(),account:"acct-a".into(),provider:"github".into(),
        max_parallel:2,observed_at:now(),ttl_seconds:3600,source:"synthetic".into(),
    }).unwrap();
}
fn p(id:&str)->Proposal{
    Proposal{job_id:id.into(),account_id:"acct-a".into(),project_id:"project-a".into(),
        environment_id:"codespace".into(),estimated_wall_seconds:60,
        claims:vec![Claim{meter_id:"core".into(),amount:10}],
        paid_spend_cap_micros:None,forecast_context:None}
}
#[test]
fn role_and_project_scope_are_enforced_on_actual_controller_state(){
    let d=tempfile::tempdir().unwrap();
    let db=d.path().join("state.db");
    bootstrap(&db);
    let mut s=Store::open(&db).unwrap();
    let uid=1001;
    let policy=policy(uid);
    assert!(policy.authorize(uid,&json!({"op":"quote","proposal":p("a")}),&s).is_ok());
    assert!(policy.authorize(uid,&json!({"op":"register_meter"}),&s).is_err());
    assert!(policy.authorize(uid,&json!({"op":"provider_report"}),&s).is_err());
    assert!(policy.authorize(7777,&json!({"op":"snapshot"}),&s).is_err());
    let mut changed=p("b");changed.project_id="other-project".into();
    assert!(policy.authorize(uid,&json!({"op":"reserve","proposal":changed}),&s).is_err());
    assert!(policy.authorize(uid,&json!({"op":"events","job_id":null}),&s).is_err());
    let rev=s.catalog_version().unwrap();
    s.reserve(&p("job-owned"),rev,now()).unwrap();
    assert!(policy.authorize(uid,&json!({"op":"launch_mock","job_id":"job-owned"}),&s).is_ok());
    assert!(policy.authorize(uid,&json!({"op":"job","job_id":"unrelated"}),&s).is_err());
}
#[test]
fn administrative_privileges_are_explicit_and_unscoped(){
    let d=tempfile::tempdir().unwrap();
    let db=d.path().join("state.db");
    bootstrap(&db);
    let s=Store::open(&db).unwrap();
    let p=Policy{administrators:vec![555],callers:vec![]};
    assert_eq!(p.authorize(555,&json!({"op":"register_account"}),&s).unwrap().role,"admin");
    assert!(p.authorize(556,&json!({"op":"snapshot"}),&s).is_err());
}
#[test]
fn unix_gateway_refuses_admin_operations_from_orchestrator_uid(){
    let d=tempfile::tempdir().unwrap();
    let db=d.path().join("state.db");
    let socket=d.path().join("gate.sock");
    let config=d.path().join("policy.json");
    bootstrap(&db);
    // The policy is administered out of band. This test deliberately grants
    // the test process only orchestrator, not admin, capability.
    let uid=unsafe { libc::geteuid() };
    fs::write(&config,serde_json::to_vec(&policy(uid)).unwrap()).unwrap();
    let gateway=env!("CARGO_BIN_EXE_resource-gateway");
    let controller=env!("CARGO_BIN_EXE_ases-resource-control");
    let mut child=Command::new(gateway)
        .arg(&db).arg(&socket).arg(&config).arg(controller)
        .stdout(Stdio::null()).stderr(Stdio::piped()).spawn().unwrap();
    for _ in 0..100{
        if socket.exists(){break;}
        thread::sleep(Duration::from_millis(15));
    }
    assert!(socket.exists(),"gateway failed to create Unix socket");
    let send=|message:serde_json::Value|{
        let mut stream=UnixStream::connect(&socket).unwrap();
        stream.write_all(serde_json::to_string(&message).unwrap().as_bytes()).unwrap();
        stream.shutdown(std::net::Shutdown::Write).unwrap();
        let mut out=String::new();stream.read_to_string(&mut out).unwrap();
        serde_json::from_str::<serde_json::Value>(&out).unwrap()
    };
    let denial=send(json!({"op":"register_meter","meter":{"id":"unauthorized"}}));
    assert_eq!(denial["ok"],false);
    assert!(denial["error"].as_str().unwrap().contains("prohibited"));
    let allowed=send(json!({"op":"quote","proposal":p("socket-job")}));
    assert_eq!(allowed["ok"],true);
    assert_eq!(allowed["result"]["eligible"],true);
    let snapshot=send(json!({"op":"snapshot"}));
    assert_eq!(snapshot["ok"],true);
    assert_eq!(snapshot["result"]["balances"].as_array().unwrap().len(),1);
    child.kill().unwrap();
    child.wait().unwrap();
}
