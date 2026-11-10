#!/usr/bin/env python3
"""Selected flat C/p local manager/sink; trusted management, no managed replay."""
import hashlib
import http.server
import importlib.util
import json
from pathlib import Path
import select
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('managed_base', HERE.parent / 'run.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.DURABLE_EVENTS += tuple('managed_' + n for n in ('created', 'granted', 'activated', 'revoked', 'replaced'))
base.ORDERED_MODES += ('managed',)


class State(base.SinkState):
    def __init__(self, journal, recover=False):
        super().__init__('managed' if recover else 'sink-ordered', journal)
        self.mode = 'managed'
        self.version = 0
        self.created = self.granted = self.active = False
        self.holder = 'old'
        if recover:
            self.replay()

    def replay(self):
        # Current trusted same-root journal is a premise, not established by parsing.
        with self.journal.open('rb') as stream:
            raw = stream.read(65537)
        if not raw or len(raw) > 65536 or not raw.endswith(b'\n'):
            raise ValueError('empty, oversized or truncated managed journal')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('duplicate managed journal key')
                result[key] = value
            return result
        last = 0
        for line in raw.splitlines():
            event = json.loads(line, object_pairs_hook=unique)
            def require(condition):
                if not condition:
                    raise ValueError('invalid managed transition')
            require(isinstance(event, dict))
            require(type(event.get('seq')) is int and event['seq'] > last)
            require(event.get('profile') == 'flat-managed-v1' and event.get('unit') == 'C' and event.get('position') == 'p')
            name = event.get('event')
            def current(key='current_version'):
                return type(event.get(key)) is int and event[key] == self.version
            def advance():
                return (current('previous_version') and type(event.get('current_version')) is int
                        and event['current_version'] == self.version + 1)
            if name == 'managed_created':
                require(not self.created and current() and event.get('holder') == 'old')
                self.created = True
            elif name == 'managed_granted':
                require(self.created and not self.granted and advance()
                        and event.get('right') == 'write' and event.get('allow') is True)
                self.version += 1
                self.granted, self.active = True, False
            elif name == 'managed_activated':
                require(self.granted and not self.active and current())
                self.active = True
            elif name == 'managed_revoked':
                require(self.created and self.granted and current() and event.get('right') == 'write')
                self.granted = self.active = False
            elif name == 'managed_replaced':
                require(self.created and self.granted and advance() and event.get('previous_holder') == self.holder
                        and isinstance(event.get('holder'), str) and event['holder'] != self.holder)
                self.version += 1
                self.holder, self.active = event['holder'], False
            elif name in ('obligation_committed', 'effect_accepted'):
                payload = event.get('payload')
                require(isinstance(payload, str))
                require(hashlib.sha256(payload.encode()).hexdigest() == event.get('payload_sha256'))
                if name == 'obligation_committed':
                    key = event.get('obligation_id')
                    require(current('committed_under_version') and self.created and self.granted and self.active
                            and isinstance(key, str) and key not in self.obligations)
                    self.obligations[key] = payload
                else:
                    require(current('accepted_under_version') and isinstance(event.get('request_id'), str))
                    if event.get('check_mode') == 'managed-use-current':
                        require(current('presented_version') and self.created and self.granted and self.active)
                    elif event.get('check_mode') == 'committed-exact-obligation':
                        key = event.get('obligation_id')
                        require(isinstance(key, str) and key in self.obligations and self.obligations[key] == payload)
                    else:
                        raise ValueError('unsupported managed effect profile')
                    self.effects.append(event)
            else:
                raise ValueError('unsupported managed journal event')
            self.events.append(event)
            last = event['seq']
        require(self.created)
        self.next_seq = last + 1

    def eligible(self, token):
        return self.created and self.granted and self.active and token == self.version

    def snapshot(self):
        return dict(profile='flat-managed-v1', unit='C', position='p', holder=self.holder,
                    created=self.created, granted=self.granted, active=self.active,
                    authority_version=self.version, persistence_failed=self.persistence_failed,
                    events=list(self.events), effects=list(self.effects), obligations=dict(self.obligations))

    def apply(self, path, data):
        # Called only with the sink's lock held. Trusted local manager boundary.
        common = dict(profile='flat-managed-v1', unit='C', position='p')
        def deny():
            self.emit_locked('managed_rejected', path=path, **common)
            return 409, dict(outcome='rejected', authority_version=self.version)
        def emit(name, **fields):
            return self.emit_locked(name, **common, **fields)
        def token():
            value = data['authority_version']
            if type(value) is not int:
                raise ValueError('integer token required')
            return value
        if path == '/create':
            if self.created:
                return deny()
            event = emit('managed_created', current_version=0, holder='old')
            self.created = True
        elif path == '/grant':
            if not self.created or self.granted:
                return deny()
            event = emit('managed_granted', previous_version=self.version, current_version=self.version + 1,
                         right='write', allow=True)
            self.version += 1
            self.granted, self.active = True, False
        elif path == '/activate':
            if not self.granted or self.active or token() != self.version:
                return deny()
            event = emit('managed_activated', current_version=self.version)
            self.active = True
        elif path == '/revoke':
            if not self.created or not self.granted:
                return deny()
            event = emit('managed_revoked', current_version=self.version, right='write')
            self.granted = self.active = False
        elif path == '/replace':
            if not self.created or not self.granted or data['holder'] == self.holder:
                return deny()
            event = emit('managed_replaced', previous_version=self.version, current_version=self.version + 1,
                         previous_holder=self.holder, holder=data['holder'])
            self.version += 1
            self.holder, self.active = data['holder'], False
        elif path in ('/submit', '/commit-obligation'):
            presented = token()
            if not self.eligible(presented):
                return deny()
            payload = data['payload']
            if not isinstance(payload, str):
                raise ValueError('string payload required')
            payload_hash = hashlib.sha256(payload.encode()).hexdigest()
            if path == '/commit-obligation':
                key = data['obligation_id']
                if not isinstance(key, str) or key in self.obligations:
                    return deny()
                event = emit('obligation_committed', obligation_id=key, payload=payload,
                             payload_sha256=payload_hash, committed_under_version=self.version)
                self.obligations[key] = payload
            else:
                event = emit('effect_accepted', request_id=data['request_id'], payload=payload,
                             payload_sha256=payload_hash, presented_version=presented,
                             accepted_under_version=self.version, check_mode='managed-use-current')
        elif path == '/deliver-obligation':
            key = data['obligation_id']
            if key not in self.obligations:
                return deny()
            payload = self.obligations[key]
            event = emit('effect_accepted', request_id='obligation:' + key, obligation_id=key,
                         payload=payload, payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                         accepted_under_version=self.version, check_mode='committed-exact-obligation')
        else:
            return 404, dict(error='unknown route')
        return (201 if path in ('/submit', '/commit-obligation', '/deliver-obligation') else 200), dict(
            outcome='accepted', event_seq=event['seq'], authority_version=self.version)


def serve(journal, recover=False):
    state = State(journal, recover)
    class Handler(base.make_handler(state)):
        def do_GET(self):
            if self.path != '/status':
                self.send_json(404, dict(error='unknown route'))
                return
            with state.lock:
                data = state.snapshot()
            self.send_json(200, data)

        def do_POST(self):
            try:
                data = self.read_json()
                with state.lock:
                    status, reply = state.apply(self.path, data)
            except (KeyError, TypeError, ValueError) as exc:
                status, reply = 400, dict(error=str(exc))
            except OSError as exc:
                status, reply = 503, dict(error=str(exc))
            self.send_json(status, reply)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    print(json.dumps(dict(ready=True, port=server.server_address[1], profile='flat-managed-v1')), flush=True)
    server.serve_forever(poll_interval=0.05)


class RunningSink(base.RunningSink):
    def __init__(self, source, root, recover=False):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.journal = root / 'sink-effects.jsonl'
        self.process = subprocess.Popen([sys.executable, str(source), '--recover' if recover else '--server', str(self.journal)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        readable, _, _ = select.select([self.process.stdout], [], [], 3)
        line = self.process.stdout.readline() if readable else ''
        if not line:
            self.process.kill()
            self.process.wait(timeout=2)
            raise RuntimeError('managed sink did not become ready')
        self.port = json.loads(line)['port']


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('--server', '--recover'):
        raise SystemExit('usage: managed_sink.py {--server|--recover} JOURNAL')
    serve(Path(sys.argv[2]), sys.argv[1] == '--recover')
