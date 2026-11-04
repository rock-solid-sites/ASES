#!/usr/bin/env python3
"""Observe the preregistered F4 gates; leave the pinned sink unchanged."""
import hashlib
import json
import platform
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
import run as sinkmod

HERE = Path(__file__).resolve().parent
PAYLOAD = 'round2-effect-π\nimmutable payload'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def snapshot(path):
    try:
        raw = path.read_bytes()
        return {'exists': True, 'raw_hex': raw.hex(), 'sha256': digest(raw)}
    except FileNotFoundError:
        return {'exists': False, 'raw_hex': None, 'sha256': None}

def strict_read(path):
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return {'state': 'MISSING'}, 3
    if not raw:
        return {'state': 'EMPTY', 'effects': [], 'sha256': digest(raw)}, 0
    try:
        if not raw.endswith(b'\n'):
            raise ValueError('truncated final record')
        effects = []
        for i, line in enumerate(raw.splitlines(), 1):
            event = json.loads(line)
            if event['seq'] != i or event['event'] != 'effect_accepted':
                raise ValueError('unexpected sequence or record type in one-effect profile')
            payload = bytes.fromhex(event['payload_utf8_hex'])
            if payload.decode() != event['payload'] or digest(payload) != event['payload_sha256']:
                raise ValueError('payload mismatch')
            effects.append({'request_id': event['request_id'], 'payload_hex': payload.hex(),
                            'payload_sha256': digest(payload), 'seq': event['seq']})
        return {'state': 'VALID', 'effects': effects, 'sha256': digest(raw)}, 0
    except (ValueError, KeyError, TypeError) as exc:
        return {'state': 'REFUSED', 'error': str(exc), 'sha256': digest(raw)}, 2

def reader(path):
    p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--read', str(path)],
                       capture_output=True, text=True, timeout=4)
    return {'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
            'observation': json.loads(p.stdout)}

def run_case(root, name, cut, gate):
    sink = sinkmod.RunningSink('f4', root)
    client = None
    record = {'sink_pid': sink.process.pid, 'cut': cut, 'request_id': name}
    try:
        record['client_start_ns'] = time.monotonic_ns()
        client = subprocess.Popen([sys.executable, str(HERE/'run.py'), '--client', str(sink.port),
                                   name, PAYLOAD, cut], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        record['client_pid'] = client.pid
        if gate:
            record['status'] = sinkmod.wait_for_event(sink, gate)
            record['gate_observed_ns'] = time.monotonic_ns()
        if cut in ('normal', 'early_ack'):
            record['client'], record['client_stderr'] = sinkmod.read_child_json(client, name)
            record['client_completed_ns'] = time.monotonic_ns()
        if not gate:
            record['status'] = sinkmod.latest_status(sink)
            record['status_observed_ns'] = time.monotonic_ns()
        record['journal_live'] = snapshot(sink.journal)
        record['live_reader'] = reader(sink.journal)
        record['kill_start_ns'] = time.monotonic_ns()
        record['sink_exit'] = sink.kill_and_reap()
        record['reaped_ns'] = time.monotonic_ns()
        if cut not in ('normal', 'early_ack'):
            record['client'], record['client_stderr'] = sinkmod.read_child_json(client, name)
            record['client_completed_ns'] = time.monotonic_ns()
        record['client_exit'] = client.returncode
        record['journal_after'] = snapshot(sink.journal)
        record['cold_reader'] = reader(sink.journal)
        return record
    finally:
        if client and client.poll() is None:
            client.kill()
            client.communicate(timeout=2)
        sink.kill_and_reap()

def main():
    # Inherited by owned sinks, clients and readers. No system-wide limits.
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    if len(sys.argv) == 3 and sys.argv[1] == '--read':
        result, code = strict_read(Path(sys.argv[2]))
        print(json.dumps(result, sort_keys=True))
        return code
    with tempfile.TemporaryDirectory(prefix='ases-round2-f4-') as td:
        root = Path(td)
        cases = {}
        for name, cut, gate in [('normal','normal',None), ('preaccept','preaccept','request_waiting_before_accept'),
                                ('accepted','after_accept_before_ack','accepted_waiting_before_ack'),
                                ('early_ack','early_ack','early_ack_waiting_before_accept')]:
            cases[name] = run_case(root/name, name, cut, gate)
        empty = root/'empty'; empty.touch()
        malformed = root/'malformed'; malformed.write_bytes(b'{bad}\n')
        truncated = root/'truncated'; truncated.write_bytes(bytes.fromhex(cases['normal']['journal_after']['raw_hex'])[:-5])
        controls = {k: reader(p) for k,p in [('empty',empty), ('missing',root/'missing'),
                                            ('malformed',malformed), ('truncated',truncated)]}
    result = {'schema':'ases.f4-gates.v1', 'source_revision': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'environment':{'platform':platform.platform(), 'python':sys.version, 'executable':sys.executable,
                             'executable_sha256':digest(Path(sys.executable).read_bytes()), 'address_space_bytes':256*1024*1024},
              'hashes':{p.name:digest(p.read_bytes()) for p in [HERE/'run.py',Path(__file__)]},
              'payload_hex':PAYLOAD.encode().hex(), 'cases':cases,'controls':controls}
    print(json.dumps(result, indent=2,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
