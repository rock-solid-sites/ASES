#!/usr/bin/env python3
"""Bounded exclusive RTL sequences with independent-profile negative control."""
import argparse,collections,itertools,json,resource,time
from pathlib import Path
import rtl_short_sequences as base
t=base.t;m=base.m;Q=base.Q;c=base.c;D=base.D;TOOL=base.TOOL;ACTIONS=base.ACTIONS;run=base.run;hashes=base.hashes
WORK=Path('/tmp/ases-kernel-exclusive-rtl');WORK.mkdir(exist_ok=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--case-cap',type=int,default=216);a=ap.parse_args()
 if not 1<=a.case_cap<=216:ap.error('case cap 1..216')
 t0=time.monotonic();before=hashes();p=t.PROFILES[2];lines=[];manifest=[];counts=collections.Counter()
 for order in itertools.product(range(6),repeat=3):
  if len(manifest)>=a.case_cap:
   print(json.dumps({'status':'incomplete','cases':len(manifest),'next':{'profile':p.name,'action_indices':order,'actions':[ACTIONS[i][0] for i in order]},'simulation':'not_run'},sort_keys=True));return 2
  s=m.State();lines.append('1 1 7fff 000000 0 0');outcomes=[]
  for i,q in enumerate([Q('establish'),Q('grant',target=0,value=7)]+[ACTIONS[j][1] for j in order]):
   prior=s;s,kind=m.resolve(s,q,p);m.check_edge(prior,q,s,kind,p)
   if i>=2:
    label=ACTIONS[order[i-2]][0];counts[f'action/{label}/{kind}']+=1
    old='linked' if prior.parents[3]>=0 else 'none';new='linked' if s.parents[3]>=0 else 'none';counts[f'parent/{old}_to_{new}']+=1
   lines.append(f'0 1 {c.encode_request(q):04x} {c.encode_state(s):06x} 1 {int(kind=="commit")}');outcomes.append(kind)
  manifest.append({'actions':[ACTIONS[j][0] for j in order],'outcomes':outcomes,'first_cycle':len(lines)-6})
 assert len(manifest)==216 and len(lines)==1296
 assert counts['action/grant3/commit']>0 and counts['action/grant3/deny']>0 and counts['parent/none_to_none']==648
 positive=WORK/'exclusive.vectors';positive.write_text('\n'.join(lines)+'\n');badlines=lines.copy();parts=badlines[1].split();parts[3]=f'{int(parts[3],16)^2:06x}';badlines[1]=' '.join(parts);badfile=WORK/'bad.vectors';badfile.write_text('\n'.join(badlines)+'\n')
 builds={};runs={};ivl=TOOL/'lib/x86_64-linux-gnu/ivl'
 for exclusive in (1,0):
  exe=WORK/f'profile-{exclusive}.vvp';comp=run([TOOL/'bin/iverilog','-B',ivl,'-g2012','-s','sequence_tb','-P',f'sequence_tb.EXCLUSIVE={exclusive}','-o',exe,D/'kernel0.v',D/'sequence_tb.v']);assert comp['exit']==0,comp;builds[str(exclusive)]=comp
  runs[str(exclusive)]=run([TOOL/'bin/vvp',exe,f'+vectors={positive}'])
 bad=run([TOOL/'bin/vvp',WORK/'profile-1.vvp',f'+vectors={badfile}']);assert runs['1']['exit']==0 and 'PASS sequential cycles=1296' in runs['1']['output'];assert runs['0']['exit']!=0 and 'sequence=' in runs['0']['output'];assert bad['exit']!=0 and 'sequence=1' in bad['output']
 after=hashes();assert before==after
 print(json.dumps({'status':'complete_bounded','cases':len(manifest),'cycles':len(lines),'counts':dict(sorted(counts.items())),'vectors':positive.read_text(),'manifest':manifest,'compile':builds,'profile_runs':runs,'corrupt_expected':bad,'source_before':before,'source_after':after,'base_harness_sha256':__import__('hashlib').sha256(Path(base.__file__).read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-t0,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
