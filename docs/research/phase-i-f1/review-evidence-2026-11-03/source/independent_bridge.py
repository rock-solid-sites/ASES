import json, os, select, sqlite3, subprocess, sys, tempfile
CODE = r'''import json, os, sqlite3, sys
p, owner, variant = sys.argv[1:]
db=sqlite3.connect(p, isolation_level=None, timeout=4)
db.execute('PRAGMA synchronous=FULL')
print(json.dumps({'event':'ready','pid':os.getpid(),'owner':owner}),flush=True)
assert sys.stdin.readline().strip()=='start'
if variant=='detached':
 count=db.execute('SELECT count(*) FROM reservations').fetchone()[0]
 print(json.dumps({'event':'precheck','owner':owner,'count':count}),flush=True)
 assert sys.stdin.readline().strip()=='proceed'
db.execute('BEGIN IMMEDIATE')
if variant=='reference': count=db.execute('SELECT count(*) FROM reservations').fetchone()[0]
if count: db.execute('ROLLBACK'); print(json.dumps({'event':'denied','owner':owner,'count':count}),flush=True); sys.exit(0)
db.execute('INSERT INTO reservations VALUES (?)',(owner,)); db.execute('INSERT INTO effects VALUES (?)',(owner,)); db.execute('COMMIT')
print(json.dumps({'event':'committed','owner':owner,'count_seen':count}),flush=True)
assert sys.stdin.readline().strip()=='ack'
print(json.dumps({'event':'ack','owner':owner}),flush=True)
db.close()
'''
def msg(p):
 ready,_,_=select.select([p.stdout],[],[],4)
 if not ready: raise TimeoutError('child output')
 line=p.stdout.readline()
 if not line: raise RuntimeError('closed pipe')
 return json.loads(line)
def run(variant, root):
 path=root+'/'+variant+'.db'
 with sqlite3.connect(path) as d:
  d.execute('PRAGMA journal_mode=DELETE'); d.execute('CREATE TABLE reservations(owner TEXT)');d.execute('CREATE TABLE effects(owner TEXT)')
 ps=[subprocess.Popen([sys.executable,'-c',CODE,path,o,variant],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1) for o in ['C','S']]
 try:
  ready=[msg(p) for p in ps]
  for p in ps:p.stdin.write('start\n');p.stdin.flush()
  pre=[]
  if variant=='detached':
   pre=[msg(p) for p in ps]
   for p in ps:p.stdin.write('proceed\n');p.stdin.flush()
  decisions=[msg(p) for p in ps]
  with sqlite3.connect('file:'+path+'?mode=ro',uri=True,timeout=4) as d:
   store={'integrity':d.execute('PRAGMA integrity_check').fetchone()[0], 'reservations':sorted(x[0] for x in d.execute('SELECT owner FROM reservations')), 'effects':sorted(x[0] for x in d.execute('SELECT owner FROM effects'))}
  for p,e in zip(ps,decisions):
   if e['event']=='committed':p.stdin.write('ack\n');p.stdin.flush()
  acks=[msg(p) for p,e in zip(ps,decisions) if e['event']=='committed']
  exits=[p.wait(timeout=4) for p in ps]
  return {'ready':ready,'prechecks':pre,'decisions':decisions,'independent_read_only_pre_ack':store,'acks':acks,'exitcodes':exits}
 finally:
  for p in ps:
   if p.poll() is None:p.kill();p.wait(timeout=4)
   p.stdin.close();p.stdout.close();p.stderr.close()
with tempfile.TemporaryDirectory(prefix='independent-bridge-') as t:
 print(json.dumps({'reference':run('reference',t),'detached':run('detached',t),'sqlite':sqlite3.sqlite_version},sort_keys=True))
