#!/usr/bin/env python3
"""Dependency-free structural/semantic validation, including pinned artifact digests."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
STATUSES={'executed_observed','independently_reproduced','source_reviewed_only','preregistered_not_executed','blocked_environment','timed_out_inconclusive','falsified_counterexample'}

def validate(d, artifacts=True):
    assert d['schema']=='ases.autonomy.experiment-index' and d['schema_version']==1
    assert d['usage']['remaining']=='unknown' or isinstance(d['usage']['remaining'],dict)
    assert abs(sum(d['usage']['allocation_targets'].values())-1)<1e-9
    assert all(re.fullmatch('[a-f0-9]{40}',s) for s in d['branch_tips'].values())
    ids=set()
    for e in d['experiments']:
        for key in ['id','stream','claim','source_branch','source_sha','implementation','command','environment','status','observed_result','limits','raw_evidence','reviewers','dependencies','blockers','next_discriminator','supersedes']:
            assert key in e, (e.get('id'),key)
        assert e['id'] not in ids; ids.add(e['id'])
        assert e['status'] in STATUSES
        assert re.fullmatch('[a-f0-9]{40}',e['source_sha'])
        assert all(isinstance(e[k],list) for k in ['raw_evidence','reviewers','dependencies','blockers','supersedes'])
        if e['status'] in {'executed_observed','independently_reproduced','falsified_counterexample'}:
            assert e['raw_evidence'] and e['command'] and e['observed_result']
        for r in e['reviewers']:
            assert re.fullmatch('[a-f0-9]{40}',r['sha']) and r['branch'] and r['independence']
        for a in e['raw_evidence']:
            assert re.fullmatch('[a-f0-9]{64}',a['sha256'])
            assert not Path(a['path']).is_absolute() and '..' not in Path(a['path']).parts
            if artifacts:
                raw=subprocess.check_output(['git','show',e['source_sha']+':'+a['path']])
                assert hashlib.sha256(raw).hexdigest()==a['sha256'],a
    return len(ids)

if __name__=='__main__':
    d=json.loads((ROOT/'experiment-index.json').read_text())
    count=validate(d)
    for mutate in ['duplicate','invalid_status','missing_digest']:
        import copy
        bad=copy.deepcopy(d)
        if mutate=='duplicate': bad['experiments'].append(bad['experiments'][0])
        elif mutate=='invalid_status': bad['experiments'][0]['status']='passed_all_phase_i'
        else: del bad['experiments'][0]['raw_evidence'][0]['sha256']
        try: validate(bad,False)
        except (AssertionError,KeyError): pass
        else: raise AssertionError('invalid index accepted: '+mutate)
    print(f'VALID: {count} experiments; pinned digests verified; 3 invalid-index controls rejected')
