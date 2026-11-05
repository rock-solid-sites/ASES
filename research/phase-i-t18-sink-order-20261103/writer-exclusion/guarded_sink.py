#!/usr/bin/env python3
"""Cooperative lifetime writer guard before original sink validation/serving."""
import fcntl
import http.server
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('guarded_original_sink',HERE.parent/'run.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

def serve(mode,journal):
    journal.parent.mkdir(parents=True,exist_ok=True)
    guard_path=journal.parent/'sink-writer.lock'
    fd=os.open(guard_path,os.O_RDWR|os.O_CREAT,0o600)
    stat=os.fstat(fd);guard=dict(path=str(guard_path),device=stat.st_dev,inode=stat.st_ino)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps(dict(ready=False,reason='writer-guard-busy',guard=guard)),flush=True);return 75
        try:state=base.SinkState(mode,journal)
        except (ValueError,OSError) as error:
            print(json.dumps(dict(ready=False,reason=str(error),error=type(error).__name__,guard=guard)),flush=True);return 1
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),base.make_handler(state));server.daemon_threads=True
        print(json.dumps(dict(ready=True,port=server.server_address[1],guard=guard)),flush=True)
        try:server.serve_forever(poll_interval=.05)
        finally:server.server_close()
    finally:os.close(fd)
    return 0

if __name__=='__main__':
    if len(sys.argv)!=4 or sys.argv[1]!='--server' or sys.argv[2] not in ('sink-ordered','recover-ordered'):
        raise SystemExit('usage: --server {sink-ordered,recover-ordered} JOURNAL')
    raise SystemExit(serve(sys.argv[2],Path(sys.argv[3])))
