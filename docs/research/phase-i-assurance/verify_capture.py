#!/usr/bin/env python3
"""Independent file-set and SHA256 verification of a captured evidence manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HEX = re.compile(r"[0-9a-f]{64}\Z")

class CaptureMismatch(Exception):
    pass

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as stream:
        for part in iter(lambda:stream.read(65536),b""):
            h.update(part)
    return h.hexdigest()

def verify(root):
    root=Path(root).resolve()
    manifest_file=root/"manifest.json"
    if not manifest_file.is_file() or manifest_file.is_symlink():
        raise CaptureMismatch("missing/nonregular manifest")
    report=json.loads(manifest_file.read_text())
    recorded=report.get("artifacts")
    if not isinstance(recorded,list) or not recorded:
        raise CaptureMismatch("missing artifact index")
    actual={}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise CaptureMismatch("symlink evidence")
        if not path.is_file():
            continue
        name=path.relative_to(root).as_posix()
        if name=="manifest.json":
            continue
        if name in actual:
            raise CaptureMismatch("duplicate evidence path")
        actual[name]=path
    recorded_names=[]
    for item in recorded:
        if not isinstance(item,dict):
            raise CaptureMismatch("invalid artifact record")
        name=item.get("path")
        if not isinstance(name,str) or name.startswith("/") or "\\" in name or any(
            p in ("",".","..") for p in name.split("/")
        ):
            raise CaptureMismatch("unsafe artifact path")
        if name=="manifest.json":
            raise CaptureMismatch("manifest cannot hash itself")
        digest=item.get("sha256")
        if not isinstance(digest,str) or not HEX.fullmatch(digest):
            raise CaptureMismatch("malformed SHA256")
        if type(item.get("size")) is not int or item["size"]<0 or item.get("capture_complete") is not True:
            raise CaptureMismatch("invalid capture metadata")
        recorded_names.append(name)
    if len(set(recorded_names))!=len(recorded_names):
        raise CaptureMismatch("duplicate indexed path")
    if set(recorded_names)!=set(actual):
        raise CaptureMismatch("artifact set differs; missing="+str(sorted(set(recorded_names)-set(actual)))+
                              " unlisted="+str(sorted(set(actual)-set(recorded_names))))
    by_name={x["path"]:x for x in recorded}
    for name,path in actual.items():
        item=by_name[name]
        if path.stat().st_size!=item["size"] or sha(path)!=item["sha256"]:
            raise CaptureMismatch("artifact content differs: "+name)
    return {"verified":True,"file_count":len(actual),"manifest_file_set_exact":True,
            "archive_complete":False,"note":"SHA verification of local capture, not independent source authenticity"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directory")
    args=p.parse_args()
    print(json.dumps(verify(args.directory),sort_keys=True))
