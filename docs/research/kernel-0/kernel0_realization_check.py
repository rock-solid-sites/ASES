#!/usr/bin/env python3
"""Model-derived checks for the still-live service; run without -O on Unix."""
from __future__ import annotations

import argparse
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from hashlib import sha256
from itertools import permutations, product
import json
import os
from pathlib import Path
import re
import select
import socket
import subprocess
import sys
import threading
import time

from hypothesis import given, settings, strategies as st, find, example
import hypothesis
import kernel0_finite_model as m
import kernel0_service as c

HERE = Path(__file__).resolve().parent
PROFILES = (m.Profile('independent'), m.Profile('coupled', coupled=True),
            m.Profile('exclusive', exclusive=True))
CATALOG = tuple(m.catalog())
METRICS = Counter()
EVIDENCE = {}


def wire(q):
    out = {key: getattr(q, key) for key in ('kind', 'target', 'value', 'other')}
    if q.kind in ('accept', 'resume'):
        out['value'] = c.CONTENTS[q.value]
    if not q.authentic:
        out['authentic'] = True  # Deliberate caller assertion: forbidden schema field.
    return out


def abstract(raw):
    return m.State(raw['established'], tuple(raw['data']),
                   -1 if raw['content'] is None else c.CONTENTS.index(raw['content']),
                   raw['issued'], tuple(raw['rights']), tuple(raw['parents']))


def concrete(s):
    return c.View(s.established, s.data, None if s.content == -1 else c.CONTENTS[s.content],
                  s.issued, s.rights, s.parents)


def packet(obj):
    return json.dumps(obj, separators=(',', ':')).encode() + b'\n'


def receive(conn):
    # Byte-at-a-time intentionally leaves no buffered reply in a killed executor.
    buf = bytearray()
    while not buf.endswith(b'\n'):
        part = conn.recv(1)
        if not part:
            raise EOFError('peer closed before reply')
        buf.extend(part)
    return json.loads(buf)


