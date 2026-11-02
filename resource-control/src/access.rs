//! Least-privilege rules for a local Unix-socket gateway.
//! Caller identity must come from OS peer credentials, never the request JSON.
use crate::{Error, Result, Store};
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Grant {
    pub uid:u32,
    pub role:String,
    pub accounts:Vec<String>,
    pub projects:Vec<String>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Policy {
    pub administrators:Vec<u32>,
    pub callers:Vec<Grant>,
}
impl Policy {
    pub fn grant(&self,uid:u32)->Result<Grant>{
        if self.administrators.contains(&uid) {
            return Ok(Grant{uid,role:"admin".into(),accounts:vec![],projects:vec![]});
        }
        let grants:Vec<_>=self.callers.iter().filter(|g|g.uid==uid).collect();
        if grants.len()!=1 {return Err(Error::Invalid("caller UID not uniquely authorized".into()));}
        let g=grants[0];
        if !["orchestrator","collector","viewer"].contains(&g.role.as_str()) {
            return Err(Error::Invalid("unknown gateway role".into()));
        }
        Ok(g.clone())
    }
    pub fn authorize(&self,uid:u32,request:&Value,store:&Store)->Result<Grant>{
        let grant=self.grant(uid)?;
        if grant.role=="admin" {return Ok(grant);}
        let op=request.get("op").and_then(Value::as_str)
            .ok_or_else(||Error::Invalid("request missing op".into()))?;
        let allowed = match grant.role.as_str() {
            "orchestrator" => ["snapshot","quote","reserve","acknowledge",
               "launch_mock","job","events","timeline","catalog_states","catalog_models"].contains(&op),
            "collector" => ["snapshot","job","events","timeline","observe_usage",
               "observe_lifecycle","provider_report","finalize","reconcile"].contains(&op),
            "viewer" => ["snapshot","job","events","timeline",
               "catalog_states","catalog_models"].contains(&op),
            _ => false,
        };
        if !allowed {return Err(Error::Invalid("operation prohibited for caller role".into()));}
        let account_project=match op {
            "quote"|"reserve" => {
                let p=request.get("proposal").ok_or_else(||Error::Invalid("missing proposal".into()))?;
                let a=p.get("account_id").and_then(Value::as_str).unwrap_or("");
                let project=p.get("project_id").and_then(Value::as_str).unwrap_or("");
                Some((a.to_string(),project.to_string()))
            }
            "job"|"acknowledge"|"launch_mock"|"timeline"|"finalize"|
                "observe_lifecycle" => {
                let job=request.get("job_id").and_then(Value::as_str).unwrap_or("");
                let j=store.job(job)?;
                let a=j["proposal"]["account_id"].as_str().unwrap_or("");
                let project=j["proposal"]["project_id"].as_str().unwrap_or("");
                Some((a.to_string(),project.to_string()))
            }
            "events" => {
                let job=request.get("job_id").and_then(Value::as_str)
                    .ok_or_else(||Error::Invalid("unscoped event enumeration prohibited".into()))?;
                let j=store.job(job)?;
                Some((
                    j["proposal"]["account_id"].as_str().unwrap_or("").into(),
                    j["proposal"]["project_id"].as_str().unwrap_or("").into()
                ))
            }
            "observe_usage" => {
                if let Some(job)=request.get("job_id").and_then(Value::as_str){
                    let j=store.job(job)?;
                    Some((
                        j["proposal"]["account_id"].as_str().unwrap_or("").into(),
                        j["proposal"]["project_id"].as_str().unwrap_or("").into()
                    ))
                } else {
                    let meter=request.get("meter_id").and_then(Value::as_str).unwrap_or("");
                    // Look up the meter owner; never trust a supplied account alias.
                    let a=store.account_for_meter(meter)?;
                    if !grant.accounts.contains(&a) {
                        return Err(Error::Invalid("unattributed meter is outside caller scope".into()));
                    }
                    None
                }
            }
            "provider_report" => {
                let meter=request.get("meter_id").and_then(Value::as_str).unwrap_or("");
                let a=store.account_for_meter(meter)?;
                if !grant.accounts.contains(&a) {
                    return Err(Error::Invalid("provider meter is outside caller scope".into()));
                }
                None
            }
            _=>None
        };
        if let Some((account,project))=account_project {
            if !grant.accounts.contains(&account) || !grant.projects.contains(&project) {
                return Err(Error::Invalid("account or project outside caller grant".into()));
            }
        }
        Ok(grant)
    }
    pub fn filter_result(&self,grant:&Grant,op:&str,mut output:Value)->Value {
        if grant.role=="admin" {return output;}
        if op=="snapshot" || op=="reconcile" {
            if let Some(values)=output.pointer_mut("/result/balances").and_then(Value::as_array_mut) {
                values.retain(|b|{
                    b.get("account").and_then(Value::as_str).is_some_and(|a|grant.accounts.iter().any(|x|x==a))
                });
            }
            if let Some(values)=output.pointer_mut("/result/deficits").and_then(Value::as_array_mut) {
                values.clear(); // No unscoped provider deficit disclosure.
            }
            if let Some(values)=output.pointer_mut("/result/stale_meters").and_then(Value::as_array_mut){
                values.clear();
            }
        }
        output
    }
}
