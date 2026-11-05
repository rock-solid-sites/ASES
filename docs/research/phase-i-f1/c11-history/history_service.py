#!/usr/bin/env python3
"""Selected stable-field/retained-evidence profile over existing concrete holder."""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'c11-sqlite'))
import c11_service as c11

def validate_required(observations):
    if (not isinstance(observations,dict) or set(observations)!=set(c11.FIELDS)
            or not all(isinstance(observations[key],str) for key in c11.FIELDS)):
        raise ValueError('invalid required observation fields')

def enrich(profile):
    original_query=c11.query
    def query(db):
        current=original_query(db)
        rows=db.execute('SELECT accepted_content,record FROM consumer_archive ORDER BY accepted_content').fetchall()
        raw=[row[1] for row in rows]
        archived=[]
        for content,encoded in rows:
            record=json.loads(encoded,object_pairs_hook=c11.core.unique_object)
            if (not isinstance(record,dict) or set(record)!= {'accepted_content','required'}
                    or not isinstance(content,str) or record['accepted_content']!=content):
                raise ValueError('invalid accepted archive binding')
            validate_required(record['required']);archived.append(record)
        if profile=='archive':
            if current['accepted_content'] is not None:
                if (current['status']!='available' or dict(accepted_content=current['accepted_content'],required=current['required']) not in archived):
                    raise ValueError('current accepted observations unavailable from archive')
            records=archived
        else:
            records=[dict(accepted_content=current['accepted_content'],required=current['required'])] if current['status']=='available' else []
        return dict(current,retained_records=records,archive_rows_raw_hex=[row.encode().hex() for row in raw])
    c11.query=query

def serve(config):
    profile=config['retention_profile']
    if profile not in ('latest','archive'):raise ValueError('unknown selected retention profile')
    observations=config.get('observations')
    if observations is not None:validate_required(observations)
    original_store=c11.persistent.Store
    class Store(original_store):
        def __init__(self,*args):
            super().__init__(*args)
            self.db.execute('SELECT record FROM consumer_archive')
            c11.query(self.db)  # Validate existing semantic records before ready.
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
