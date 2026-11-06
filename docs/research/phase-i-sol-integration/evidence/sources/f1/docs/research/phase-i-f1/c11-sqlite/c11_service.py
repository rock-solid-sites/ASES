#!/usr/bin/env python3
"""Selected concrete C11 observation storage experiment, not a canonical schema."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'kernel-0'))
import kernel0_recovery_service as persistent
import kernel0_service as core
FIELDS=('identity_genesis','created_by','project','consumer_evidence')

class Trace:
    def __init__(self,db,path):self.db,self.path=db,path
    @property
    def in_transaction(self):return self.db.in_transaction
    def execute(self,sql,*args):
        start=time.monotonic_ns()
        result=self.db.execute(sql,*args)
        if sql.split()[0] in ('BEGIN','UPDATE','INSERT','COMMIT','ROLLBACK'):
            with self.path.open('a') as stream:
                stream.write(json.dumps(dict(sql=sql.split()[0],start_ns=start,end_ns=time.monotonic_ns(),
                                             in_transaction=self.db.in_transaction,pid=os.getpid()))+'\n')
        return result

def query(db):
    content=json.loads(db.execute('SELECT view FROM kernel WHERE id=1').fetchone()[0])['content']
    row=db.execute('SELECT record FROM consumer_observations WHERE id=1').fetchone()
    if row is None:
        return dict(status='not_accepted' if content is None else 'missing_required_observations',accepted_content=content,required=None)
    record=json.loads(row[0],object_pairs_hook=core.unique_object)
    if (set(record)!= {'accepted_content','required'} or not isinstance(record['accepted_content'],str)
            or not isinstance(record['required'],dict) or set(record['required'])!=set(FIELDS)
            or not all(isinstance(record['required'][key],str) for key in FIELDS)):
        raise ValueError('incompatible accepted observation record')
    if record['accepted_content']!=content:
        return dict(status='incompatible_required_observations',accepted_content=content,required=None,
                    stored_content=record['accepted_content'])
    return dict(status='available',**record)

def serve(config):
    observations=config.get('observations')
    mode=config['observation_mode']
    original=persistent.Store
    class ObservedStore(original):
        def __init__(self,*args):
            super().__init__(*args)
            self.db.execute('SELECT record FROM consumer_observations WHERE id=1')
            self.db=Trace(self.db,Path(config['trace']))
        def write_observations(self,content):
            record=json.dumps(dict(accepted_content=content,required=observations),sort_keys=True)
            self.db.execute('INSERT INTO consumer_observations(id,record) VALUES(1,?) '
                            'ON CONFLICT(id) DO UPDATE SET record=excluded.record',(record,))
        def write(self,state):
            super().write(state)
            if mode=='atomic' and observations is not None and state.content is not None:
                self.write_observations(state.content)
    persistent.Store=ObservedStore
    class Boundary(persistent.Boundary):
        def resolve(self,context,q,gate):
            result=super().resolve(context,q,gate)
            if mode=='split' and observations is not None and q is not None and q.kind=='accept' and result['outcome']=='commit':
                db=self.store.db
                db.execute('BEGIN IMMEDIATE')
                self.store.write_observations(result['state']['content'])
                db.execute('COMMIT')
            return dict(result,consumer_query=query(self.store.db))
    persistent.serve(config,Boundary(config))

def reader(path):
    with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) as db:
        raw_view=db.execute('SELECT view FROM kernel WHERE id=1').fetchone()[0].encode()
        row=db.execute('SELECT record FROM consumer_observations WHERE id=1').fetchone()
        raw_record=row[0].encode() if row else None
        print(json.dumps(dict(pid=os.getpid(),integrity=db.execute('PRAGMA integrity_check').fetchone()[0],
                              query=query(db),view=json.loads(raw_view),view_utf8_hex=raw_view.hex(),
                              view_sha256=hashlib.sha256(raw_view).hexdigest(),
                              observation_utf8_hex=None if raw_record is None else raw_record.hex(),
                              observation_sha256=None if raw_record is None else hashlib.sha256(raw_record).hexdigest()),sort_keys=True))

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--reader':reader(sys.argv[2])
    else:serve(json.loads(sys.argv[1]))