class Service:
    # Three independent endpoints denote a0; none can upgrade itself to manager.
    CONTEXTS = (-1, 0, 1, 2, 3, 0, 0, -1)

    def __init__(self, profile='independent', gate=None):
        pairs = [socket.socketpair() for _ in self.CONTEXTS]
        self.clients = [p[0] for p in pairs]
        self.children = []
        for conn in self.clients:
            conn.settimeout(10)
        config = {'profile': profile,
                  'channels': [(a, p[1].fileno()) for a, p in zip(self.CONTEXTS, pairs)]}
        inherited = [p[1].fileno() for p in pairs]
        self.event, event_write = os.pipe()
        release_read, self.release = os.pipe()
        if gate:
            config['gate'] = dict(gate, event_fd=event_write, release_fd=release_read)
            inherited += [event_write, release_read]
        self.process = subprocess.Popen([sys.executable, str(HERE / 'kernel0_service.py'), json.dumps(config)],
                                        pass_fds=inherited, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=0)
        for _, server in pairs:
            server.close()
        os.close(event_write)
        os.close(release_read)
        assert select.select([self.process.stdout], [], [], 10)[0], 'service startup timed out'
        assert self.process.stdout.readline() == b'ready\n'

    def call(self, obj, lane=0):
        self.clients[lane].sendall(packet(obj))
        return receive(self.clients[lane])

    def request(self, q, lane=None):
        if lane is None:
            lane = self.CONTEXTS.index(q.evidence)
        return self.call(wire(q), lane)

    def read(self, lane=0):
        return self.call({'kind': 'read'}, lane)['state']

    def setup(self, *grants):
        assert self.request(m.Request('establish'))['outcome'] == 'commit'
        for a, rights in grants:
            assert self.request(m.Request('grant', target=a, value=rights))['outcome'] == 'commit'
        return abstract(self.read())

    def gated(self):
        assert select.select([self.event], [], [], 10)[0], 'gate timed out'
        assert os.read(self.event, 1) == b'G'

    def unblock(self):
        os.write(self.release, b'R')

    def worker(self, lane, obj, mode='send'):
        # A fresh exec, not a forked Python heap. Only its own endpoint is inherited.
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker',
                                 str(self.clients[lane].fileno()), mode, json.dumps(obj)],
                                pass_fds=[self.clients[lane].fileno()], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, bufsize=0)
        self.children.append(proc)
        assert select.select([proc.stdout], [], [], 10)[0]
        assert proc.stdout.readline() == b'private-ready\n'
        return proc

    def close(self):
        worker_errors = []
        for proc in self.children:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
            error = proc.stderr.read().decode()
            if error or proc.returncode > 0:
                worker_errors.append((proc.returncode, error))
            proc.stdout.close()
            proc.stderr.close()
        for conn in self.clients:
            conn.close()
        os.close(self.event)
        os.close(self.release)
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=10)
        errors = self.process.stderr.read().decode()
        self.process.stdout.close()
        self.process.stderr.close()
        assert not errors, errors
        assert not worker_errors, worker_errors

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def worker_main(fd, mode, obj):
    # Candidate bytes and the serialized proposal exist in this process before loss.
    os.dup2(fd, 64)  # Deliberately identical descriptor label in every executor.
    if fd != 64:
        os.close(fd)
    conn = socket.socket(fileno=64)
    conn.settimeout(10)  # Match inherited O_NONBLOCK to Python's timeout wrapper.
    raw = packet(obj)
    print('private-ready', flush=True)
    if mode == 'before':
        threading.Event().wait()
    if mode == 'partial':
        conn.sendall(raw[:len(raw)//2])
        print('partial-sent', flush=True)
        threading.Event().wait()
    if mode == 'resume':
        conn.sendall(packet({'kind': 'read'}))
        retained = receive(conn)['state']['content']
        raw = packet(dict(kind='resume', target=0, value=retained, other=0))
    conn.sendall(raw)
    if mode == 'no-ack':
        threading.Event().wait()
    print(json.dumps(receive(conn)), flush=True)
    if mode == 'ack-stay':
        threading.Event().wait()


def check_one(service, s, q, p):
    expected, outcome = m.resolve(s, q, p)
    response = service.request(q)
    actual = abstract(response['state'])
    assert (actual, response['outcome']) == (expected, outcome), (s, q, response, expected, outcome)
    m.check_edge(s, q, actual, outcome, p)
    METRICS['live_requests'] += 1
    METRICS['live_' + outcome] += 1
    METRICS['kind_' + q.kind + '_' + outcome] += 1
    return actual


def graph_differential():
    parsed = [(q, c.decode(packet(wire(q)))) for q in CATALOG]
    results = []
    for profile in PROFILES:
        queue, seen = deque([m.State()]), {m.State()}
        count = Counter()
        while queue:
            s = queue.popleft()
            view = concrete(s)
            for q, decoded in parsed:
                expected, outcome = m.resolve(s, q, profile)
                candidate = c.candidate(view, q.evidence, decoded, profile.name)
                accepted = candidate is not None and c.valid(candidate, profile.name)
                actual = candidate if accepted else view
                assert (actual, 'commit' if accepted else 'deny') == (concrete(expected), outcome), (s, q)
                count['edges'] += 1
                count[outcome] += 1
                if expected not in seen:
                    seen.add(expected)
                    queue.append(expected)
        result = dict(profile=profile.name, states=len(seen), **count)
        results.append(result)
        print('differential graph:', result, flush=True)
    EVIDENCE['differential_graphs'] = results


def parse_label(label, authentic=True):
    match = re.fullmatch(r'(\w+)\((management|a[0-3]), (\d), (\d), (\d)\)', label)
    assert match, label
    kind, actor, target, value, other = match.groups()
    return m.Request(kind, -1 if actor == 'management' else int(actor[1]),
                     int(target), int(value), int(other), authentic)


def recorded_traces():
    evidence = json.loads((HERE / 'Kernel-0-Finite-Model-results.json').read_text())
    assert evidence['source_sha256'] == sha256((HERE / 'kernel0_finite_model.py').read_bytes()).hexdigest()
    witnesses = evidence['witnesses']
    traces = {'success': witnesses['success'], **{k: v['reference'] for k, v in witnesses['mutants'].items()}}
    traces['new_current_evidence'] = witnesses['new_evidence_at_old_physical_producer']
    for name, trace in traces.items():
        p = PROFILES[2] if name == 'exclusivity' else PROFILES[0]
        with Service(p.name) as service:
            s = m.State()
            if name != 'success':
                s = service.setup((0, 7))
            if name == 'new_current_evidence':
                s = check_one(service, s, m.Request('replace', target=0, other=1), p)
            for step in trace:
                assert asdict(s) == {k: tuple(v) if k in ('data', 'rights', 'parents') else v
                                     for k, v in step['before'].items()}
                q = parse_label(step['event'], name != 'forgery')
                s = check_one(service, s, q, p)
                assert json.loads(json.dumps(asdict(s))) == step['after']
            if name == 'success':
                for step in witnesses['replay_after_two_replacements']:
                    s = check_one(service, s, parse_label(step['event']), p)
    # Replay the model's shortest detached-validation counterexamples against the
    # real service in their recorded resolution orders. Observations stay advisory.
    for fixture in evidence['detached_validation_mutants']:
        name = fixture['name']
        p = PROFILES[2] if name == 'exclusive grant race' else PROFILES[1] if name == 'coupled fields' else PROFILES[0]
        grants = () if name == 'exclusive grant race' else ((0, 7), (3, 2)) if name == 'coupled fields' else ((0, 7),)
        with Service(p.name) as service:
            s, requests = service.setup(*grants), {}
            for event in fixture['counterexample']['trace']:
                if ': invoke/copy ' in event:
                    index, label = event.split(': invoke/copy ')
                    requests[int(index)] = parse_label(label)
                elif ': observe ' in event:
                    service.read()
                elif ': commit -> ' in event or ': deny -> ' in event:
                    s = check_one(service, s, requests[int(event.split(':')[0])], p)
            assert json.loads(json.dumps(asdict(s))) == fixture['counterexample']['expected_state']
    EVIDENCE['recorded_trace_groups'] = len(traces) + len(evidence['detached_validation_mutants'])


def authority_and_bypass():
    p = PROFILES[0]
    with Service() as service:
        s = service.setup((0, 7))
        for order in (0, 1):
            # Both orders tested with successive fresh replacements.
            work = m.Request('flip', order)
            replacement = m.Request('replace', target=order, other=order + 1)
            for q in ((work, replacement) if order == 0 else (replacement, work)):
                s = check_one(service, s, q, p)
        # Old endpoint and replacement endpoint use same apparent request identity.
        payload = wire(m.Request('set', 0, value=1))
        assert service.call(payload, 1)['outcome'] == 'deny'
        assert service.call(payload, 3)['outcome'] == 'commit'
        s = abstract(service.read())
        for field in ('evidence', 'context', 'authentic', 'manager', 'state', 'rights'):
            bad = dict(payload, **{field: -1})
            assert service.call(bad, 1)['outcome'] == 'deny'
            assert abstract(service.read()) == s
        # Worker cannot become manager even with an otherwise valid management frame.
        assert service.call(wire(m.Request('grant', target=3, value=2)), 3)['outcome'] == 'deny'
        snapshot = service.read()
        snapshot['rights'][2] = 0
        snapshot['data'][0] = 0
        snapshot['content'] = 'changed'
        assert abstract(service.read()) == s
        s = check_one(service, s, m.Request('accept', 2, value=1), p)
        candidate = wire(m.Request('accept', 2, value=1))
        candidate['value'] = c.CONTENTS[0]
        assert service.read()['content'] == c.CONTENTS[1]
        s = check_one(service, s, m.Request('mixed', 2), p)
        s = check_one(service, s, m.Request('flip', 2), p)
        s = check_one(service, s, m.Request('flip', 2), p)
        assert abstract(service.read()) == s
    EVIDENCE['authority_and_bypass'] = 'pass: both replacement orders, same payload/different endpoint, forgery, copies, mixed denial, replay'
    with Service() as service:
        service.setup((0, 7))
        assert service.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
        for lane, outcome in ((1, 'deny'), (2, 'commit')):
            proc = service.worker(lane, wire(m.Request('set', 0, value=1)))
            assert select.select([proc.stdout], [], [], 10)[0]
            assert json.loads(proc.stdout.readline())['outcome'] == outcome
            proc.wait(timeout=10)
    EVIDENCE['confusable_descriptor_label'] = 'old and replacement both use local fd 64 and identical JSON; old denied, replacement committed'


def kill(proc):
    proc.kill()
    proc.wait(timeout=10)
    assert proc.returncode < 0


def loss_cuts():
    observations = []
    for stage in ('before', 'partial', 'received', 'validated', 'published'):
        gate = None if stage in ('before', 'partial') else {'lane': 1, 'kind': 'pair', 'stage': stage}
        with Service(gate=gate) as service:
            before = service.setup((0, 7))
            q = m.Request('pair', 0, value=3)
            proc = service.worker(1, wire(q), stage if stage in ('before', 'partial') else 'send')
            if stage == 'partial':
                assert select.select([proc.stdout], [], [], 10)[0]
                assert proc.stdout.readline() == b'partial-sent\n'
            elif gate:
                service.gated()
            kill(proc)
            # Remove the supervisor's duplicate so the service really sees EOF.
            service.clients[1].close()
            if stage in ('received', 'validated', 'published'):
                service.unblock()
                # Synchronize through a read on a separate a0 channel; validated
                # gate owns the lock, received gate may not yet own it.
                for _ in range(100):
                    after = abstract(service.read())
                    if after.data == (1, 1):
                        break
                    time.sleep(.005)
                assert after == m.resolve(before, q, PROFILES[0])[0]
            else:
                after = abstract(service.read())
                assert after == before
            assert after.data in ((0, 0), (1, 1))
            observations.append({'cut': stage, 'after': asdict(after), 'executor_returncode': proc.returncode})
    # A validated old request holds the lock; replacement cannot slip in.
    with Service(gate={'lane': 1, 'kind': 'pair', 'stage': 'validated'}) as service:
        before = service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('pair', 0, value=3)))
        service.gated()
        service.clients[0].sendall(packet(wire(m.Request('replace', target=0, other=1))))
        assert not select.select([service.clients[0]], [], [], .05)[0]
        kill(proc)
        service.clients[1].close()
        service.unblock()
        reply = receive(service.clients[0])
        assert reply['outcome'] == 'commit' and reply['state']['data'] == [1, 1]
        assert reply['state']['rights'] == [0, 7, 0, 0]
    # Real lost acknowledgement followed by an authorized replay on another copy.
    with Service(gate={'lane': 1, 'kind': 'flip', 'stage': 'published'}) as service:
        service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('flip', 0)))
        service.gated()
        assert service.read()['data'] == [1, 0]
        kill(proc)
        service.clients[1].close()
        service.unblock()
        assert service.request(m.Request('flip', 0), lane=5)['state']['data'] == [0, 0]
    # Accepted bytes survive the sole producing process. Replacement consumes them.
    with Service() as service:
        service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('accept', 0, value=1)), 'ack-stay')
        assert select.select([proc.stdout], [], [], 10)[0]
        assert json.loads(proc.stdout.readline())['outcome'] == 'commit'
        kill(proc)
        service.clients[1].close()
        assert service.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
        replacement = service.worker(2, {}, 'resume')
        assert select.select([replacement.stdout], [], [], 10)[0]
        assert json.loads(replacement.stdout.readline())['state']['data'] == [1, 0]
        replacement.wait(timeout=10)
    with Service() as service:
        before = service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('accept', 0, value=1)), 'before')
        kill(proc)
        assert abstract(service.read()) == before
    EVIDENCE['executor_loss'] = observations
    EVIDENCE['content_continuation_and_lost_ack_replay'] = 'pass'


