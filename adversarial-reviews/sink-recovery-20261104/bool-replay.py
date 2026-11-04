import hashlib, json, pathlib, select, subprocess, sys, tempfile
source = pathlib.Path('research/phase-i-t18-sink-order-20261103/run.py').resolve()
event = {'seq':1,'event':'effect_accepted','request_id':'r','payload':'x','presented_version':True,'accepted_under_version':True,'check_mode':'sink-ordered'}
raw = (json.dumps(event,sort_keys=True)+'\n').encode()
with tempfile.TemporaryDirectory(prefix='sink-bool-review-') as d:
    journal=pathlib.Path(d)/'journal.jsonl'
    journal.write_bytes(raw)
    p=subprocess.Popen([sys.executable,str(source),'--server','recover-ordered',str(journal)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        ready=select.select([p.stdout],[],[],3)[0]
        line=p.stdout.readline().strip() if ready else ''
    finally:
        if p.poll() is None: p.kill()
        stdout,stderr=p.communicate(timeout=3)
    print(json.dumps({'command':[sys.executable,str(source),'--server','recover-ordered','<temporary>/journal.jsonl'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'journal_utf8':raw.decode(),'journal_sha256':hashlib.sha256(raw).hexdigest(),'first_stdout_line':line,'remaining_stdout':stdout,'stderr':stderr,'process_returncode':p.returncode,'killed_after_ready':bool(line)},indent=2))
