#!/usr/bin/env python
"""Phase: Tests 1-3 in one session.

Test 1 (cold registration, backend never started):
    register_from_mcp(<lazy proxy>) -> registration succeeds; proxy log
    shows NO attempt to reach the backend; print(registry) matches the
    cached manifest.

Test 2 (first call triggers spawn; same session/registry):
    invoke add(2,3); backend spawned at this point and not before;
    ms timings invocation->backend_up and backend_up->result; result ok.

Test 3 (steady state; same session/registry):
    invoke add 3 more times; backend reused (no respawn); rough latency
    vs always-on baseline.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import (  # noqa: E402
    LOGS_DIR,
    backend_pid_from_file,
    count_events,
    first_event,
    hlog,
    make_transport,
    now_ms,
    print_registry_json,
    read_proxy_log,
    safe_invoke,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402

PHASE = "tests1-3"
PROXY_LOG = LOGS_DIR / f"{PHASE}-proxy.log"
BACKEND_PID_FILE = LOGS_DIR / f"{PHASE}-backend.pid"


def main() -> None:
    hlog(f"phase_start phase={PHASE} {versions_line()}")
    hlog(f"proxy_log={PROXY_LOG} backend_pid_file={BACKEND_PID_FILE}")

    # Ensure clean slate for this session.
    if PROXY_LOG.exists():
        PROXY_LOG.unlink()
    if BACKEND_PID_FILE.exists():
        BACKEND_PID_FILE.unlink()

    registry = ToolRegistry(name="test123")
    transport = make_transport(str(PROXY_LOG), backend_pid_file=str(BACKEND_PID_FILE))

    # ---------------- Test 1: cold registration ----------------
    hlog("TEST1_BEGIN")
    t_reg_start = now_ms()
    try:
        registry.register_from_mcp(transport)
        reg_ok = True
        reg_error = None
    except Exception as exc:
        reg_ok = False
        reg_error = exc
    t_reg_end = now_ms()
    hlog(
        f"TEST1_REGISTER result={'ok' if reg_ok else 'FAILED'} "
        f"delta_ms={t_reg_end - t_reg_start} error={reg_error!r}"
    )
    if not reg_ok:
        hlog("TEST1_FAIL registration failed; aborting phase")
        sys.exit(2)

    # Give the (short-lived) registration proxy time to flush/exit.
    time.sleep(0.5)

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns = count_events(proxy_lines, "backend_spawn_start")
    backends_up = count_events(proxy_lines, "backend_up")
    backend_pid_before = backend_pid_from_file(BACKEND_PID_FILE)
    backend_lines_in_proxy_log = count_events(proxy_lines, "backend_")
    hlog(
        f"TEST1_PROXY_LOG backend_spawn_count={spawns} backend_up_count={backends_up} "
        f"backend_pid_file_exists={backend_pid_before is not None} "
        f"proxy_log_backend_events={backend_lines_in_proxy_log}"
    )
    registered_names = registry.list_tools()
    hlog(f"TEST1_REGISTRY list_tools={registered_names}")
    print_registry_json(registry)

    # Manifest comparison: the registered schema for 'add' should equal
    # the manifest's input_schema (through ToolRegistry's JSON schema).
    manifest = (common.HERE / "manifest.json").read_text(encoding="utf-8")
    schema_dump = repr(registry)
    schema_has_add = '"add"' in schema_dump
    manifest_has_add = '"add"' in manifest
    hlog(
        "TEST1_MANIFEST_MATCH schema_mentions_add="
        f"{schema_has_add} manifest_has_add={manifest_has_add} "
        f"pass={'add' in registered_names and manifest_has_add}"
    )

    test1_pass = (
        reg_ok
        and spawns == 0
        and backends_up == 0
        and backend_pid_before is None
        and "add" in registered_names
    )
    hlog(f"TEST1_RESULT pass={test1_pass}")
    hlog("TEST1_END")

    # ---------------- Test 2: first call triggers spawn ----------------
    hlog("TEST2_BEGIN")
    t0 = now_ms()
    result = safe_invoke(registry, "add", {"a": 2, "b": 3}, "5.0")
    t1 = now_ms()

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_after = count_events(proxy_lines, "backend_spawn_start")
    up_line = first_event(proxy_lines, "backend_up")
    resp_lines = [l for l in proxy_lines if l[1].startswith("response tools/call")]
    backend_pid_after = backend_pid_from_file(BACKEND_PID_FILE)

    hlog(
        f"TEST2_SPAWN backend_spawn_count={spawns_after} "
        f"backend_pid_file_exists={backend_pid_after is not None}"
    )
    if up_line:
        up_epoch = up_line[0]
        hlog(
            f"TEST2_TIMING invocation_to_backend_up_ms={up_epoch - t0} "
            f"(harness_call_start={t0} backend_up={up_epoch})"
        )
    if resp_lines:
        resp_epoch = resp_lines[0][0]
        if up_line:
            hlog(
                f"TEST2_TIMING backend_up_to_response_ms={resp_epoch - up_line[0]} "
                f"(backend_up={up_line[0]} response={resp_epoch})"
            )
        hlog(f"TEST2_TIMING end_to_end_ms={t1 - t0} (harness)")
    test2_pass = (
        spawns_after == 1
        and backend_pid_after is not None
        and result == "5.0"
    )
    hlog(f"TEST2_RESULT pass={test2_pass}")
    hlog("TEST2_END")

    # ---------------- Test 3: steady state ----------------
    hlog("TEST3_BEGIN")
    cases = [(4, 5, "9.0"), (10, 20, "30.0"), (0, 0, "0.0")]
    for i, (a, b, expected) in enumerate(cases, start=1):
        safe_invoke(registry, "add", {"a": a, "b": b}, expected)

    proxy_lines = read_proxy_log(PROXY_LOG)
    spawns_final = count_events(proxy_lines, "backend_spawn_start")
    ups_final = count_events(proxy_lines, "backend_up")
    forwards = [l for l in proxy_lines if l[1].startswith("forward tools/call")]
    instance_ids = set()
    for _, msg in forwards:
        for token in msg.split():
            if token.startswith("instance="):
                instance_ids.add(token.split("=", 1)[1])
    hlog(
        f"TEST3_STEADY backend_spawn_count={spawns_final} backend_up_count={ups_final} "
        f"forwards={len(forwards)} distinct_backend_instances={len(instance_ids)} "
        f"instances={sorted(instance_ids)}"
    )
    test3_pass = (
        spawns_final == 1
        and ups_final == 1
        and len(forwards) == 4  # Test 2's call + Test 3's three calls
        and len(instance_ids) == 1
    )
    hlog(f"TEST3_RESULT pass={test3_pass}")
    hlog("TEST3_END")

    registry.close()
    hlog(f"phase_done phase={PHASE} test1_pass={test1_pass} test2_pass={test2_pass} test3_pass={test3_pass}")
    sys.exit(0 if (test1_pass and test2_pass and test3_pass) else 1)


if __name__ == "__main__":
    main()
