#!/usr/bin/env python3
"""Selected stable-field/retained-evidence profile over existing concrete holder."""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'c11-sqlite'))
import c11_service as c11

def enrich(profile):
    original_query=c11.query
    def query(db):
        current=original_query(db)
        raw=[row[0] for row in db.execute('SELECT record FROM consumer_archive ORDER BY accepted_content')]
        if profile=='archive':records=[json.loads(row,object_pairs_hook=c11.core.unique_object) for row in raw]
        else:
            records=[dict(accepted_content=current['accepted_content'],required=current['required'])] if current['status']=='available' else []
        return dict(current,retained_records=records,archive_rows_raw_hex=[row.encode().hex() for row in raw])
    c11.query=query

def serve(config):
    profile=config['retention_profile']
    if profile not in ('latest','archive'):raise ValueError('unknown selected retention profile')
    observations=config.get('observations')
    original_store=c11.persistent.Store
    class Store(original_store):
        def __init__(self,*args):
            super().__init__(*args)
            self.db.execute('SELECT record FROM consumer_archive')
        def write(self,state):
            super().write(state)
            if profile!='archive' or observations is None or state.content is None:return
            record=json.dumps(dict(accepted_content=state.content,required=observations),sort_keys=True)
            existing=self.db.execute('SELECT record FROM consumer_archive WHERE accepted_content=?',(state.content,)).fetchone()
            if existing is None:
                self.db.execute('INSERT INTO consumer_archive(accepted_content,record) VALUES(?,?)',(state.content,record))
            elif existing[0]!=record:
                raise ValueError('conflicting accepted consumer observation binding')
    c11.persistent.Store=Store
    enrich(profile)
    c11.serve(config)

if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--reader':
        enrich(sys.argv[3]);c11.reader(sys.argv[2])
    else:serve(json.loads(sys.argv[1]))
