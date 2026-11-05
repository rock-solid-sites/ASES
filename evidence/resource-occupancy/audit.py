#!/usr/bin/env python3
"""Independent read-only spot audit of raw native lifetime and transaction ordering."""
import errno
import json
import sys
from pathlib import Path

raw = json.loads(Path(sys.argv[1]).read_text())
findings = {}
for kind, c in raw['cases'].items():
    original = c['initial']['native']['identity']
    released = c['release_ack']
    assert released['native_identity'] == original
    assert released['sql_trace'][-1]['sql'] == 'COMMIT'
    assert released['sql_trace'][-1]['end_ns'] < released['ns'] < released['parent_received_ns']
    assert c['ledger_before_release']['claims'] == ['A']
    assert c['ledger_after_release']['claims'] == []

    if kind == 'retained':
        assert c['handoff']['native_identity'] == original == c['keeper_ready']['native_identity']
        assert c['A_exit']['exit'] == -9 < 0
        assert c['A_exit']['exit_ns'] < c['busy']['process']['start_ns']
        denial = c['busy']['first']
        assert denial['native']['errno'] == errno.EADDRINUSE and not denial['native']['bound']
        assert c['keeper_exit']['exit'] == 0
        assert c['keeper_exit']['exit_ns'] < c['acquisition']['first']['native']['start_ns']
        assert c['close_ack']['prior_identity'] == original
    elif kind == 'terminated':
        assert c['A_exit']['exit'] == -9
        assert c['A_exit']['exit_ns'] < c['acquisition']['first']['native']['start_ns']
    elif kind == 'live':
        weak = c['unbacked']
        assert weak['first']['stage'] == 'claim_ack'
        assert weak['second']['native']['errno'] == errno.EADDRINUSE
        assert weak['ledger']['claims'] == ['B']
        assert c['explicit_unbacked_cleanup']['ledger']['claims'] == []
        assert c['close_ack']['parent_received_ns'] < c['acquisition']['first']['native']['start_ns']

    ack = c['acquisition']['first']
    native = ack['native']
    assert native['bound'] and native['identity']['address'] == ['127.0.0.1', c['port']]
    assert native['identity']['accepting'] == 1
    begin, insert, commit = ack['sql_trace']
    assert [x['sql'] for x in (begin, insert, commit)] == ['BEGIN', 'INSERT', 'COMMIT']
    assert native['end_ns'] < commit['start_ns'] < commit['end_ns'] < ack['ns'] < ack['parent_received_ns']
    assert c['occupied_probe']['errno'] == errno.EADDRINUSE
    assert c['after_B_termination']['ledger']['claims'] == ['B']
    assert c['after_B_termination']['native_probe']['bound']
    findings[kind] = 'release ACK followed COMMIT; guarded bind/listen preceded COMMIT/ACK; B row remained after B death and ephemeral socket release'

print(json.dumps({'status': 'SUPPORTED', 'cases': findings,
                  'scope': 'observed Linux loopback TCP and SQLite ordering/lifetime only'}, indent=2, sort_keys=True))
