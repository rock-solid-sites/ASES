//! Experimental ASES resource control: typed metering, durable admission and evidence.
//! This crate deliberately cannot launch a real external provider without a separate
//! credential-isolated adapter. The mock launch is the testable control boundary.
use rusqlite::{params, Connection, OptionalExtension, Transaction, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::fmt::{Display, Formatter};
use std::path::Path;

pub mod archive;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug)]
pub enum Error {
    Database(rusqlite::Error),
    Json(serde_json::Error),
    Io(std::io::Error),
    Invalid(String),
    Conflict(String),
}
impl Display for Error {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Database(e) => write!(f, "database: {e}"),
            Self::Json(e) => write!(f, "json: {e}"),
            Self::Io(e) => write!(f, "io: {e}"),
            Self::Invalid(e) => write!(f, "invalid: {e}"),
            Self::Conflict(e) => write!(f, "conflict: {e}"),
        }
    }
}
impl std::error::Error for Error {}
impl From<rusqlite::Error> for Error { fn from(e: rusqlite::Error) -> Self { Self::Database(e) } }
impl From<serde_json::Error> for Error { fn from(e: serde_json::Error) -> Self { Self::Json(e) } }
impl From<std::io::Error> for Error { fn from(e: std::io::Error) -> Self { Self::Io(e) } }
pub type Result<T> = std::result::Result<T, Error>;

