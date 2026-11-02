//! Recoverable *local* compressed session evidence.
//! Successful local read-back does not establish offsite durability.
use crate::{now, Error, Result, Store};
use flate2::{read::GzDecoder, write::GzEncoder, Compression};
use rusqlite::params;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Read, Write};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ArchiveManifest {
    pub job_id: String,
    pub path: String,
    pub sha256: String,
    pub compressed_bytes: u64,
    pub records: usize,
    pub verified_at: i64,
    pub local_recovery_verified: bool,
    pub offsite_recovery_verified: bool,
}

fn digest_file(path: &Path) -> Result<(String,u64)> {
    let mut f=File::open(path)?;
    let mut hasher=Sha256::new();
    let mut buf=[0u8;64*1024];
    let mut size=0u64;
    loop {
        let n=f.read(&mut buf)?;
        if n==0 {break;}
        size+=n as u64;
        hasher.update(&buf[..n]);
    }
    Ok((format!("{:x}",hasher.finalize()),size))
}
pub fn verify_archive(path: &Path,expected_sha:&str,expected_records:usize) -> Result<usize> {
    let (got,_) = digest_file(path)?;
    if got!=expected_sha {return Err(Error::Conflict("archive digest mismatch".into()));}
    let mut reader=BufReader::new(GzDecoder::new(File::open(path)?));
    let mut line=String::new();
    let mut count=0usize;
    loop {
        line.clear();
        let n=reader.read_line(&mut line)?;
        if n==0 {break;}
        let _:Value=serde_json::from_str(&line)?;
        count+=1;
    }
    if count!=expected_records {return Err(Error::Conflict("archive record count mismatch".into()));}
    Ok(count)
}
impl Store {
    /// Exports evidence for one job to a local gzip archive. Redaction/access control
    /// must happen at the call boundary before moving any artifact offsite.
    pub fn export_session(&mut self,job:&str,output:&Path) -> Result<ArchiveManifest> {
        let state=self.job(job)?;
        let events=self.event_log(Some(job))?;
        let mut records=vec![json!({"type":"job","value":state})];
        for event in events { records.push(json!({"type":"event","value":event})); }
        let mut stmt=self.db.prepare(
            "SELECT id,meter_id,amount,occurred_at,source FROM usage_events WHERE job_id=?1 ORDER BY occurred_at,id")?;
        let usage:Vec<Value>=stmt.query_map([job],|r|{
            Ok(json!({"id":r.get::<_,String>(0)?,"meter":r.get::<_,String>(1)?,
              "amount":r.get::<_,i64>(2)?,"at":r.get::<_,i64>(3)?,"source":r.get::<_,String>(4)?}))
        })?.collect::<rusqlite::Result<_>>()?;
        drop(stmt);
        for value in usage {records.push(json!({"type":"usage","value":value}));}

        let parent=output.parent().ok_or_else(||Error::Invalid("archive needs parent directory".into()))?;
        fs::create_dir_all(parent)?;
        if output.exists() {return Err(Error::Conflict("archive destination exists; never overwrite original evidence".into()));}
        let temp=output.with_extension(format!("partial-{}",std::process::id()));
        let result=(||->Result<()>{
            let file=OpenOptions::new().write(true).create_new(true).open(&temp)?;
            let writer=BufWriter::new(file);
            let mut encoder=GzEncoder::new(writer,Compression::default());
            for record in &records {
                serde_json::to_writer(&mut encoder,record)?;
                encoder.write_all(b"\n")?;
            }
            let mut writer=encoder.finish()?;
            writer.flush()?;
            writer.get_ref().sync_all()?;
            fs::rename(&temp,output)?;
            if let Ok(dir)=File::open(parent) {let _=dir.sync_all();}
            Ok(())
        })();
        if result.is_err() {let _=fs::remove_file(&temp);}
        result?;
        let (sha,size)=digest_file(output)?;
        verify_archive(output,&sha,records.len())?;
        let manifest=ArchiveManifest{
            job_id:job.into(),path:output.to_string_lossy().to_string(),
            sha256:sha,compressed_bytes:size,records:records.len(),
            verified_at:now(),local_recovery_verified:true,offsite_recovery_verified:false
        };
        // Add to the archive index *after* the archive exists and read-back succeeded.
        self.db.execute("INSERT INTO archives(id,path,sha256,bytes,verified,scope,exported_at)
            VALUES (?1,?2,?3,?4,1,?5,?6)",
            params![format!("{job}:{}",manifest.sha256),manifest.path,manifest.sha256,
                    i64::try_from(size).map_err(|_|Error::Invalid("archive too large".into()))?,
                    job,manifest.verified_at])?;
        let manifest_path=output.with_extension("manifest.json");
        let manifest_json=serde_json::to_vec_pretty(&manifest)?;
        let mut sidecar=OpenOptions::new().write(true).create_new(true).open(&manifest_path)?;
        sidecar.write_all(&manifest_json)?;
        sidecar.sync_all()?;
        Ok(manifest)
    }
}