def stale_gate():
    for operation in ('restrict', 'replace'):
        with Service(gate={'lane': 1, 'kind': 'set', 'stage': 'received'}) as service:
            service.setup((0, 7))
            old_view = service.read(1)
            proc = service.worker(1, wire(m.Request('set', 0, value=1)))
            service.gated()
            change = m.Request(operation, target=0, other=1)
            assert service.request(change)['outcome'] == 'commit'
            service.unblock()
            assert select.select([proc.stdout], [], [], 10)[0]
            assert json.loads(proc.stdout.readline())['outcome'] == 'deny'
            proc.wait(timeout=10)
            assert old_view['rights'][0] == 7 and service.read()['rights'][0] == 0
            # This new invocation starts strictly after the change's acknowledgement.
            assert service.request(m.Request('set', 0, value=1))['outcome'] == 'deny'
    EVIDENCE['stale_read_and_completed_change'] = 'pass: ingress held across acknowledged revocation/replacement'


def concurrent(service, requests):
    barrier = threading.Barrier(len(requests))
    def issue(item):
        lane, obj = item
        barrier.wait(timeout=10)
        start = time.monotonic_ns()
        response = service.call(obj, lane)
        end = time.monotonic_ns()
        return start, end, response
    with ThreadPoolExecutor(max_workers=len(requests)) as pool:
        events = list(pool.map(issue, requests))
    if any(a[0] < b[1] and b[0] < a[1] for i, a in enumerate(events) for b in events[i+1:]):
        METRICS['observed_overlapping_histories'] += 1
    return events


