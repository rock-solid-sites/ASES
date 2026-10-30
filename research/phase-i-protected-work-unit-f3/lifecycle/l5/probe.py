#!/usr/bin/env python3
"""L5 blocker probe: check supported mediator surface and actual direct-write route."""
import ctypes,json,os,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'l1'))
import l1
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'l4'))
import l4
HERE=Path(__file__).resolve().parent; LAB=HERE.parent/'l4'/'lab'; STATE=LAB/'protected'
DIRECT=r'''import errno,json,os,sys
p=sys.argv[1]
try: fd=os.open(p,os.O_WRONLY); os.close(fd); print(json.dumps({'result':'allowed'}))
except OSError as e: print(json.dumps({'result':'denied','errno':e.errno,'error':e.strerror}))
'''
def main():
 selector=(STATE/'CURRENT').read_text().strip(); rec=json.loads((STATE/selector).read_text()); units=rec['work_units']; obj=STATE/units['C']['accepted_contents'][0]['object']; ops=sorted(set(re.findall(r"q\.get\('op'\)=='([^']+)'",l4.AUTH2))); p=subprocess.run([sys.executable,'-S','-c',DIRECT,str(obj)],capture_output=True,text=True,timeout=3,preexec_fn=l1.confine,close_fds=True,check=True); direct=json.loads(p.stdout)
 out={'status':'l5-obstruction','current_record':selector,'current_ingress':rec.get('current_ingress'),'P':units['P'],'C_grants':units['C']['grants'],'Q_present':'Q' in units,'mediator_supported_ops':ops,'write_operation_supported':any('write' in x for x in ops),'direct_open_accepted_object_O_WRONLY':direct,'direct_write_denial_is_parent_ceiling_evidence':False,'disposition':'STOP L5: selected attachment profile has no mediated write effect; direct Landlock EACCES is unconditional and cannot distinguish preservation of P latent write ceiling after a permissive-parent move. Do not invent a write primitive or report latent-rights success.'}
 out['pass_obstruction']=not out['write_operation_supported'] and not out['Q_present'] and direct.get('result')=='denied' and direct.get('errno')==13
 (HERE/'raw-run.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n'); print(json.dumps(out,sort_keys=True,indent=2))
 if not out['pass_obstruction']: raise SystemExit(1)
if __name__=='__main__': main()