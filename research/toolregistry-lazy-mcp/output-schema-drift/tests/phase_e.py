#!/usr/bin/env python
"""Phase: Test E — determinism + recovery search.

Fresh proxy process, fresh registry (same diverging setup as Test C).

Sequence in ONE session:
1. Call #1: reproduce the Test C failure (cached conforming manifest,
   backend returns non-conforming shape).  Records the failure.
2. Call #2: IMMEDIATELY repeat the identical call in the same session.
   Records whether it fails identically / deterministically, succeeds on
   retry, produces a different error, or hangs.

The source-read half of the recovery investigation (does ANY refresh /
invalidation mechanism exist — in ToolRegistry, in the proxy, or a
Lexicon-CID-based cache-invalidation path) is done in the report; this
phase records the runtime half: whether repeating the call recovers.

Recorded per call: spawn counts, error verbatim, elapsed ms, and whether
the failure is identical across the two calls.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_drift as common  # noqa: E402
from common_drift import (  # noqa: E402
    HERE,
    LOGS_DIR,
    count_events,
    events,
    hlog,
    invoke_recorded,
    make_transport,
    print_manifest_schemas,
    proxy_pids,
    read_proxy_log,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "test-e"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
MANIFEST = HERE / "manifest.json"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"manifest={MANIFEST.name} backend_schema_mode=conforming backend_response_mode=diverging")
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()

    registry = ToolRegistry(name="teste")
    transport = make_transport(
        str(PROXY_LOG),
        manifest=str(MANIFEST),
        backend_schema_mode="conforming",
        backend_response_mode="diverging",
    )

    hlog("TESTE_BEGIN register")
    t0 = common.now_ms()
    reg_error = None
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t1 = common.now_ms()
    hlog(f"TESTE_REGISTER result={'ok' if reg_ok else 'FAILED'} delta_ms={t1 - t0} error={reg_error!r}")
    if not reg_ok:
        sys.exit(2)
    time.sleep(0.5)

    print_manifest_schemas(MANIFEST)

    # ---- Call 1: reproduce Test C failure ----
    hlog("TESTE_CALL1_BEGIN (reproduces Test C)")
    outcome1 = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="call1-add(2,3)")
    msg1 = getattr(outcome1, "message", None) if outcome1 is not None else None

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_after_1 = len(events(proxy_lines, "backend_spawn_start"))
    hlog(
        f"TESTE_CALL1_SPAWN_COUNT backend_spawn_count={spawns_after_1} "
        f"proxy_processes={len(proxy_pids(proxy_lines))}"
    )

    # ---- Call 2: immediate repeat, same session ----
    hlog("TESTE_CALL2_BEGIN (immediate repeat)")
    outcome2 = invoke_recorded(registry, "add", {"a": 2, "b": 3}, label="call2-add(2,3)")
    msg2 = getattr(outcome2, "message", None) if outcome2 is not None else None

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_after_2 = len(events(proxy_lines, "backend_spawn_start"))
    pids_after_2 = proxy_pids(proxy_lines)
    hlog(
        f"TESTE_CALL2_SPAWN_COUNT backend_spawn_count={spawns_after_2} "
        f"proxy_processes={len(pids_after_2)} proxy_pids={pids_after_2}"
    )

    # ---- Determinism analysis ----
    both_failed = (
        outcome1 is not None and not hasattr(outcome1, "result")
        and outcome2 is not None and not hasattr(outcome2, "result")
    )
    identical = both_failed and msg1 == msg2
    hlog(
        f"TESTE_DETERMINISM call1_failed={outcome1 is not None and not hasattr(outcome1, 'result')} "
        f"call2_failed={outcome2 is not None and not hasattr(outcome2, 'result')} "
        f"identical_message={identical}"
    )
    if msg1 is not None:
        hlog(f"TESTE_CALL1_MESSAGE_VERBATIM={msg1!r}")
    if msg2 is not None:
        hlog(f"TESTE_CALL2_MESSAGE_VERBATIM={msg2!r}")

    pass_e = both_failed and identical and spawns_after_2 >= spawns_after_1 + 1
    hlog(f"TESTE_RESULT pass={pass_e} (deterministic failure, no self-recovery)")
    registry.close()
    hlog(f"phase_done phase={PHASE} test_e_pass={pass_e}")
    sys.exit(0 if pass_e else 1)


if __name__ == "__main__":
    main()
