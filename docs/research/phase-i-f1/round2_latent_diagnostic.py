#!/usr/bin/env python3
"""Named original C8 predicate witness plus descendant/relocation controls."""
from dataclasses import asdict,replace
import hashlib,json,platform,resource,subprocess,sys
from pathlib import Path
import phase_i_f1_model as m
HERE=Path(__file__).resolve().parent
PREFIX=[('grant',m.P,m.SINK,m.R),('grant',m.C,m.SINK,m.RW),('seal',m.C),('move',m.C,m.Q)]
TAIL=[('grant',m.Q,m.SINK,m.RW),('activate',m.C),('grant',m.D,m.SINK,m.RW),('use',m.D,m.SINK,m.W,m.B_GEN),
      ('grant',m.D,m.SINK,m.R),('use',m.D,m.SINK,m.R,m.B_GEN),('seal',m.D),('move',m.D,m.P),('activate',m.D),
      ('grant',m.P,m.SINK,m.RW),('grant',m.D,m.SINK,m.RW),('use',m.D,m.SINK,m.W,m.B_GEN),('use',m.D,m.SINK,m.R,m.B_GEN)]

def run(profile,events,observe_at=None):
    s=m.initial();trace=[];checkpoint=None
    for index,event in enumerate(events):
        before=s;guard=m.guard(s,event,profile)
        oracle=m.oracle_use_permitted(s,event[1],event[2],event[3],event[4],profile) if event[0]=='use' else None
        outcome,s,reason=m.resolve(s,event,profile)
        trace.append(dict(event=event,outcome=outcome,reason=reason,guard_reason=guard,oracle_allowed=oracle,
                          invariant=m.invariant(s,profile),state=asdict(s)))
        assert outcome in ('commit','deny') and m.invariant(s,profile) is None
        if event[0]=='use':assert oracle==(guard is None)==(outcome=='commit')
        if outcome=='deny':assert s==before
        if index==observe_at:
            helper=next(c for c in m.semantic_checks({m.key(s):m.Node(tuple(events[:index+1]),s)},[]) if c['clause']=='C8')
            checkpoint=dict(state=asdict(s),D_local=m.get(s.wu(m.D).latent,m.SINK),D_effective=m.latent_chain(s,m.D,m.SINK),
                            C_local=m.get(s.wu(m.C).latent,m.SINK),original_C8_helper=helper)
    return dict(profile=profile.__dict__,trace=trace,checkpoint=checkpoint)

def main():
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,)*2)
    reference=run(m.REFERENCE,PREFIX+TAIL,len(PREFIX)-1)
    mutant=run(replace(m.REFERENCE,name='weak-latent-retention',latent_preserved=False),PREFIX+TAIL,len(PREFIX)-1)
    positive=run(m.REFERENCE,[('grant',m.P,m.SINK,m.RW),('grant',m.C,m.SINK,m.RW),('grant',m.D,m.SINK,m.RW),('use',m.D,m.SINK,m.W,m.B_GEN)])
    assert all(row['outcome']=='commit' for row in reference['trace'][:4])
    assert reference['checkpoint']['D_local']==m.RW and reference['checkpoint']['D_effective']==m.R
    assert reference['checkpoint']['original_C8_helper']['passed'] is False
    writes=lambda case:[row['outcome'] for row in case['trace'] if row['event'][0]=='use' and row['event'][3]==m.W]
    reads=lambda case:[row['outcome'] for row in case['trace'] if row['event'][0]=='use' and row['event'][3]==m.R]
    assert writes(reference)==['deny','deny'] and writes(mutant)==['commit','commit']
    assert reads(reference)==reads(mutant)==['commit','commit'] and writes(positive)==['commit']
    print(json.dumps(dict(schema='ases.f1-latent-predicate-witness.v1',execution_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                         source_hashes={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('round2_latent_diagnostic.py','phase_i_f1_model.py')},
                         environment=dict(platform=platform.platform(),python=sys.version,executable=sys.executable,executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()),
                         cases=dict(reference=reference,weak_mutation=mutant,unrestricted_positive=positive),
                         qualification='specific stored-local predicate failure contrasted with effective path use/regrant/relocation; no universal C8 proof or canonical checker repair'),indent=2,sort_keys=True))
if __name__=='__main__':main()
