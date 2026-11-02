//! Trusted local command adapter; NOT a public network API or external launcher.
use ases_resource_control::{archive::verify_archive, now, Environment, Meter, Proposal, Store};
use ases_resource_control::catalog::{Account, CatalogImport};
use serde::Deserialize;
use serde_json::{json, Value};
use std::io::Read;
use std::path::Path;

#[derive(Deserialize)]
#[serde(tag="op",rename_all="snake_case",deny_unknown_fields)]
enum Request {
    RegisterAccount { account: Account },
    Accounts,
    RegisterMeter { meter: Meter },
    ImportCatalog { catalog: CatalogImport },
    CatalogStates { ttl_seconds: i64 },
    CatalogModels { provider: String },
    CatalogFailure { provider: String, description: String },
    Annotate { id:String, related_event_id:String, reported_actor:String, reason:String },
    RegisterEnvironment { environment: Environment },
    Snapshot,
    Quote { proposal: Proposal },
    Reserve { proposal: Proposal, expected_catalog: i64 },
    Acknowledge { job_id:String, acknowledgement_id:String, expected_catalog:i64 },
    LaunchMock { job_id:String, launch_id:String },
    ObserveUsage { event_id:String, job_id:Option<String>, meter_id:String, amount:u64,
                   occurred_at:Option<i64>, source:String },
    ProviderReport { event_id:String, meter_id:String, total_used:u64,
                     complete_through:Option<i64>, observed_at:Option<i64>, source:String },
    ObserveLifecycle { event_id:String, job_id:String, kind:String, subject:String,
                       occurred_at:Option<i64>, details:Option<Value> },
    Timeline { job_id:String },
    Finalize { job_id:String, outcome:String },
    Expire,
    Job { job_id:String },
    Events { job_id:Option<String> },
    Reconcile,
    ExportSession { job_id:String, output_path:String },
    VerifyArchive { path:String, sha256:String, expected_records:usize },
}

fn main() {
    if let Err(e)=run() {
        eprintln!("{}",json!({"ok":false,"error":e.to_string()}));
        std::process::exit(1);
    }
}
fn run()->Result<(),Box<dyn std::error::Error>> {
    let mut args=std::env::args().skip(1);
    let db=args.next().ok_or("usage: ases-resource-control DB_PATH init | request JSON_OR_STDIN_DASH")?;
    let operation=args.next().ok_or("missing operation")?;
    let mut store=Store::open(&db)?;
    if operation=="init" {
        println!("{}",json!({"ok":true,"initialized":db,"catalog_version":store.catalog_version()?}));
        return Ok(());
    }
    if operation!="request" {return Err("only init or request supported".into());}
    let mut text=args.next().ok_or("request JSON required")?;
    if text=="-" {
        text.clear();
        std::io::stdin().read_to_string(&mut text)?;
    }
    let request:Request=serde_json::from_str(&text)?;
    let time=now(); // Client cannot select the clock used for admission/authorization.
    let result:Value=match request {
        Request::RegisterAccount{account}=>json!({"catalog_version":store.register_account(&account)?}),
        Request::Accounts=>json!({"accounts":store.accounts()?}),
        Request::RegisterMeter{meter}=>json!({"catalog_version":store.register_meter(&meter)?}),
        Request::ImportCatalog{catalog}=>serde_json::to_value(store.import_catalog(&catalog)?)?,
        Request::CatalogStates{ttl_seconds}=>json!({"catalogs":store.catalog_states(time,ttl_seconds)?}),
        Request::CatalogModels{provider}=>store.catalog_payload(&provider)?,
        Request::CatalogFailure{provider,description}=>{
            store.catalog_failure(&provider,&description,time)?;
            json!({"catalog_preserved":true})
        },
        Request::Annotate{id,related_event_id,reported_actor,reason}=>{
            store.annotate(&id,&related_event_id,&reported_actor,&reason,time)?;
            json!({"annotation":"RECORDED","authority":"UNVERIFIED","numeric_accounting":"UNCHANGED"})
        },
        Request::RegisterEnvironment{environment}=>json!({"catalog_version":store.register_environment(&environment)?}),
        Request::Snapshot=>json!({"catalog_version":store.catalog_version()?,"balances":store.balances(time)?}),
        Request::Quote{proposal}=>serde_json::to_value(store.quote(&proposal,time)?)?,
        Request::Reserve{proposal,expected_catalog}=>serde_json::to_value(store.reserve(&proposal,expected_catalog,time)?)?,
        Request::Acknowledge{job_id,acknowledgement_id,expected_catalog}=>json!({
            "authorization":store.acknowledge(&job_id,&acknowledgement_id,expected_catalog,time)?
        }),
        Request::LaunchMock{job_id,launch_id}=>json!({
            "execution":store.launch_mock(&job_id,&launch_id,time)?
        }),
        Request::ObserveUsage{event_id,job_id,meter_id,amount,occurred_at,source}=>json!({
            "observation":store.observe_usage(&event_id,job_id.as_deref(),&meter_id,amount,
                                               occurred_at.unwrap_or(time),&source)?
        }),
        Request::ProviderReport{event_id,meter_id,total_used,complete_through,observed_at,source}=>json!({
            "provider_observation":store.provider_report(&event_id,&meter_id,total_used,
                                                         complete_through,observed_at.unwrap_or(time),&source)?
        }),
        Request::ObserveLifecycle{event_id,job_id,kind,subject,occurred_at,details}=>json!({
            "lifecycle":store.observe_lifecycle(&event_id,&job_id,&kind,
                 occurred_at.unwrap_or(time),&subject,details.unwrap_or(json!({})))?
        }),
        Request::Timeline{job_id}=>store.timeline(&job_id)?,
        Request::Finalize{job_id,outcome}=>json!({"finalization":store.finalize(&job_id,&outcome,time)?}),
        Request::Expire=>json!({"expired":store.expire_unlaunched(time)?}),
        Request::Job{job_id}=>store.job(&job_id)?,
        Request::Events{job_id}=>json!({"events":store.event_log(job_id.as_deref())?}),
        Request::Reconcile=>store.reconcile(time)?,
        Request::ExportSession{job_id,output_path}=>serde_json::to_value(store.export_session(&job_id,Path::new(&output_path))?)?,
        Request::VerifyArchive{path,sha256,expected_records}=>json!({
            "verified_records":verify_archive(Path::new(&path),&sha256,expected_records)?,
            "scope":"local_readback_only"
        }),
    };
    println!("{}",serde_json::to_string(&json!({"ok":true,"result":result}))?);
    Ok(())
}