pub fn now() -> i64 {
    SystemTime::now().duration_since(UNIX_EPOCH).expect("system clock before Unix epoch").as_secs() as i64
}
fn check_id(s: &str, field: &str) -> Result<()> {
    if s.is_empty() || s.len() > 160 || !s.bytes().all(|c| c.is_ascii_alphanumeric() || matches!(c, b'-' | b'_' | b'.' | b':' | b'/')) {
        return Err(Error::Invalid(format!("{field}: invalid or empty identifier")));
    }
    Ok(())
}
fn nonblank(s: &str, field: &str) -> Result<()> {
    if s.trim().is_empty() || s.len() > 1024 { return Err(Error::Invalid(format!("{field}: missing or too long"))); }
    Ok(())
}
fn as_i64(n: u64, what: &str) -> Result<i64> {
    i64::try_from(n).map_err(|_| Error::Invalid(format!("{what}: exceeds SQLite integer range")))
}
fn checked_add(a: i64, b: i64, what: &str) -> Result<i64> {
    a.checked_add(b).ok_or_else(|| Error::Invalid(format!("{what}: arithmetic overflow")))
}
fn checked_mul(a: i64, b: i64, what: &str) -> Result<i64> {
    a.checked_mul(b).ok_or_else(|| Error::Invalid(format!("{what}: arithmetic overflow")))
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Meter {
    pub id: String,
    pub account: String,
    pub provider: String,
    pub product: String,
    pub period: String,
    pub unit: String,
    pub limit: u64,
    #[serde(default)]
    pub guard: u64,
    pub observed_at: i64,
    pub ttl_seconds: i64,
    pub source: String,
    #[serde(default)]
    pub price_per_unit_micros: u64,
    #[serde(default)]
    pub chargeable: bool,
}
impl Meter {
    fn verify(&self) -> Result<()> {
        for (v, n) in [(&self.id, "meter"), (&self.account, "account"), (&self.provider, "provider"),
                       (&self.product, "product"), (&self.period, "period"), (&self.unit, "unit")] {
            check_id(v, n)?;
        }
        nonblank(&self.source, "source")?;
        if self.guard > self.limit { return Err(Error::Invalid("meter guard exceeds limit".into())); }
        if self.ttl_seconds < 0 { return Err(Error::Invalid("negative TTL".into())); }
        as_i64(self.limit, "limit")?;
        as_i64(self.guard, "guard")?;
        as_i64(self.price_per_unit_micros, "price")?;
        if self.chargeable && self.price_per_unit_micros == 0 {
            return Err(Error::Invalid("chargeable meter without verified nonzero price".into()));
        }
        Ok(())
    }
    fn fresh(&self, at: i64) -> bool {
        self.ttl_seconds > 0 && at >= self.observed_at &&
            at.saturating_sub(self.observed_at) <= self.ttl_seconds
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Environment {
    pub id: String,
    pub account: String,
    pub max_parallel: u32,
    pub observed_at: i64,
    pub ttl_seconds: i64,
    pub source: String,
}
impl Environment {
    fn verify(&self) -> Result<()> {
        check_id(&self.id, "environment")?;
        check_id(&self.account, "environment account")?;
        nonblank(&self.source, "source")?;
        if self.max_parallel == 0 || self.ttl_seconds < 0 {
            return Err(Error::Invalid("environment requires positive concurrency and nonnegative TTL".into()));
        }
        Ok(())
    }
    fn fresh(&self, at: i64) -> bool {
        self.ttl_seconds > 0 && at >= self.observed_at &&
        at.saturating_sub(self.observed_at) <= self.ttl_seconds
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct Claim { pub meter_id: String, pub amount: u64 }
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Proposal {
    pub job_id: String,
    pub account_id: String,
    pub environment_id: String,
    pub estimated_wall_seconds: u64,
    #[serde(default)]
    pub claims: Vec<Claim>,
    #[serde(default)]
    pub paid_spend_cap_micros: Option<u64>,
    #[serde(default)]
    pub forecast_context: Option<Value>,
}
impl Proposal {
    fn verify(&self) -> Result<()> {
        check_id(&self.job_id, "job")?;
        check_id(&self.account_id, "proposal account")?;
        check_id(&self.environment_id, "environment")?;
        if self.estimated_wall_seconds == 0 { return Err(Error::Invalid("estimated wall duration must be positive".into())); }
        as_i64(self.estimated_wall_seconds, "duration")?;
        if let Some(cap) = self.paid_spend_cap_micros { as_i64(cap, "spend cap")?; }
        let mut seen = std::collections::HashSet::new();
        for c in &self.claims {
            check_id(&c.meter_id, "claim meter")?;
            if c.amount == 0 || !seen.insert(&c.meter_id) {
                return Err(Error::Invalid("zero or duplicate claim; combine claims per meter".into()));
            }
            as_i64(c.amount, "claim")?;
        }
        Ok(())
    }
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub meter_id: String,
    pub limit: i64,
    pub guard: i64,
    pub local_observed: i64,
    pub provider_reported: Option<i64>,
    pub provider_complete_through: Option<i64>,
    pub effective_consumed: i64,
    pub active_reserved_remaining: i64,
    pub available: i64,
    pub fresh: bool,
    pub account: String,
    pub period: String,
    pub unit: String,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quote {
    pub eligible: bool,
    pub reason: String,
    pub catalog_version: i64,
    pub estimated_cash_micros: i64,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Reservation {
    pub job_id: String,
    pub status: String,
    pub catalog_version: i64,
    pub expires_at: i64,
    pub replayed: bool,
}
pub struct Store { db: Connection }

impl Store {
    pub fn open(path: impl AsRef<Path>) -> Result<Self> {
        let db = Connection::open(path)?;
        db.busy_timeout(std::time::Duration::from_secs(8))?;
        db.execute_batch(
            "PRAGMA foreign_keys=ON;
             PRAGMA journal_mode=WAL;
             PRAGMA synchronous=FULL;
             CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value INTEGER NOT NULL);
             INSERT OR IGNORE INTO meta(key,value) VALUES ('catalog_version',0);
             CREATE TABLE IF NOT EXISTS meters (
                id TEXT PRIMARY KEY, data TEXT NOT NULL
             );
             CREATE TABLE IF NOT EXISTS environments (
                id TEXT PRIMARY KEY, data TEXT NOT NULL
             );
             CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, env TEXT NOT NULL,
                proposal TEXT NOT NULL,
                catalog_version INTEGER NOT NULL,
                state TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                ack_id TEXT, launch_id TEXT, outcome TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(env) REFERENCES environments(id)
             );
             CREATE TABLE IF NOT EXISTS claims (
                job_id TEXT NOT NULL, meter_id TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
                PRIMARY KEY(job_id,meter_id),
                FOREIGN KEY(job_id) REFERENCES jobs(id),
                FOREIGN KEY(meter_id) REFERENCES meters(id)
             );
             CREATE TABLE IF NOT EXISTS usage_events (
                id TEXT PRIMARY KEY, job_id TEXT, meter_id TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK(amount>0), occurred_at INTEGER NOT NULL,
                source TEXT NOT NULL, FOREIGN KEY(meter_id) REFERENCES meters(id)
             );
             CREATE TABLE IF NOT EXISTS provider_reports (
                id TEXT PRIMARY KEY, meter_id TEXT NOT NULL,
                used INTEGER NOT NULL CHECK(used>=0), complete_through INTEGER,
                observed_at INTEGER NOT NULL, source TEXT NOT NULL,
                FOREIGN KEY(meter_id) REFERENCES meters(id)
             );
             CREATE INDEX IF NOT EXISTS ix_usage_meter_time ON usage_events(meter_id, occurred_at);
             CREATE INDEX IF NOT EXISTS ix_report_meter_time ON provider_reports(meter_id, observed_at);
             CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, job_id TEXT, kind TEXT NOT NULL,
                at INTEGER NOT NULL, payload TEXT NOT NULL
             );
             CREATE TABLE IF NOT EXISTS archives (
                id TEXT PRIMARY KEY, path TEXT NOT NULL, sha256 TEXT NOT NULL,
                bytes INTEGER NOT NULL, verified INTEGER NOT NULL,
                scope TEXT NOT NULL, exported_at INTEGER NOT NULL
             );"
        )?;
        Ok(Self { db })
    }

    pub fn catalog_version(&self) -> Result<i64> {
        Ok(self.db.query_row("SELECT value FROM meta WHERE key='catalog_version'", [], |r| r.get(0))?)
    }
    fn bump_catalog(tx: &Transaction<'_>) -> Result<()> {
        tx.execute("UPDATE meta SET value=value+1 WHERE key='catalog_version'", [])?;
        Ok(())
    }
    pub fn register_meter(&mut self, meter: &Meter) -> Result<i64> {
        meter.verify()?;
        let tx = self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        if let Some(raw)=tx.query_row("SELECT data FROM meters WHERE id=?1",[&meter.id],|r|r.get::<_,String>(0)).optional()? {
            let old:Meter=serde_json::from_str(&raw)?;
            if (old.account.as_str(),old.provider.as_str(),old.product.as_str(),old.period.as_str(),old.unit.as_str())
                != (meter.account.as_str(),meter.provider.as_str(),meter.product.as_str(),meter.period.as_str(),meter.unit.as_str()) {
                return Err(Error::Conflict("meter identity cannot be rebound; create new meter ID".into()));
            }
        }
        tx.execute("INSERT INTO meters(id,data) VALUES (?1,?2)
                    ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                   params![meter.id,serde_json::to_string(meter)?])?;
        Self::bump_catalog(&tx)?;
        let rev: i64 = tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        tx.commit()?;
        Ok(rev)
    }
    pub fn register_environment(&mut self, env: &Environment) -> Result<i64> {
        env.verify()?;
        let tx = self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        tx.execute("INSERT INTO environments(id,data) VALUES (?1,?2)
                    ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                   params![env.id,serde_json::to_string(env)?])?;
        Self::bump_catalog(&tx)?;
        let rev: i64 = tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        tx.commit()?;
        Ok(rev)
    }
    fn meter(tx: &Transaction<'_>, id: &str) -> Result<Meter> {
        let raw: String = tx.query_row("SELECT data FROM meters WHERE id=?1", [id], |r| r.get(0))
            .optional()?.ok_or_else(||Error::Invalid(format!("unknown meter {id}")))?;
        Ok(serde_json::from_str(&raw)?)
    }
    fn env(tx: &Transaction<'_>, id: &str) -> Result<Environment> {
        let raw: String = tx.query_row("SELECT data FROM environments WHERE id=?1", [id], |r| r.get(0))
            .optional()?.ok_or_else(||Error::Invalid(format!("unknown environment {id}")))?;
        Ok(serde_json::from_str(&raw)?)
    }
    fn balance(tx: &Transaction<'_>, id: &str, at: i64) -> Result<Balance> {
        let m = Self::meter(tx, id)?;
        let local: i64 = tx.query_row(
            "SELECT COALESCE(SUM(amount),0) FROM usage_events WHERE meter_id=?1",
            [id], |r|r.get(0))?;
        let report: Option<(i64, Option<i64>)> = tx.query_row(
            "SELECT used,complete_through FROM provider_reports WHERE meter_id=?1
             ORDER BY observed_at DESC,rowid DESC LIMIT 1",
            [id], |r| Ok((r.get(0)?,r.get(1)?))).optional()?;
        let provider_used = report.map(|v|v.0);
        let watermark = report.and_then(|v|v.1);
        let effective = match (provider_used, watermark) {
            (Some(reported), Some(through)) => {
                let after: i64 = tx.query_row(
                    "SELECT COALESCE(SUM(amount),0) FROM usage_events WHERE meter_id=?1 AND occurred_at>?2",
                    params![id,through], |r| r.get(0))?;
                std::cmp::max(local, checked_add(reported, after, "reported+recent usage")?)
            }
            (Some(reported), None) => checked_add(reported,local,"unknown report coverage")?,
            (None, _) => local,
        };
        let mut reserved: i64 = 0;
        let mut stmt = tx.prepare(
            "SELECT c.job_id,c.amount FROM claims c JOIN jobs j ON j.id=c.job_id
             WHERE c.meter_id=?1 AND j.state NOT IN ('CLOSED','EXPIRED')")?;
        let rows = stmt.query_map([id], |r| Ok((r.get::<_,String>(0)?,r.get::<_,i64>(1)?)))?;
        for row in rows {
            let (job, amount) = row?;
            let observed: i64 = tx.query_row(
                "SELECT COALESCE(SUM(amount),0) FROM usage_events WHERE job_id=?1 AND meter_id=?2",
                params![job,id],|r|r.get(0))?;
            reserved = checked_add(reserved, amount.saturating_sub(observed).max(0),"total reservations")?;
        }
        let headroom = as_i64(m.limit,"limit")?
            .checked_sub(as_i64(m.guard,"guard")?)
            .and_then(|v|v.checked_sub(effective))
            .and_then(|v|v.checked_sub(reserved))
            .ok_or_else(||Error::Invalid("balance overflow".into()))?;
        Ok(Balance{
            meter_id: id.into(), limit:as_i64(m.limit,"limit")?,guard:as_i64(m.guard,"guard")?,
            local_observed:local,provider_reported:provider_used,
            provider_complete_through:watermark,effective_consumed:effective,
            active_reserved_remaining:reserved,available:headroom,
            fresh:m.fresh(at),account:m.account,period:m.period,unit:m.unit
        })
    }
    pub fn balances(&mut self, at: i64) -> Result<Vec<Balance>> {
        let tx = self.db.transaction_with_behavior(TransactionBehavior::Deferred)?;
        let mut ids = Vec::new();
        { let mut q=tx.prepare("SELECT id FROM meters ORDER BY id")?;
          for r in q.query_map([],|r|r.get::<_,String>(0))? { ids.push(r?); }
        }
        let mut out=Vec::new();
        for id in ids { out.push(Self::balance(&tx,&id,at)?); }
        tx.commit()?;
        Ok(out)
    }
    fn validate_proposal(tx: &Transaction<'_>, p: &Proposal, at: i64) -> Result<i64> {
        p.verify()?;
        let env = Self::env(tx,&p.environment_id)?;
        if env.account != p.account_id { return Err(Error::Invalid("environment account mismatch or unauthorized borrowing".into())); }
        if !env.fresh(at) { return Err(Error::Invalid("environment information stale or unverified".into())); }
        let slots:i64=tx.query_row("SELECT COUNT(*) FROM jobs WHERE env=?1 AND state IN ('RESERVED','AUTHORIZED','RUNNING')",
                                   [&p.environment_id],|r|r.get(0))?;
        if slots >= i64::from(env.max_parallel) {
            return Err(Error::Conflict("environment concurrency exhausted".into()));
        }
        let mut quoted = 0i64;
        for claim in &p.claims {
            let m=Self::meter(tx,&claim.meter_id)?;
            if m.account != p.account_id { return Err(Error::Invalid("meter account mismatch or unauthorized borrowing".into())); }
            if !m.fresh(at) {
                return Err(Error::Invalid(format!("meter {} stale or unverified",m.id)));
            }
            let b=Self::balance(tx,&claim.meter_id,at)?;
            let requested=as_i64(claim.amount,"claim")?;
            if b.available < requested {
                return Err(Error::Conflict(format!("insufficient {}: available {} requested {}",
                                                   m.id,b.available,requested)));
            }
            if m.chargeable {
                quoted = checked_add(quoted,checked_mul(requested,as_i64(m.price_per_unit_micros,"price")?,"cost")?,"cash budget")?;
            }
        }
        if quoted > 0 {
            let cap= p.paid_spend_cap_micros.ok_or_else(|| Error::Invalid("paid execution requires explicit spend cap".into()))?;
            if quoted > as_i64(cap,"cap")? { return Err(Error::Conflict("estimated charge exceeds authorized cap".into())); }
        }
        Ok(quoted)
    }
    pub fn quote(&mut self, p: &Proposal, at: i64) -> Result<Quote> {
        let tx = self.db.transaction_with_behavior(TransactionBehavior::Deferred)?;
        let catalog:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        let checked = Self::validate_proposal(&tx,p,at);
        tx.commit()?;
        Ok(match checked {
            Ok(cost)=>Quote{eligible:true,reason:"eligible for atomic admission".into(),catalog_version:catalog,estimated_cash_micros:cost},
            Err(e)=>Quote{eligible:false,reason:e.to_string(),catalog_version:catalog,estimated_cash_micros:0}
        })
    }
    fn log(tx:&Transaction<'_>, id:&str, job:Option<&str>, kind:&str, at:i64, payload:Value) -> Result<()> {
        tx.execute("INSERT INTO events(id,job_id,kind,at,payload) VALUES (?1,?2,?3,?4,?5)",
                   params![id,job,kind,at,serde_json::to_string(&payload)?])?;
        Ok(())
    }
    pub fn reserve(&mut self,p:&Proposal,expected_catalog:i64,at:i64) -> Result<Reservation> {
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let current:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        if current != expected_catalog { return Err(Error::Conflict("stale catalog revision".into())); }
        let previous:Option<(String,String,i64)> = tx.query_row(
            "SELECT proposal,state,expires_at FROM jobs WHERE id=?1", [&p.job_id],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
        let canonical=serde_json::to_string(p)?;
        if let Some((existing,state,expires_at))=previous {
            if existing != canonical {return Err(Error::Conflict("job ID reused with different forecast".into()));}
            tx.commit()?;
            return Ok(Reservation{job_id:p.job_id.clone(),status:state,catalog_version:current,expires_at,replayed:true});
        }
        let cost=Self::validate_proposal(&tx,p,at)?;
        let expires_at=checked_add(at,900,"expiry")?;
        tx.execute("INSERT INTO jobs(id,env,proposal,catalog_version,state,expires_at,created_at)
                    VALUES (?1,?2,?3,?4,'RESERVED',?5,?6)",
                   params![p.job_id,p.environment_id,canonical,current,expires_at,at])?;
        for c in &p.claims {
            tx.execute("INSERT INTO claims(job_id,meter_id,amount) VALUES (?1,?2,?3)",
                       params![p.job_id,c.meter_id,as_i64(c.amount,"claim")?])?;
        }
        Self::log(&tx,&format!("{}:reserved",p.job_id),Some(&p.job_id),"RESERVED",at,
                  json!({"forecast":p,"estimated_cash_micros":cost,"catalog_version":current}))?;
        tx.commit()?;
        Ok(Reservation{job_id:p.job_id.clone(),status:"RESERVED".into(),catalog_version:current,expires_at,replayed:false})
    }
    pub fn acknowledge(&mut self,job:&str,ack_id:&str,expected_catalog:i64,at:i64) -> Result<String> {
        check_id(job,"job")?;check_id(ack_id,"ack")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let current:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        let (state,version,expiry,prior):(String,i64,i64,Option<String>)=tx.query_row(
            "SELECT state,catalog_version,expires_at,ack_id FROM jobs WHERE id=?1",[job],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?)))
            .optional()?.ok_or_else(||Error::Invalid("unknown job".into()))?;
        if ["AUTHORIZED","RUNNING","CLOSED"].contains(&state.as_str()) && prior.as_deref()==Some(ack_id) {
            tx.commit()?;return Ok("AUTHORIZED_REPLAY".into());
        }
        if state!="RESERVED" {return Err(Error::Conflict(format!("cannot acknowledge state {state}")));}
        if version!=expected_catalog || version!=current {
            return Err(Error::Conflict("catalog changed since reservation".into()));
        }
        if expiry<at {return Err(Error::Conflict("reservation expired".into()));}
        let mut stmt=tx.prepare("SELECT meter_id FROM claims WHERE job_id=?1")?;
        let meters:Vec<String>=stmt.query_map([job],|r|r.get(0))?.collect::<rusqlite::Result<_>>()?;
        drop(stmt);
        for id in meters {
            let m=Self::meter(&tx,&id)?;
            if !m.fresh(at) {return Err(Error::Conflict("meter data expired before authorization".into()));}
            // A newly reported overrun may consume this reservation's capacity.
            let b=Self::balance(&tx,&id,at)?;
            if b.available<0 {return Err(Error::Conflict("provider usage exceeds admitted capacity".into()));}
        }
        let proposal:String=tx.query_row("SELECT proposal FROM jobs WHERE id=?1",[job],|r|r.get(0))?;
        let p:Proposal=serde_json::from_str(&proposal)?;
        if !Self::env(&tx,&p.environment_id)?.fresh(at) {
            return Err(Error::Conflict("environment data expired before authorization".into()));
        }
        tx.execute("UPDATE jobs SET state='AUTHORIZED',ack_id=?2 WHERE id=?1",params![job,ack_id])?;
        Self::log(&tx,&format!("{job}:ack:{ack_id}"),Some(job),"AUTHORIZED",at,
                  json!({"ack_id":ack_id,"catalog_version":version}))?;
        tx.commit()?;
        Ok("AUTHORIZED".into())
    }
    /// Only an idempotent mock adapter is implemented. Never infer an external launch occurred.
    pub fn launch_mock(&mut self,job:&str,launch_id:&str,at:i64) -> Result<String> {
        check_id(job,"job")?;check_id(launch_id,"launch")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let (state,prior,expiry):(String,Option<String>,i64)=tx.query_row(
            "SELECT state,launch_id,expires_at FROM jobs WHERE id=?1",[job],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?)))
            .optional()?.ok_or_else(||Error::Invalid("unknown job".into()))?;
        if state=="RUNNING" && prior.as_deref()==Some(launch_id) {
            tx.commit()?;return Ok("RUNNING_REPLAY".into());
        }
        if state!="AUTHORIZED" {return Err(Error::Conflict(format!("launch forbidden from state {state}")));}
        if expiry<at {return Err(Error::Conflict("authorization expired".into()));}
        let (proposal,version):(String,i64)=tx.query_row(
            "SELECT proposal,catalog_version FROM jobs WHERE id=?1",[job],
            |r|Ok((r.get(0)?,r.get(1)?)))?;
        let p:Proposal=serde_json::from_str(&proposal)?;
        let current:i64=tx.query_row("SELECT value FROM meta WHERE key='catalog_version'",[],|r|r.get(0))?;
        if current!=version {return Err(Error::Conflict("launch catalog revision stale".into()));}
        if !Self::env(&tx,&p.environment_id)?.fresh(at) {
            return Err(Error::Conflict("environment observation stale at launch".into()));
        }
        for claim in &p.claims {
            if !Self::meter(&tx,&claim.meter_id)?.fresh(at) ||
               Self::balance(&tx,&claim.meter_id,at)?.available<0 {
                return Err(Error::Conflict("resource overconsumed or stale at launch".into()));
            }
        }
        tx.execute("UPDATE jobs SET state='RUNNING',launch_id=?2 WHERE id=?1",params![job,launch_id])?;
        Self::log(&tx,&format!("{job}:launch:{launch_id}"),Some(job),"MOCK_LAUNCH",at,
                  json!({"launch_id":launch_id,"external_provider_launch":false}))?;
        tx.commit()?;
        Ok("MOCK_RUNNING".into())
    }
    pub fn observe_usage(&mut self,id:&str,job:Option<&str>,meter:&str,amount:u64,at:i64,source:&str) -> Result<String> {
        check_id(id,"usage event")?;check_id(meter,"meter")?;nonblank(source,"usage source")?;
        if let Some(job)=job {check_id(job,"job")?;}
        if amount==0 {return Err(Error::Invalid("usage delta must be positive".into()));}
        let n=as_i64(amount,"observed usage")?;
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let selected_meter=Self::meter(&tx,meter)?;
        if let Some(job)=job {
            let proposal:Option<String>=tx.query_row("SELECT proposal FROM jobs WHERE id=?1",[job],|r|r.get(0)).optional()?;
            let proposal=proposal.ok_or_else(||Error::Invalid("unknown observation job".into()))?;
            let p:Proposal=serde_json::from_str(&proposal)?;
            if p.account_id!=selected_meter.account {
                return Err(Error::Invalid("cross-account usage cannot be attributed to this job; record as external".into()));
            }
        }
        let prior:Option<(Option<String>,String,i64,i64,String)>=tx.query_row(
            "SELECT job_id,meter_id,amount,occurred_at,source FROM usage_events WHERE id=?1",[id],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).optional()?;
        if let Some(p)=prior {
            if p==(job.map(str::to_string),meter.to_string(),n,at,source.to_string()) {
                tx.commit()?;return Ok("USAGE_REPLAY".into());
            }
            return Err(Error::Conflict("same usage event ID with different payload".into()));
        }
        tx.execute("INSERT INTO usage_events(id,job_id,meter_id,amount,occurred_at,source)
                    VALUES (?1,?2,?3,?4,?5,?6)",params![id,job,meter,n,at,source])?;
        Self::log(&tx,&format!("obs:{id}"),job,"USAGE_OBSERVED",at,
                  json!({"meter":meter,"amount":n,"source":source,"event_id":id}))?;
        tx.commit()?;
        Ok("USAGE_RECORDED".into())
    }
    pub fn provider_report(&mut self,id:&str,meter:&str,used:u64,complete_through:Option<i64>,at:i64,source:&str)->Result<String> {
        check_id(id,"provider report")?;check_id(meter,"meter")?;nonblank(source,"provider source")?;
        let used=as_i64(used,"provider usage")?;
        if complete_through.is_some_and(|t|t>at) {return Err(Error::Invalid("future report coverage".into()));}
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        Self::meter(&tx,meter)?;
        let existing:Option<(String,i64,Option<i64>,i64,String)>=tx.query_row(
            "SELECT meter_id,used,complete_through,observed_at,source FROM provider_reports WHERE id=?1",
            [id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).optional()?;
        if let Some(prior)=existing {
            if prior==(meter.to_string(),used,complete_through,at,source.to_string()) {
                tx.commit()?;return Ok("REPORT_REPLAY".into());
            }
            return Err(Error::Conflict("report event ID reused".into()));
        }
        let prior:Option<(i64,i64,Option<i64>)>=tx.query_row(
            "SELECT used,observed_at,complete_through FROM provider_reports WHERE meter_id=?1
             ORDER BY observed_at DESC,rowid DESC LIMIT 1",[meter],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
        if let Some((old,old_at,old_coverage))=prior {
            if at<old_at || used<old || (old_coverage.is_some() && complete_through<old_coverage) {
                return Err(Error::Conflict("stale or decreasing provider report requires attributed correction".into()));
            }
        }
        tx.execute("INSERT INTO provider_reports(id,meter_id,used,complete_through,observed_at,source)
                    VALUES (?1,?2,?3,?4,?5,?6)",params![id,meter,used,complete_through,at,source])?;
        Self::log(&tx,&format!("report:{id}"),None,"PROVIDER_REPORTED",at,
                  json!({"meter":meter,"reported_used":used,"complete_through":complete_through,
                         "source":source,"report_id":id}))?;
        tx.commit()?;
        Ok("PROVIDER_RECORDED".into())
    }
    pub fn finalize(&mut self,job:&str,outcome:&str,at:i64)->Result<String>{
        check_id(job,"job")?;
        if !["completed","failed","cancelled","interrupted"].contains(&outcome) {
            return Err(Error::Invalid("unsupported terminal outcome".into()));
        }
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let previous:Option<(String,Option<String>)>=tx.query_row(
            "SELECT state,outcome FROM jobs WHERE id=?1",[job],
            |r|Ok((r.get(0)?,r.get(1)?))).optional()?;
        let (state,old)=previous.ok_or_else(||Error::Invalid("unknown job".into()))?;
        if state=="CLOSED" {
            if old.as_deref()==Some(outcome) {tx.commit()?;return Ok("CLOSED_REPLAY".into());}
            return Err(Error::Conflict("terminal outcome already recorded".into()));
        }
        if state=="RESERVED" && outcome!="cancelled" {
            return Err(Error::Conflict("unlaunched reservation can only be cancelled".into()));
        }
        if state=="AUTHORIZED" && !["cancelled","interrupted"].contains(&outcome) {
            return Err(Error::Conflict("authorized but unlaunched job cannot claim completion".into()));
        }
        tx.execute("UPDATE jobs SET state='CLOSED',outcome=?2 WHERE id=?1",params![job,outcome])?;
        Self::log(&tx,&format!("{job}:final:{outcome}"),Some(job),"FINALIZED",at,json!({"outcome":outcome}))?;
        tx.commit()?;
        Ok("CLOSED".into())
    }
    pub fn expire_unlaunched(&mut self,at:i64)->Result<usize>{
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let mut stmt=tx.prepare("SELECT id FROM jobs WHERE state IN ('RESERVED','AUTHORIZED') AND expires_at<?1")?;
        let jobs:Vec<String>=stmt.query_map([at],|r|r.get(0))?.collect::<rusqlite::Result<_>>()?;
        drop(stmt);
        for job in &jobs {
            tx.execute("UPDATE jobs SET state='EXPIRED',outcome='expired' WHERE id=?1",[job])?;
            Self::log(&tx,&format!("{job}:expired"),Some(job),"EXPIRED",at,json!({}))?;
        }
        tx.commit()?;
        Ok(jobs.len())
    }
    pub fn job(&self,id:&str)->Result<Value>{
        check_id(id,"job")?;
        let row:Option<(String,String,i64,i64,Option<String>,Option<String>,Option<String>)>=self.db.query_row(
            "SELECT proposal,state,catalog_version,expires_at,ack_id,launch_id,outcome FROM jobs WHERE id=?1",
            [id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?,r.get(5)?,r.get(6)?))).optional()?;
        let (p,state,revision,expiry,ack,launch,outcome)=row.ok_or_else(||Error::Invalid("unknown job".into()))?;
        let mut q=self.db.prepare(
            "SELECT c.meter_id,c.amount,COALESCE(SUM(u.amount),0)
             FROM claims c LEFT JOIN usage_events u ON u.job_id=c.job_id AND u.meter_id=c.meter_id
             WHERE c.job_id=?1 GROUP BY c.meter_id,c.amount ORDER BY c.meter_id")?;
        let charges:Vec<Value>=q.query_map([id],|r|{
            let meter:String=r.get(0)?;let reserved:i64=r.get(1)?;let observed:i64=r.get(2)?;
            Ok(json!({"meter":meter,"reserved":reserved,"observed":observed,
                      "overrun":(observed-reserved).max(0),"unspent":(reserved-observed).max(0)}))
        })?.collect::<rusqlite::Result<_>>()?;
        Ok(json!({"job_id":id,"proposal":serde_json::from_str::<Value>(&p)?,"state":state,
                  "catalog_version":revision,"expires_at":expiry,"ack_id":ack,
                  "launch_id":launch,"outcome":outcome,"meters":charges}))
    }
    pub fn event_log(&self,job:Option<&str>)->Result<Vec<Value>>{
        let sql=if job.is_some() {
            "SELECT id,job_id,kind,at,payload FROM events WHERE job_id=?1 ORDER BY at,id"
        } else {
            "SELECT id,job_id,kind,at,payload FROM events ORDER BY at,id"
        };
        let mut stmt=self.db.prepare(sql)?;
        let decode=|r:&rusqlite::Row<'_>|->rusqlite::Result<(String,Option<String>,String,i64,String)>{
            Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))
        };
        let records:Vec<_>=if let Some(job)=job {
            stmt.query_map([job],decode)?.collect::<rusqlite::Result<_>>()?
        } else {
            stmt.query_map([],decode)?.collect::<rusqlite::Result<_>>()?
        };
        records.into_iter().map(|(id,job,kind,at,payload)|Ok(json!({
            "event_id":id,"job_id":job,"kind":kind,"at":at,
            "payload":serde_json::from_str::<Value>(&payload)?
        }))).collect()
    }

    /// Authenticated collector records lifecycle facts. This records observations,
    /// not inferred productive time or a verified provider bill.
    pub fn observe_lifecycle(&mut self,id:&str,job:&str,kind:&str,at:i64,subject:&str,details:Value)->Result<String>{
        check_id(id,"lifecycle event")?;
        check_id(job,"job")?;
        check_id(subject,"subject")?;
        const ALLOWED:&[&str]=&["ENV_STARTED","ENV_STOPPED","AGENT_STARTED","AGENT_STOPPED",
            "WAIT_STARTED","WAIT_STOPPED","PROVIDER_PAUSED","PROVIDER_RESUMED",
            "LAUNCH_FAILED","PROVISIONING_STARTED","PROVISIONING_ENDED"];
        if !ALLOWED.contains(&kind) {return Err(Error::Invalid("unsupported lifecycle observation".into()));}
        let tx=self.db.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let exists:bool=tx.query_row("SELECT EXISTS(SELECT 1 FROM jobs WHERE id=?1)",[job],|r|r.get(0))?;
        if !exists {return Err(Error::Invalid("unknown lifecycle job".into()));}
        let payload=json!({"subject":subject,"details":details});
        let prior:Option<(Option<String>,String,i64,String)>=tx.query_row(
            "SELECT job_id,kind,at,payload FROM events WHERE id=?1",[id],
            |r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?))).optional()?;
        if let Some((j,k,t,v))=prior {
            if j.as_deref()==Some(job) && k==kind && t==at && v==serde_json::to_string(&payload)? {
                tx.commit()?;return Ok("LIFECYCLE_REPLAY".into());
            }
            return Err(Error::Conflict("lifecycle event ID reused".into()));
        }
        Self::log(&tx,id,Some(job),kind,at,payload)?;
        tx.commit()?;
        Ok("LIFECYCLE_RECORDED".into())
    }
    /// Derived intervals are *only* computed for matched starts/stops; lost events
    /// produce unknown intervals rather than fabricated idle/provider fault time.
    pub fn timeline(&self,job:&str)->Result<Value>{
        let events=self.event_log(Some(job))?;
        let mut open=std::collections::HashMap::<(String,String),i64>::new();
        let mut seconds=std::collections::BTreeMap::<String,i64>::new();
        let mut anomalies=Vec::<String>::new();
        for ev in events {
            let kind=ev["kind"].as_str().unwrap_or("");
            let at=ev["at"].as_i64().unwrap_or(0);
            let subject=ev["payload"]["subject"].as_str().unwrap_or("");
            let (family,start)=match kind {
                "ENV_STARTED"=>("environment",true),"ENV_STOPPED"=>("environment",false),
                "AGENT_STARTED"=>("agent",true),"AGENT_STOPPED"=>("agent",false),
                "WAIT_STARTED"=>("waiting",true),"WAIT_STOPPED"=>("waiting",false),
                "PROVISIONING_STARTED"=>("provisioning",true),"PROVISIONING_ENDED"=>("provisioning",false),
                _=>continue
            };
            let key=(family.to_string(),subject.to_string());
            if start {
                if open.insert(key.clone(),at).is_some() {
                    anomalies.push(format!("duplicate start {}:{}",family,subject));
                }
            } else if let Some(from)=open.remove(&key) {
                if at<from {anomalies.push(format!("negative interval {}:{}",family,subject));continue;}
                let v=seconds.entry(family.to_string()).or_default();
                *v=checked_add(*v,at-from,"timeline")?;
            } else {anomalies.push(format!("unmatched stop {}:{}",family,subject));}
        }
        for ((family,subject),_) in open {anomalies.push(format!("open interval {family}:{subject}"));}
        Ok(json!({"job_id":job,"observed_interval_seconds":seconds,
                  "incomplete_or_ambiguous":!anomalies.is_empty(),"anomalies":anomalies,
                  "note":"Agent intervals may overlap; totals are not a partition of environment lifetime"}))
    }
    pub fn reconcile(&mut self, at:i64)->Result<Value>{
        let balances=self.balances(at)?;
        let deficits:Vec<_>=balances.iter().filter(|b|b.available<0).map(|b|json!({
            "meter":b.meter_id,"deficit":-b.available,"status":"overcommitted_or_overconsumed"
        })).collect();
        let stale:Vec<_>=balances.iter().filter(|b|!b.fresh).map(|b|b.meter_id.clone()).collect();
        Ok(json!({"balances":balances,"deficits":deficits,"stale_meters":stale,
                  "settlement":"NOT_ESTABLISHED_BY_LOCAL_LEDGER"}))
    }
}