def whole_history(initial, qs, events, profile, final):
    edges = {(i, j) for i in range(len(qs)) for j in range(len(qs)) if events[i][1] < events[j][0]}
    for order in permutations(range(len(qs))):
        ranks = {i: n for n, i in enumerate(order)}
        if any(ranks[i] >= ranks[j] for i, j in edges):
            continue
        state = initial
        for i in order:
            state, outcome = m.resolve(state, qs[i], profile)
            if (state, outcome) != (abstract(events[i][2]['state']), events[i][2]['outcome']):
                break
        else:
            if state == final:
                return order
    return None


def concurrency_attacks():
    results = []
    for p in PROFILES:
        with Service(p.name) as service:
            if p.exclusive:
                initial = service.setup()
                qs = [m.Request('grant', target=0, value=1), m.Request('grant', target=3, value=2)]
                lanes = (0, 7)
            else:
                initial = service.setup((0, 7), (3, 2))
                qs = [m.Request('set', 0, 0, 1), m.Request('set', 3, 1, 1)]
                lanes = (1, 4)
                assert service.read(1)['data'] == service.read(4)['data'] == [0, 0]
            events = concurrent(service, [(lane, wire(q)) for lane, q in zip(lanes, qs)])
            outcomes = [event[2]['outcome'] for event in events]
            witness = whole_history(initial, qs, events, p, abstract(service.read()))
            assert witness is not None
            assert outcomes.count('commit') == (1 if p.coupled or p.exclusive else 2)
            results.append({'profile': p.name, 'outcomes': outcomes, 'witness': witness, 'concurrent': True})
    with Service() as service:
        initial = service.setup((0, 7))
        qs = [m.Request('delegate', 0, 3, 2), m.Request('restrict', target=0, value=1)]
        events = concurrent(service, [(1, wire(qs[0])), (0, wire(qs[1]))])
        final = abstract(service.read())
        witness = whole_history(initial, qs, events, PROFILES[0], final)
        assert witness is not None and final.rights == (1, 0, 0, 0)
        results.append({'profile': 'delegation/restriction', 'witness': witness, 'concurrent': True})
    # Same live commit boundary, separate three-bit model extension; all attempts
    # observed 000, but each current guard is re-evaluated under the real lock.
    for order in permutations(range(3)):
        with Service('cycle') as service:
            service.setup((0, 7))
            for lane in (1, 5, 6):
                assert service.read(lane)['cycle'] == [0, 0, 0]
            qs = [{'kind': 'cycle', 'target': i, 'value': 0, 'other': 0} for i in order]
            events = concurrent(service, list(zip((1, 5, 6), qs)))
            accepted = tuple(order[i] for i, event in enumerate(events) if event[2]['outcome'] == 'commit')
            ops = [(lambda s, r=(i + 1) % 3: s[r] == 0,
                    lambda s, w=i: tuple(1 if j == w else bit for j, bit in enumerate(s))) for i in range(3)]
            final = tuple(service.read()['cycle'])
            witness = m.serial_witness((0, 0, 0), ops, accepted, frozenset(), final)
            assert len(accepted) < 3 and witness is not None
            results.append({'profile': 'cycle', 'submission_labels': order, 'accepted': accepted,
                            'final': final, 'witness': witness})
    EVIDENCE['concurrent_attacks'] = results


