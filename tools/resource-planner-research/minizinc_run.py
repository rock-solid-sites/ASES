"""MiniZinc runner. Supports bundled Gecode and Chuffed independently."""
import sys,json,time,subprocess,tempfile,os,re
from pathlib import Path
from common import load,report

def run(m,solver='gecode',time_limit=3.0):
    names=list(m['stages']);rn=list(m['resources']);n=len(names);r=len(rn)
    if any(not m['stages'][x]['modes'] for x in names):return None,'INFEASIBLE','preflight',{}
    kmax=max(len(m['stages'][x]['modes']) for x in names)
    horizon=sum(max(mo['duration'] for mo in st['modes'])+st.get('transferMinutesIfMoved',0) for st in m['stages'].values())+1
    mode_r=[];mode_d=[];mode_c=[];counts=[]
    for x in names:
        mods=m['stages'][x]['modes'];counts.append(len(mods))
        for idx in range(kmax):
            mo=mods[min(idx,len(mods)-1)];mode_r.append(rn.index(mo['resource'])+1);mode_d.append(mo['duration']);mode_c.append(mo.get('costCents',0))
    fmt=lambda x:'['+','.join(str(z).lower() if isinstance(z,bool) else str(z) for z in x)+']'
    deps=[p in m['stages'][z].get('after',[]) for p in names for z in names]
    indep=[(p in m['stages'][z].get('independentFrom',[])) or (z in m['stages'][p].get('independentFrom',[])) for p in names for z in names]
    def arr2(seq):return f'array2d(1..{n},1..{kmax},{fmt(seq)})'
    text='\n'.join([f'n={n};',f'r={r};',f'kmax={kmax};',f'horizon={horizon};',f'budget={m["budgetCents"]};','kcount='+fmt(counts)+';','mode_resource='+arr2(mode_r)+';','mode_duration='+arr2(mode_d)+';','mode_cost='+arr2(mode_c)+';','quota='+fmt([m['resources'][x]['quotaMinutes'] for x in rn])+';','depends='+f'array2d(1..{n},1..{n},{fmt(deps)});','independent='+f'array2d(1..{n},1..{n},{fmt(indep)});','move_penalty='+fmt([m['stages'][x].get('transferMinutesIfMoved',0) for x in names])+';'])
    with tempfile.TemporaryDirectory() as td:
        dzn=Path(td)/'data.dzn';dzn.write_text(text)
        cmd=['minizinc','--solver',solver,'--time-limit',str(int(time_limit*1000)),str(Path(__file__).parent/'scheduling.mzn'),str(dzn)]
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=time_limit+20)
    if p.returncode and ('UNSATISFIABLE' not in p.stdout):return None,'ERROR','none',{'stderr':p.stderr[-1000:],'returncode':p.returncode}
    match=re.search(r'RESULT\s+(\d+)\|(\[[^]]+\])\|(\[[^]]+\])',p.stdout)
    optimal='==========' in p.stdout
    if not match:
        if 'UNSATISFIABLE' in p.stdout:return None,'INFEASIBLE','proven',{}
        return None,'UNKNOWN','bounded',{'stderr':p.stderr[-600:],'stdout':p.stdout[-600:]}
    starts=[int(k.strip()) for k in match.group(2)[1:-1].split(',')];choices=[int(k.strip())-1 for k in match.group(3)[1:-1].split(',')]
    plans={}
    for i,n in enumerate(names):
        idx=choices[i];mo=m['stages'][n]['modes'][idx];plans[n]=(mo['resource'],starts[i],starts[i]+mo['duration'],idx)
    return plans,'OPTIMAL' if optimal else 'FEASIBLE_NOT_PROVEN','proven' if optimal else 'bounded',{'solver':solver}

if __name__=='__main__':
    m=load(sys.argv[1]);solver=sys.argv[2] if len(sys.argv)>2 else 'gecode';t=time.perf_counter()
    plans,status,guar,extra=run(m,solver)
    print(json.dumps(report(m,'minizinc-'+solver,plans,(time.perf_counter()-t)*1000,status,guar,extra)))
