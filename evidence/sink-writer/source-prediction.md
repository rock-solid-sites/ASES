# Source prediction recorded before the probe

**Baseline execution tree:** `55aee5131141c82c9a6cd2e6418e02890a6291d8`

**Prediction:** In the original unguarded case, both separate sink processes will report ready while the same journal does not yet exist. Each has independent in-memory `next_seq=1`; subsequent actual requests will each be acknowledged as sequence 1 and append duplicate sequence records. Cold recovery will refuse the journal for invalid durable sequence while leaving bytes untouched. The intentionally guarded restart will acquire the lock before constructing `SinkState`, reject a second cooperating process before the first append, refuse fresh-mode restart on an existing journal, then recover the same current journal and continue at sequence 2 after the first owner is killed. The mixed guarded/unguarded case should reproduce the duplicate sequence because the unguarded process does not participate in flock. Distinct journal roots should each accept/recover their own sequence 1.

**Limits expected from source:** flock is advisory and only coordinates participating writers. This does not authenticate a journal/root or confine an untrusted writer. Refusal to recover malformed sequence does not imply accepted contents disappeared; raw bytes should remain observable. This is a bounded same-host process probe, not F4/F1 or cross-family closure.

## Source files and SHA-256 captured before run

- `research/phase-i-t18-sink-order-20261103/run.py` — `3dcb7f66f7e712778e275034e13cf21e845b0348a2c15fcd93bc465fd8823149`
- `research/phase-i-t18-sink-order-20261103/writer-exclusion/guarded_sink.py` — `08cfe9d019631448f9570e418762d48326959bbedf89ac37fc41f380b2ef4133`
- `research/phase-i-t18-sink-order-20261103/writer-exclusion/probe.py` — `d31473bcd0d70553351e18b927d96d4d842a890d6bd3cced7ac25e0c78f48f32`
- `research/phase-i-t18-sink-order-20261103/writer-exclusion/check.py` — `586682823a8b487163ec8d756feb7b90f2e3b35a6d68c0df8af25b39c63615a1`

## Independent premise anchors inspected

Phase-I Closure C6 concerns exclusion of old authority and source binding when physical-producer exclusion is claimed; C7 concerns covered recovery retaining accepted commitments and contents through a current compatible cut; C12 requires successful acknowledgements/publications to follow recoverable commitment. The probe can inform only the local sink-writer/recovery premise, not the full closure.
