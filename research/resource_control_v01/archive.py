"""Portable compressed and verified evidence bundles for controlled sessions."""
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path
from control import canonical, require_id, utc_now, Rejected


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(name):
    require_id(name, "artifact_name")
    if name.startswith(".") or "/" in name or chr(92) in name or ".." in name:
        raise ValueError("unsafe artifact name")
    return name


def verify(zip_path, manifest_path):
    try:
        m=json.loads(Path(manifest_path).read_text())
        raw=Path(zip_path).read_bytes()
        if m.get("schema")!=1 or m["archive_sha256"]!=sha(raw):
            raise ValueError("archive hash/schema mismatch")
        with zipfile.ZipFile(zip_path) as z:
            if sorted(z.namelist())!=sorted(m["files"]):
                raise ValueError("archive entries mismatch")
            for name, info in m["files"].items():
                safe(name)
                data=z.read(name)
                if len(data)!=info["size"] or sha(data)!=info["sha256"]:
                    raise ValueError("artifact hash/size mismatch: "+name)
        return {"verified":True,"job_id":m["job_id"],"files":sorted(m["files"])}
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,Rejected) as exc:
        return {"verified":False,"reason":str(exc)}


def archive(control, job_id, output_directory, *, artifacts=None):
    """Never claim completion before archive bytes and manifest are independently verified."""
    require_id(job_id,"job_id")
    root=Path(output_directory)
    root.mkdir(parents=True,exist_ok=True)
    events=control.events(job_id)
    record={"schema":1,"evidence_through":events[-1]["observed_at"] if events else None,
            "job":control.status(job_id),"events":events,
            "scope":"available local-control evidence, not all external transcripts"}
    files={"session.json":canonical(record).encode()}
    for name,data in (artifacts or {}).items():
        safe(name)
        if name in files or not isinstance(data,(bytes,bytearray)):
            raise ValueError("invalid artifact")
        files[name]=bytes(data)
    entries={name:{"size":len(blob),"sha256":sha(blob)} for name,blob in files.items()}
    identity=sha(canonical(entries).encode())[:20]
    dest=root/(job_id+"-"+identity+".zip")
    manifest=root/(job_id+"-"+identity+".manifest.json")
    if dest.exists() or manifest.exists():
        existing=verify(dest,manifest)
        if existing["verified"]:
            return {"archive":str(dest),"manifest":str(manifest),"duplicate":True,"verified":True}
        raise Rejected("ARCHIVE_CONFLICT")
    fd,temp=tempfile.mkstemp(dir=root,prefix=".archive-",suffix=".tmp")
    os.close(fd)
    try:
        with zipfile.ZipFile(temp,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(files.items()):
                z.writestr(name,data)
        metadata={"schema":1,"job_id":job_id,"files":entries,
                  "archive_sha256":sha(Path(temp).read_bytes())}
        temp_manifest=Path(temp+".manifest")
        try:
            with temp_manifest.open("w") as f:
                f.write(canonical(metadata)+"\n")
                f.flush()
                os.fsync(f.fileno())
            if not verify(temp,temp_manifest)["verified"]:
                raise Rejected("PRECOMMIT_ARCHIVE_VERIFY_FAILURE")
            os.replace(temp,dest)
            os.replace(temp_manifest,manifest)
        finally:
            temp_manifest.unlink(missing_ok=True)
        if not verify(dest,manifest)["verified"]:
            raise Rejected("ARCHIVE_VERIFY_FAILURE")
        return {"archive":str(dest),"manifest":str(manifest),
                "duplicate":False,"verified":True}
    finally:
        Path(temp).unlink(missing_ok=True)


def restore(zip_path,manifest_path,directory):
    result=verify(zip_path,manifest_path)
    if not result["verified"]:
        raise Rejected("ARCHIVE_NOT_VERIFIED",result["reason"])
    dest=Path(directory)
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        for name in result["files"]:
            safe(name)
            (dest/name).write_bytes(z.read(name))
    return result
