# Baseline executed negative-input boundary

Source6b332ae. Both missing required field and integer evidence reached actual content/
archive/latest COMMIT before consumer validation; caller got no response. A fresh holder
advertised ready, then returned no usable read response. Independent diagnostic SQL
reader (not a consumer validity oracle) sees new content plus actual malformed required
JSON, integrity ok. Well-typed positive ACKs/recovery pass. Same-content conflicting
well-typed bundle triggers actual ROLLBACK/no ACK and retains earlier accepted records.
Original malformed database image invalid-missing.sqlite retained with exact digest;
baseline recovery advertises ready but query fails, unchanged database digest.

First read-only checker required a specific stderr exception. Parent kills/reaps soon
after socket EOF, so traceback delivery can race process termination; raw stderr was
not guaranteed. Initial checker failure retained; do not infer no exception from absent
stderr, nor claim an observed exception class where metadata is missing. Checker now
reports optional exception metadata separately. Actual SQL COMMIT, malformed persisted
fields, no usable response and fresh readiness/query observations establish the narrower
failure. Re-audited same raw, no behavioral rerun. This is an observation-instrument
qualification, not a product repair or manufactured stderr result.

Completed well-typed archive evidence remains under its explicit input premise. This
new selected invalid-input boundary shows validation is too late; it is not source
truth/authentication proof or a defect in the unchanged parent holder. Next authorized
repair: type/presence check supplied observations before exposing endpoint, existing
current/archive shape/content-key checks before ready; refuse retained malformed image
unchanged. Keep valid/conflicting controls and exact baseline history.
