"""Run the same research fixtures across implementations; log machine-specific evidence.
No provider accounts. No claim that partial test coverage proves production fitness.
"""
from __future__ import annotations
import subprocess,sys,json,time,platform,os
from pathlib import Path
from common import load,ModelError
ROOT=Path(__file__).parent

def exe(args):
    command=['/usr/bin/time','-f','RESEARCH_PEAK_RSS_KB=%M',*args]
    start=time.perf_counter()
    p=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
    elapsed=round((time.perf_counter()-start)*1000,2)
    rss=None
    for line in p.stderr.splitlines():
        if line.startswith('RESEARCH_PEAK_RSS_KB='):rss=int(line.split('=')[1])
    if p.returncode:
        return {'status':'PROCESS_FAILED','exitCode':p.returncode,'cmd':args,'stderr':p.stderr[-1200:],'stdout':p.stdout[-600:],'wallMs':elapsed,'peakRssKb':rss}
    try: result=json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:return {'status':'PARSE_FAILED','error':str(e),'stdout':p.stdout[-1000:],'stderr':p.stderr[-1200:]}
    result['wallProcessMs']=elapsed;result['peakRssKb']=rss
    return result

def main():
    result={'environment':{'platform':platform.platform(),'python':platform.python_version(),'cpuCount':os.cpu_count(),'miniZincVersion':None,'ortoolsVersion':None},'runs':[]}
    v=subprocess.run(['minizinc','--version'],capture_output=True,text=True)
    result['environment']['miniZincVersion']=v.stdout.strip().splitlines()[0] if v.returncode==0 else 'NOT INSTALLED'
    try:
        import ortools
        result['environment']['ortoolsVersion']=ortools.__version__
    except ImportError:result['environment']['ortoolsVersion']='NOT INSTALLED'
    tools=[('exact',lambda f:[sys.executable,'exact.py',str(f),'50000']),('ortools-cpsat',lambda f:[sys.executable,'cpsat.py',str(f),'3.0']),('minizinc-gecode',lambda f:[sys.executable,'minizinc_run.py',str(f),'gecode']),('minizinc-chuffed',lambda f:[sys.executable,'minizinc_run.py',str(f),'chuffed'])]
    all_ok=True
    for f in sorted((ROOT/'fixtures').glob('*.json')):
        name=f.stem
        if name.startswith('F09'):
            try:
                load(f); report={'status':'ERROR_EXPECTED_INVALID_NOT_DETECTED'};all_ok=False
            except (ModelError,ValueError,TypeError) as e: report={'status':'REJECTED_INVALID_INPUT','reason':str(e)}
            result['runs'].append({'fixture':name,'backend':'preflight','result':report})
            continue
        m=load(f)
        for tool,cmd in tools:
            if tool=='exact' and len(m['stages'])>8:
                report={'status':'SKIPPED_TOO_LARGE','nodesLimit':50000}
            else:
                report=exe(cmd(f))
            result['runs'].append({'fixture':name,'backend':tool,'result':report})
            expect=json.loads(f.read_text()).get('expect')
            if report['status'] in ('PROCESS_FAILED','PARSE_FAILED','ERROR','MODEL_INVALID'):
                all_ok=False
            if expect and 'makespan' in expect and report['status']=='OPTIMAL' and report.get('makespan')!=expect['makespan']:
                all_ok=False;report['unexpectedMakespan']=expect['makespan']
            if expect and expect['status']=='INFEASIBLE' and report['status']!='INFEASIBLE':
                all_ok=False;report['unexpectedStatus']=expect['status']
            if expect and expect.get('resource') and report['status']=='OPTIMAL' and report['placements']['build']['resource']!=expect['resource']:
                all_ok=False;report['unexpectedResource']=expect['resource']
            print(f'{name:27s} {tool:17s} {report["status"]:23s} ms={report.get("wallProcessMs","-")} rss={report.get("peakRssKb","-")} objective={report.get("makespan","-")}',flush=True)
    result['allPass']=all_ok
    (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SUMMARY',json.dumps({'allPass':all_ok,'tests':len(result['runs']),'environment':result['environment']}))
    sys.exit(0 if all_ok else 1)
if __name__=='__main__':main()
