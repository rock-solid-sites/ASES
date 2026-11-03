import importlib.util, json, shutil, tempfile, os
from pathlib import Path
p=Path('' + os.environ['ASES_F3_EVIDENCE_COPY'] + '/lifecycle/l5/l5_integrated.py')
s=p.read_text()
s=s.replace("else:\n  # Positive control has separately", "if move and not mutant:\n  st['work_units']['Q']['active']=False; st['work_units']['Q']['sealed']=True\n  commit(root,st,{'op':'test-seal-ancestor'})\n else:\n  # Positive control has separately")
# Keep original conditional structure; inject immediately before worker instead.
s=p.read_text().replace("if not graph_valid(st): raise AssertionError('post-transition graph invalid')", "if move and not mutant:\n  st['work_units']['Q']['active']=False; st['work_units']['Q']['sealed']=True\n  commit(root,st,{'op':'test-seal-ancestor'})\n if not graph_valid(st): raise AssertionError('post-transition graph invalid')")
mut=p.with_name('test_ancestor.py'); mut.write_text(s)
spec=importlib.util.spec_from_file_location('test_ancestor',mut); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
fixture=Path('' + os.environ['ASES_F3_EVIDENCE_COPY'] + '/lifecycle/l4')
def bootstrap():
 t=Path(tempfile.mkdtemp(prefix='ases-policy-')); root=t/'l4'/'lab'; root.parent.mkdir(); shutil.copytree(fixture/'lab',root); shutil.copy2(fixture/'raw-run.json',root.parent/'raw-run.json')
 name,st=m.load_current(root)
 st['work_units']['P'].update(parent=None,grants=['read']); st['work_units']['C'].update(parent='P',grants=['read','write'],active=False)
 st['work_units']['Q']={'id':'Q','parent':None,'active':False,'sealed':True,'grants':['read','write'],'accepted_contents':[]}
 y=st['work_units']['C']['accepted_contents'][-1]
 st['work_units']['D']={'id':'D','parent':'C','depends_on':['C'],'active':False,'sealed':True,'grants':['read','write'],'accepted_contents':[y]}
 for u in st['work_units'].values(): u.update(active=False,sealed=True)
 st['current_ingress']=None
 new,_=m.commit(root,st,{'op':'test-bootstrap'})
 return t,root,new,'',''
m.l4_bootstrap=bootstrap
m.l1.confine=lambda: None
for label,move,mutant in [('positive',False,False),('sealed-ancestor',True,False),('unsafe-ceiling',True,True)]:
 c=m.run_case(label,['read'],move,mutant)
 print(json.dumps({'case':label,'observation':c['worker_observation'],'checks':c['mediator_checks'],'effect_count':len(c['effects'])},sort_keys=True))
