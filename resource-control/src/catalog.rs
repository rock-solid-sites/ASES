//! Account registry and passive model catalog snapshots.
//! A public catalog is *never* equivalent to account entitlement or runtime capacity.
use crate::{check_id, nonblank, Error, Result, Store};
use rusqlite::{params, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Account {
    pub id: String,
    pub provider: String,
    pub payer_ref: String,
    pub registration_status: String,
    pub credential_status: String,
    pub entitlement_status: String,
    pub allowed_projects: Vec<String>,
    pub source: String,
    pub observed_at: i64,
    pub ttl_seconds: i64,
}
impl Account {
    fn verify(&self)->Result<()>{
        for (v,name) in [(&self.id,"account"),(&self.provider,"provider"),(&self.payer_ref,"payer")]{
            check_id(v,name)?;
        }
        for project in &self.allowed_projects {check_id(project,"authorized project")?;}
        nonblank(&self.source,"account evidence source")?;
        if self.ttl_seconds<0 {return Err(Error::Invalid("negative account observation TTL".into()));}
        if !["reported","verified","inactive","unknown"].contains(&self.registration_status.as_str()) ||
           !["working","untested","invalid","unknown"].contains(&self.credential_status.as_str()) ||
           !["active","exhausted","expired","unknown"].contains(&self.entitlement_status.as_str()) {
            return Err(Error::Invalid("invalid account or entitlement evidence classification".into()));
        }
        Ok(())
    }
    pub fn fresh(&self,at:i64)->bool{
        self.ttl_seconds>0 && at>=self.observed_at &&
            at.saturating_sub(self.observed_at)<=self.ttl_seconds
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CatalogImport {
    pub provider: String,
    pub source_url: String,
    pub retrieved_at: i64,
    pub payload: Value,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CatalogChange {
    pub provider: String,
    pub digest: String,
    pub changed: bool,
    pub catalog_version: i64,
    pub added_ids: Vec<String>,
    pub removed_ids: Vec<String>,
}
fn version_marker(tx:&rusqlite::Transaction<'_>)->Result<i64>{
    Ok(tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?)
}
fn model_ids(payload:&Value)->Result<std::collections::BTreeSet<String>>{
    let models=payload.get("data").or_else(||payload.get("models"))
        .and_then(Value::as_array).ok_or_else(||Error::Invalid("catalog requires models/data array".into()))?;
    if models.len()>10000 {return Err(Error::Invalid("catalog unreasonably large".into()));}
    let mut ids=std::collections::BTreeSet::new();
    for row in models {
        let id=row.get("id").and_then(Value::as_str)
            .ok_or_else(||Error::Invalid("catalog model without identifier".into()))?;
        check_id(id,"model")?;
        if !ids.insert(id.into()) {return Err(Error::Invalid("duplicate model id".into()));}
    }
    Ok(ids)
}
impl Store {
    pub(crate) fn init_catalog(&self)->Result<()>{
        self.db.execute_batch(
            "CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY, data TEXT NOT NULL);
             CREATE TABLE IF NOT EXISTS catalog_checks (
                provider TEXT PRIMARY KEY, last_digest TEXT, last_success INTEGER,
                last_error_at INTEGER, last_error TEXT
             );
             CREATE TABLE IF NOT EXISTS catalog_snapshots (
                provider TEXT NOT NULL, digest TEXT NOT NULL,
                source_url TEXT NOT NULL, retrieved_at INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY(provider,digest)
             );"
        )?;
        Ok(())
    }
    pub fn register_account(&mut self,account:&Account)->Result<i64>{
        account.verify()?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        if let Some(old)=tx.query_row("SELECT data FROM accounts WHERE id=?1",[&account.id],
                                     |r|r.get::<_,String>(0)).optional()? {
            let old:Account=serde_json::from_str(&old)?;
            if old.provider!=account.provider || old.payer_ref!=account.payer_ref {
                return Err(Error::Conflict("account identity or payer cannot silently change".into()));
            }
        }
        tx.execute("INSERT INTO accounts(id,data) VALUES (?1,?2)
                    ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                   params![account.id,serde_json::to_string(account)?])?;
        Self::bump_catalog(&tx)?;
        let rev:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        tx.commit()?;
        Ok(rev)
    }
    pub fn account(&self,id:&str)->Result<Account>{
        let s:String=self.db.query_row("SELECT data FROM accounts WHERE id=?1",[id],
                   |r|r.get(0)).optional()?.ok_or_else(||Error::Invalid("unknown account".into()))?;
        Ok(serde_json::from_str(&s)?)
    }
    pub fn accounts(&self)->Result<Vec<Account>>{
        let mut q=self.db.prepare("SELECT data FROM accounts ORDER BY id")?;
        let rows=q.query_map([],|r|r.get::<_,String>(0))?;
        rows.map(|r| Ok(serde_json::from_str(&r?)?)).collect()
    }
    pub fn import_catalog(&mut self,p:&CatalogImport)->Result<CatalogChange>{
        check_id(&p.provider,"catalog provider")?;
        if !p.source_url.starts_with("https://") {return Err(Error::Invalid("catalog source must be HTTPS".into()));}
        nonblank(&p.source_url,"catalog URL")?;
        let ids=model_ids(&p.payload)?;
        let canonical=serde_json::to_string(&p.payload)?;
        if canonical.len()>4*1024*1024 {return Err(Error::Invalid("catalog exceeds 4 MiB safety bound".into()));}
        let digest=format!("{:x}",Sha256::digest(canonical.as_bytes()));
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let previous:Option<String>=tx.query_row("SELECT last_digest FROM catalog_checks WHERE provider=?1",
                                                 [&p.provider],|r|r.get(0)).optional()?.flatten();
        let changed=previous.as_deref()!=Some(&digest);
        let mut oldids=std::collections::BTreeSet::new();
        if let Some(ref prev)=previous {
            let old:Option<String>=tx.query_row(
                "SELECT payload_json FROM catalog_snapshots WHERE provider=?1 AND digest=?2",
                params![p.provider,prev],|r|r.get(0)).optional()?;
            if let Some(old)=old { oldids=model_ids(&serde_json::from_str::<Value>(&old)?)?; }
        }
        tx.execute("INSERT OR IGNORE INTO catalog_snapshots(provider,digest,source_url,retrieved_at,payload_json)
                    VALUES (?1,?2,?3,?4,?5)",
                   params![p.provider,digest,p.source_url,p.retrieved_at,canonical])?;
        tx.execute("INSERT INTO catalog_checks(provider,last_digest,last_success,last_error_at,last_error)
                    VALUES (?1,?2,?3,NULL,NULL)
                    ON CONFLICT(provider) DO UPDATE SET last_digest=excluded.last_digest,
                    last_success=excluded.last_success,last_error_at=NULL,last_error=NULL",
                   params![p.provider,digest,p.retrieved_at])?;
        if changed {
            Self::bump_catalog(&tx)?;
            Self::log(&tx,&format!("catalog:{}:{}:{}",p.provider,version_marker(&tx)?,digest),
                None,"CATALOG_CHANGED",p.retrieved_at,json!({
                "provider":p.provider,"digest":digest,"previous_digest":previous,
                "added":ids.difference(&oldids).collect::<Vec<_>>(),
                "removed":oldids.difference(&ids).collect::<Vec<_>>()
            }))?;
        }
        let version:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        tx.commit()?;
        Ok(CatalogChange{
            provider:p.provider.clone(),digest,changed,catalog_version:version,
            added_ids:ids.difference(&oldids).cloned().collect(),
            removed_ids:oldids.difference(&ids).cloned().collect()
        })
    }
    pub fn catalog_failure(&mut self,provider:&str,description:&str,at:i64)->Result<()>{
        check_id(provider,"provider")?;
        nonblank(description,"failure")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        tx.execute("INSERT INTO catalog_checks(provider,last_digest,last_success,last_error_at,last_error)
                    VALUES (?1,NULL,NULL,?2,?3)
                    ON CONFLICT(provider) DO UPDATE SET last_error_at=excluded.last_error_at,
                    last_error=excluded.last_error",
                   params![provider,at,description])?;
        let evidence_id=format!("catalog-error:{provider}:{at}:{:x}",Sha256::digest(description.as_bytes()));
        let exists:bool=tx.query_row("SELECT EXISTS(SELECT 1 FROM events WHERE id=?1)",[&evidence_id],|r|r.get(0))?;
        if !exists {
        Self::log(&tx,&evidence_id,None,"CATALOG_REFRESH_FAILED",
                  at,json!({"provider":provider,"error":description,"old_catalog_retained":true}))?;
        }
        tx.commit()?;
        Ok(())
    }
    pub fn catalog_states(&self,at:i64,ttl_seconds:i64)->Result<Vec<Value>>{
        let mut stmt=self.db.prepare("SELECT provider,last_digest,last_success,last_error_at,last_error
                                      FROM catalog_checks ORDER BY provider")?;
        let rows=stmt.query_map([],|r|Ok((
            r.get::<_,String>(0)?,r.get::<_,Option<String>>(1)?,r.get::<_,Option<i64>>(2)?,
            r.get::<_,Option<i64>>(3)?,r.get::<_,Option<String>>(4)?
        )))?;
        let mut out=Vec::new();
        for row in rows {
            let (provider,digest,last_success,error_at,error)=row?;
            let fresh=last_success.is_some_and(|t|ttl_seconds>0 && at>=t && at-t<=ttl_seconds);
            out.push(json!({"provider":provider,"digest":digest,"last_success":last_success,
                            "last_error_at":error_at,"last_error":error,
                            "fresh":fresh,"catalog_presence_not_account_access":true}));
        }
        Ok(out)
    }
    pub fn catalog_payload(&self,provider:&str)->Result<Value>{
        check_id(provider,"provider")?;
        let r:Option<String>=self.db.query_row(
            "SELECT s.payload_json FROM catalog_checks c JOIN catalog_snapshots s
             ON c.provider=s.provider AND c.last_digest=s.digest WHERE c.provider=?1",
            [provider],|r|r.get(0)).optional()?;
        let raw=r.ok_or_else(||Error::Invalid("no successfully observed catalog".into()))?;
        Ok(serde_json::from_str(&raw)?)
    }
    /// Evidence-backed annotation: does not rewrite usage or increase spend authority.
    pub fn annotate(&mut self,id:&str,related:&str,actor:&str,reason:&str,at:i64)->Result<()>{
        check_id(id,"annotation")?;
        check_id(related,"related event")?;
        check_id(actor,"reported actor")?;
        nonblank(reason,"reason")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let found:bool=tx.query_row("SELECT EXISTS(SELECT 1 FROM events WHERE id=?1)",[related],|r|r.get(0))?;
        if !found {return Err(Error::Invalid("annotation references unknown source event".into()));}
        Self::log(&tx,&format!("annotation:{id}"),None,"MANUAL_INTERPRETATION",at,
                  json!({"related_event":related,"reported_actor":actor,"reason":reason,
                         "authority_not_authenticated":true,"numeric_ledger_unchanged":true}))?;
        tx.commit()?;
        Ok(())
    }
}
