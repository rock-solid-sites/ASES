"""Deterministically build solver-neutral research fixtures, no provider accounts."""
from pathlib import Path
import json,random
ROOT=Path(__file__).parent/'fixtures';ROOT.mkdir(exist_ok=True)
def res(id,domain='ases',quota=500,ram=8,availability='verified'):
 return dict(id=id,account='synthetic:'+domain,domain=domain,ramGiB=ram,quotaMinutes=quota,availability=availability)
def mode(r,d,c=0):return dict(resource=r,duration=d,costCents=c)
def st(id,after=(),modes=(),**kwargs):return dict(id=id,after=list(after),modes=list(modes),**kwargs)
def write(name,r,stages,budget=100000,domain='ases',expect=None):
 o=dict(version=1,name=name,domain=domain,resources=r,stages=stages,budgetCents=budget)
 if expect:o['expect']=expect
 (ROOT/(name+'.json')).write_text(json.dumps(o,indent=2)+'\n')
write('F01-priority-reordering',[res('r1'),res('r2')],[st('A',modes=[mode('r1',30)]),st('B',modes=[mode('r1',2)]),st('C',after=['B'],modes=[mode('r2',20)])],expect={'status':'OPTIMAL','makespan':32})
write('F02-identity-isolation',[res('ases-host'),res('hms-host','hms')],[st('build',modes=[mode('hms-host',1),mode('ases-host',7)])],expect={'status':'OPTIMAL','makespan':7,'resource':'ases-host'})
write('F03-independent-review',[res('r1'),res('r2')],[st('build',modes=[mode('r1',5),mode('r2',5)]),st('review',after=['build'],modes=[mode('r1',4),mode('r2',4)],independentFrom=['build'])],expect={'status':'OPTIMAL','makespan':9})
write('F04-downstream-transfer',[res('r1',ram=32),res('r2',ram=8)],[st('prep',modes=[mode('r1',3),mode('r2',1)]),st('heavy',after=['prep'],modes=[mode('r1',10)],minRamGiB=32,transferMinutesIfMoved=20)],expect={'status':'OPTIMAL','makespan':13})
write('F05-co-location',[res('warm-r1'),res('cold-r2')],[st('setup',modes=[mode('warm-r1',6),mode('cold-r2',2)]),st('test',after=['setup'],modes=[mode('warm-r1',5)],transferMinutesIfMoved=15)],expect={'status':'OPTIMAL','makespan':11})
write('F06-quota-capacity',[res('r1',quota=8),res('r2',quota=8)],[st('a',modes=[mode('r1',6),mode('r2',7)]),st('b',modes=[mode('r1',6),mode('r2',7)])],expect={'status':'OPTIMAL','makespan':7})
write('F08-retired-rejected',[res('retired','ases',availability='retired')],[st('only',modes=[mode('retired',3)])],expect={'status':'INFEASIBLE'})
# Small combinatorial workloads, reproducible and not connected to actual prices/quotas.
for n, nr in [(12,5),(30,10)]:
 rng=random.Random(3100+n)
 rs=[res('machine'+str(k),quota=1000,ram=16 if k%4==0 else 8) for k in range(nr)]
 stages=[]
 for i in range(n):
  first=f'machine{i%nr}'; second=f'machine{(i+2)%nr}'
  after=[f't{i-3}'] if i>=3 else []
  if i>=6 and i%5==0:after.append(f't{i-5}')
  modes=[mode(first,rng.randint(2,8),0),mode(second,rng.randint(3,11),rng.randint(0,8))]
  stages.append(st('t'+str(i),after=after,modes=modes,transferMinutesIfMoved=(2 if i%4==0 else 0)))
 write(f'F{11 if n==12 else 12}-{n}-stage',rs,stages)
# Deliberate syntactically valid, semantically invalid source input.
(ROOT/'F09-invalid-input.json').write_text('''{"version":1,"name":"invalid-input","domain":"ases","resources":[{"id":"r1","account":"a","domain":"ases","ramGiB":8,"quotaMinutes":50,"availability":"verified"}],"stages":[{"id":"bad","after":[],"modes":[{"resource":"r1","duration":-9,"costCents":0}]}]}''')
print('Wrote',len(list(ROOT.glob('*.json'))),'fixtures')
