#!/usr/bin/env python3
"""Read-only audit of the bounded C11 holder probe output."""
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_hex(raw):
    return hashlib.sha256(raw).hexdigest()


def audit(path):
    data = json.loads(Path(path).read_text())
    cases = data['cases']
    require(data['schema'] == 'ases.f1-c11-sqlite-history' and data['version'] == 1,
            'unexpected probe format')
    source_base = Path('docs/research')
    for rel, expected in data['source_hashes'].items():
        require(digest_hex((source_base / rel).read_bytes()) == expected,
                f'source digest mismatch: {rel}')
    service_source = (source_base / 'phase-i-f1/c11-sqlite/c11_service.py').read_text()
    probe_source = (source_base / 'phase-i-f1/c11-sqlite/probe.py').read_text()
    require('ON CONFLICT(id) DO UPDATE SET record=excluded.record' in service_source,
            'singleton observation-row replacement behavior changed')
    require("WORLDS={name:dict(identity_genesis='genesis-'+name,created_by='creator-'+name,project='project-'+name," in probe_source,
            'opaque per-world identity fixture not found')

    bootstrap_bundle = None
    views = {}
    outcomes = {}
    for name, case in cases.items():
        writer, accept, gate = case['writer'], case['accept'], case['gate']
        recovery = case['recovered']
        recovery_call = case['recovered_query']
        independent = case['independent_reader']
        require('observations' not in recovery['config'], f'{name}: recovery received source tuple')
        require(writer['config'].get('observations') == case['declared_original_observations'],
                f'{name}: writer tuple differs from declared fixture')
        require(all(x['response']['outcome'] == 'commit' for x in case['bootstrap']['calls']),
                f'{name}: bootstrap did not receive successful acknowledgements')
        require(writer['pid'] != recovery['pid'] and writer['pid'] != independent['pid']
                and recovery['pid'] != independent['pid'],
                f'{name}: recovery and independent reader were not fresh processes')
        require(writer['exit'] == -9 and writer['exit_ns'] < recovery['start_ns'],
                f'{name}: writer was not killed and reaped before recovery')

        if case['stage']:
            require(accept['start_ns'] < writer['exit_ns'] and accept['response'] is None,
                    f'{name}: interrupted caller received an acknowledgement')
            require(gate['pid'] == writer['pid'] and gate['raw_hex'] == '47',
                    f'{name}: gate event did not come from this writer')
            require(accept['start_ns'] < gate['observed_ns'] < writer['exit_ns'],
                    f'{name}: gate did not fall inside the caller request interval')
            require(gate['stage'] == case['stage'], f'{name}: wrong actual holder gate')
        else:
            require(accept['response']['outcome'] == 'commit',
                    'split-ack caller did not receive its acceptance acknowledgement')

        response = recovery_call['response']
        observed = response['consumer_query']
        raw = independent['observation']
        require(independent['exit'] == 0 and raw['integrity'] == 'ok',
                f'{name}: fresh independent SQLite reader failed')
        require(raw['pid'] == independent['pid'] and raw['query'] == observed,
                f'{name}: independent read disagrees with holder query')
        require(raw['view'] == response['state'], f'{name}: SQLite view disagrees with holder read')
        view_bytes = bytes.fromhex(raw['view_utf8_hex'])
        row_bytes = bytes.fromhex(raw['observation_utf8_hex']) if raw['observation_utf8_hex'] else None
        require(digest_hex(view_bytes) == raw['view_sha256'] and json.loads(view_bytes) == raw['view'],
                f'{name}: independently read core-view bytes/hash disagree')
        require(row_bytes is not None and digest_hex(row_bytes) == raw['observation_sha256'],
                f'{name}: independently read observation row missing or corrupt')
        stored = json.loads(row_bytes)
        require(stored['accepted_content'] == case['bootstrap']['calls'][-1]['response']['state']['content']
                or stored['accepted_content'] == accept.get('request', {}).get('value'),
                f'{name}: unexpected row content association')

        statements = case['writer_trace']
        updates = [x for x in statements if x['sql'] == 'UPDATE']
        inserts = [x for x in statements if x['sql'] == 'INSERT']
        commits = [x for x in statements if x['sql'] == 'COMMIT']
        require(len(updates) == 1 and updates[0]['in_transaction'],
                f'{name}: protected content update absent from transaction')
        require(all(x['in_transaction'] for x in inserts),
                f'{name}: observation insert outside transaction')
        require(observed['accepted_content'] == raw['view']['content'],
                f'{name}: observed content does not match recovered kernel content')

        if name == 'atomic-before':
            prior = case['bootstrap']['calls'][-1]['response']
            bootstrap_bundle = observed
            require(case['stage'] == 'prepared' and len(inserts) == 1 and not commits,
                    'pre-COMMIT cut did not occur after evidence write')
            require(raw['view'] == prior['state'] and observed == prior['consumer_query'],
                    'pre-COMMIT process death did not retain the prior acknowledged pair')
            outcomes[name] = 'SUPPORTED: uncommitted content and observation writes rolled back together'
        elif name == 'split-gap':
            require(case['stage'] == 'durable' and len(commits) == 1 and not inserts,
                    'split gap did not stop after content commit and before evidence write')
            require(observed['status'] == 'incompatible_required_observations'
                    and observed['required'] is None
                    and stored['accepted_content'] != raw['view']['content'],
                    'split gap did not leave committed content without matching evidence')
            outcomes[name] = 'COUNTEREXAMPLE: committed content recovered with only prior evidence'
        elif name.startswith('atomic-'):
            require(case['stage'] == 'durable' and len(inserts) == 1 and len(commits) == 1,
                    f'{name}: atomic durable cut has wrong SQL event counts')
            require(inserts[0]['end_ns'] < commits[0]['start_ns'],
                    f'{name}: observation was not inserted before content transaction commit')
            require(observed['status'] == 'available'
                    and observed['required'] == case['declared_original_observations']
                    and stored == {'accepted_content': raw['view']['content'],
                                   'required': case['declared_original_observations']},
                    f'{name}: committed pair did not recover with exact trusted tuple')
            outcomes[name] = 'SUPPORTED: committed content and exact observations recovered together'
        elif name == 'split-ack':
            require(len(commits) == 2 and len(inserts) == 1
                    and commits[0]['end_ns'] < inserts[0]['start_ns'] < commits[1]['start_ns'],
                    'split positive control does not show content commit, evidence commit, then ACK')
            require(observed['status'] == 'available'
                    and observed['required'] == case['declared_original_observations'],
                    'split positive control did not recover accepted evidence')
            require(accept['response']['outcome'] == 'commit'
                    and accept['end_ns'] > commits[1]['end_ns'],
                    'split positive control ACK preceded the evidence commit')
            outcomes[name] = 'SUPPORTED CONTROL: delayed evidence commit completed before ACK'
        else:
            raise AssertionError(f'unexpected case: {name}')
        views[name] = raw['view_utf8_hex']

    a, b = cases['atomic-A'], cases['atomic-B']
    qa = a['independent_reader']['observation']['query']
    qb = b['independent_reader']['observation']['query']
    require(views['atomic-A'] == views['atomic-B'],
            'worlds with different required observations have different core views')
    require(qa['required'] != qb['required'],
            'distinct trusted observation worlds were collapsed')
    require(bootstrap_bundle is not None, 'prior acknowledged bootstrap bundle not captured')

    return {
        'review_class': 'potentially producer-exposed reproduction/adversarial source check; not a clean-room independent reproduction',
        'status': 'COUNTEREXAMPLE',
        'verdict': 'The delayed second SQLite transaction violates this selected C11 acceptance contract: a process can die after accepted content commits and before the matching required observations commit.',
        'cases': outcomes,
        'checks': {
            'same_core_view_distinct_observation_tuples': True,
            'recovery_without_original_tuple_input': True,
            'independent_fresh_sqlite_read_and_integrity': True,
            'actual_inherited_gate_and_caller_ack_state': True,
            'bootstrap_acknowledged_zero_content_pair_retained_before_accept': True,
            'sql_ordering_read_from_trace': True,
        },
        'source_raw_scope_assessment': {
            'observation_row_is_latest_only_and_replaces_prior_bundle': True,
            'bootstrap_bundle_after_successful_new_acceptance_was_not_tested': True,
            'genesis_created_by_project_are_opaque_per_world_fixture_inputs': True,
            'stable_work_unit_identity_or_historical_observation_policy_demonstrated': False,
        },
        'scope': 'Trusted accepted opaque observations and SQLite process termination on one live host; not authenticity, provenance truth, physical power loss, schema/minimality, full C11/F1 closure, or formal cross-family proof.',
    }


if __name__ == '__main__':
    result = audit(sys.argv[1])
    print(json.dumps(result, indent=2, sort_keys=True))