@settings(max_examples=200, deadline=None, derandomize=True, database=None)
@given(st.sampled_from(PROFILES), st.lists(st.integers(0, 4095), min_size=1, max_size=50))
@example(PROFILES[0], [1477, 2670, 705, 1, 1, 1, 1])
def generated_sequences(profile, choices):
    with Service(profile.name) as service:
        state = m.State()
        state = check_one(service, state, m.Request('establish'), profile)
        for choice in choices:
            # Three quarters of choices select model-enabled operations. The rest
            # attack stale or otherwise inadmissible proposals. No assume/filter.
            pool = [q for q in CATALOG if m.resolve(state, q, profile)[1] == 'commit'] if choice % 4 else CATALOG
            if not pool:
                pool = CATALOG  # Exhausted authority permits only denial; no liveness promise.
            q = pool[(choice // 4) % len(pool)]
            if choice % 17 == 0:
                q = replace(q, authentic=False)
            state = check_one(service, state, q, profile)
            copied = service.read()
            copied['data'][0] = 99
            copied['rights'][0] = 7
            assert abstract(service.read()) == state
            if choice % 97 == 0:
                proc = service.worker(6, wire(m.Request('accept', 0, value=1)), 'before')
                kill(proc)
                assert abstract(service.read()) == state
                METRICS['generated_executor_losses'] += 1
        METRICS['generated_sequences'] += 1


@settings(max_examples=100, deadline=None, derandomize=True, database=None)
@given(st.sampled_from(PROFILES), st.tuples(st.integers(0, 99), st.integers(0, 99), st.integers(0, 99)))
def generated_histories(profile, choices):
    with Service(profile.name) as service:
        initial = service.setup((0, 7))
        if not profile.exclusive:
            assert service.request(m.Request('grant', target=3, value=2))['outcome'] == 'commit'
            initial = abstract(service.read())
        qs = []
        for actor, choice in zip((-1, 0, 3), choices):
            pool = [q for q in CATALOG if q.evidence == actor]
            qs.append(pool[choice % len(pool)])
        events = concurrent(service, [(lane, wire(q)) for lane, q in zip((0, 1, 4), qs)])
        assert whole_history(initial, qs, events, profile, abstract(service.read())) is not None, (qs, events)
        METRICS['generated_concurrent_histories'] += 1


def malformed_ingress():
    samples = [b'{}\n', b'[]\n', b'null\n', b'{"kind":"read","kind":"establish"}\n',
               b'\xff\n', b'{"kind":\n', packet(dict(kind='set', target=True, value=1, other=0)),
               packet(dict(kind='set', target=-1, value=1, other=0)),
               packet(dict(kind='accept', target=0, value={'url': 'live'}, other=0)),
               b'[' * 1100 + b']' * 1100 + b'\n']
    with Service() as service:
        state = service.setup((0, 7))
        for raw in samples:
            service.clients[1].sendall(raw)
            assert receive(service.clients[1])['outcome'] == 'deny'
            assert abstract(service.read()) == state
        # Retargeting the client-owned object after send cannot alter copied bytes.
        obj = wire(m.Request('set', 0, value=0))
        service.clients[1].sendall(packet(obj))
        obj['value'] = 1
        assert receive(service.clients[1])['state']['data'][0] == 0
        service.clients[5].sendall(b'x' * (c.MAX_FRAME + 1))
        assert service.clients[5].recv(1) == b''
        assert abstract(service.read()) == state
    EVIDENCE['malformed_ingress_cases'] = len(samples) + 2


@settings(max_examples=150, deadline=None, derandomize=True, database=None)
@given(st.binary(max_size=1000))
def generated_wire(raw):
    # Exercise actual service ingress, not just the decoder in isolation.
    with Service() as service:
        before = service.setup((0, 7))
        # This envelope always has a forbidden field, irrespective of random bytes.
        obj = dict(wire(m.Request('set', 0, value=1)), evidence=list(raw))
        encoded = packet(obj)
        if len(encoded) > c.MAX_FRAME:
            encoded = b'{"evidence":' + json.dumps(list(raw[:200])).encode() + b'}\n'
        service.clients[1].sendall(encoded)
        assert receive(service.clients[1])['outcome'] == 'deny'
        assert abstract(service.read()) == before
        METRICS['generated_bypass_envelopes'] += 1


def mutation_checks():
    # Mutate concrete reducer behavior locally; never expose a weakness switch on
    # the service wire. Hypothesis finds and shrinks differences from model policy.
    witnesses = {}
    base = m.established((0, 7))
    for name in ('reuse', 'confusion', 'partial', 'amplify', 'stale_view'):
        operations = {
            'reuse': [m.Request('restrict', target=0), m.Request('grant', target=0, value=7), m.Request('set', 0, value=1)],
            'confusion': [m.Request('replace', target=0, other=1), m.Request('set', 0, value=1)],
            'partial': [m.Request('mixed', 0)],
            'amplify': [m.Request('restrict', target=0, value=1), m.Request('delegate', 0, 3, 7)],
            'stale_view': [m.Request('restrict', target=0), m.Request('set', 0, value=1)],
        }[name]
        def diverges(indices):
            expected, actual = base, concrete(base)
            for index in indices:
                q = operations[index]
                expected, result = m.resolve(expected, q, PROFILES[0])
                decoded, actor = c.decode(packet(wire(q))), q.evidence
                source = actual
                if name == 'reuse' and q.kind == 'grant':
                    source = replace(source, issued=source.issued & ~(1 << q.target))
                if name == 'confusion' and actor == 0 and not source.rights[0]:
                    actor = next((i for i in range(3) if source.rights[i]), actor)
                if name == 'amplify' and q.kind == 'delegate':
                    source = replace(source, rights=(7,) + source.rights[1:])
                if name == 'stale_view' and q.kind == 'set':
                    source = replace(source, rights=base.rights)
                out = c.candidate(source, actor, decoded, 'independent')
                commit = out is not None and c.valid(out, 'independent')
                if commit:
                    if name == 'stale_view':
                        out = replace(out, rights=actual.rights)
                    if name == 'amplify':
                        out = replace(out, rights=(actual.rights[0],) + out.rights[1:])
                    actual = out
                if name == 'partial' and q.kind == 'mixed':
                    actual = replace(actual, data=(1, actual.data[1]))
                if (actual, 'commit' if commit else 'deny') != (concrete(expected), result):
                    return True
            return False
        minimized = find(st.lists(st.integers(0, len(operations)-1), min_size=1, max_size=8), diverges,
                         settings=settings(max_examples=1000, deadline=None, derandomize=True, database=None))
        witnesses[name] = [asdict(operations[i]) for i in minimized]
    EVIDENCE['deliberate_concrete_mutants'] = witnesses


def run(output, graph=True):
    if not __debug__:
        raise SystemExit('Run without -O; assertions are the test oracle.')
    for test in ([graph_differential] if graph else []) + [recorded_traces, authority_and_bypass,
            stale_gate, loss_cuts, concurrency_attacks, malformed_ingress, generated_sequences,
            generated_histories, generated_wire, mutation_checks]:
        test()
        print('passed:', test.__name__, flush=True)
    required = {'establish', 'grant', 'restrict', 'replace', 'delegate', 'set', 'flip', 'pair', 'accept', 'resume'}
    assert all(METRICS['kind_' + kind + '_commit'] > 0 for kind in required)
    assert METRICS['observed_overlapping_histories'] > 0
    EVIDENCE['metrics'] = dict(METRICS)
    EVIDENCE['source_sha256'] = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in
        ('kernel0_service.py', 'kernel0_realization_check.py', 'kernel0_finite_model.py')}
    EVIDENCE['runtime'] = {'python': sys.version, 'hypothesis': hypothesis.__version__, 'platform': sys.platform}
    EVIDENCE['status'] = 'all requested checks passed' if graph else 'development checks passed; graph omitted'
    if output:
        Path(output).write_text(json.dumps(EVIDENCE, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(METRICS), sort_keys=True), flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        worker_main(int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--output')
        parser.add_argument('--skip-graph', action='store_true', help='development only')
        args = parser.parse_args()
        run(args.output, not args.skip_graph)
