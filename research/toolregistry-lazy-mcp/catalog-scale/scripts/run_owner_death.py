#!/usr/bin/env python
"""Owner-death lifecycle observation: do stdio connectors orphan on owner death?

Lifecycle finding (report.md Section 9 item 3, catalog-scale #295): when the
ToolRegistry process exits WITHOUT explicitly closing persistent MCP
connections, the proxy and backend subprocesses persist indefinitely —
observed still alive 15+ minutes after parent death, blocked in ep_poll with
stdin at EOF. The mcp 2.0.0 stdio server does not terminate on bare EOF in
this state. Reclamation REQUIRES explicit teardown; process death alone is
not sufficient.

This script produces the committed, re-derivable evidence for that finding:

  1. Clean any pre-existing catalog-scale orphans (baseline zero).
  2. FORK an owner subprocess (fresh process, no shared registry state):
     it registers N connectors, invokes each once (creating persistent
     proxy+backend pairs), records the spawned PIDs, then SIGKILLs ITSELF —
     no close_sync(), no atexit cleanup — simulating owner death without
     explicit teardown.
  3. The parent observes the surviving (orphaned) PIDs at intervals:
       - immediately after owner death (t=0)
       - after the observation interval (OBSERVE_SECONDS) — still alive?
     For each survivor, records the /proc wchan (expected ep_poll) to show
     the process is blocked, not exiting.
  4. Sends SIGTERM to survivors, waits the reclamation grace, then SIGKILLs
     any that remain (matching common.clean_orphans() TERM/KILL fallback).
  5. Records the final zero snapshot (no catalog-scale processes remain).

Output: logs/owner-death/owner-death-lifecycle.json — parent exit timestamp,
surviving PIDs per observation, observation interval, kill signals used, and
the final zero snapshot. Stdio only; runs from the pinned venv.

Usage: /tmp/toolregistry-venv/bin/python scripts/run_owner_death.py
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # .../catalog-scale
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    GRACE_SECONDS,
    build_transport,
    clean_orphans,
    pct_line,
    persistence,
    scan_procs,
    versions,
    write_json,
)

from toolregistry import ToolRegistry  # noqa: E402
from toolregistry._async_runtime import AsyncRuntime  # noqa: E402

RUN_LABEL = "owner-death"
N = 3  # connectors; enough to be unambiguous, cheap to observe
OBSERVE_SECONDS = 5.0  # interval over which survivors must remain alive
RECLAIM_GRACE = 6.0  # TERM->KILL escalation window (matches clean_orphans)


def _conn_for(reg: ToolRegistry, cid: str):
    idx = int(cid.lstrip("c"))
    return reg._mcp_integrations[idx]._connections[0]


def _wchan(pid: int) -> str:
    try:
        return Path(f"/proc/{pid}/wchan").read_text().strip()
    except OSError:
        return "gone"


def _owner_child(log_dir: Path, pipe_fd: int) -> None:
    """Register+invoke connectors, report spawned PIDs, then SIGKILL self.

    Runs in a forked subprocess so the parent can observe the aftermath.
    Deliberately does NOT close_sync() any manager before dying.
    """
    try:
        reg = ToolRegistry()
        conn_ids = [f"c{i}" for i in range(N)]
        transports = {cid: build_transport(cid, log_dir) for cid in conn_ids}
        for cid in conn_ids:
            reg.register_from_mcp(transports[cid], namespace=cid)
        for cid in conn_ids:
            AsyncRuntime.run_sync(_conn_for(reg, cid).list_tools())
        for cid in conn_ids:
            r = reg.invoke(f"{cid}-add", {"a": 1, "b": 2})
            pct_line(f"OWNER invoke {cid}-add result={getattr(r, 'result', r)}")

        # Collect the spawned persistent proxy/backend PIDs via /proc scan
        # scoped to THIS corpus (catalog-scale scripts only).
        proxies, backends = scan_procs()
        payload = json.dumps({
            "owner_pid": os.getpid(),
            "proxies": proxies,
            "backends": backends,
        }).encode()
        os.write(pipe_fd, payload)
        os.close(pipe_fd)

        # Simulate owner death WITHOUT explicit close: SIGKILL self now.
        pct_line(f"OWNER {os.getpid()} SIGKILL self without close_sync")
        os.kill(os.getpid(), signal.SIGKILL)
    except BaseException as exc:  # pragma: no cover - child only
        pct_line(f"OWNER child error {type(exc).__name__}:{exc}")
        os._exit(3)


def main() -> None:
    base = HERE / "logs" / RUN_LABEL
    base.mkdir(parents=True, exist_ok=True)
    log_dir = base / "run"
    log_dir.mkdir(parents=True, exist_ok=True)
    for stale in list(log_dir.glob("*.log")) + list(log_dir.glob("*.pid")):
        stale.unlink()

    pct_line(f"OWNER-DEATH begin versions={versions()} pre_cleaned={clean_orphans()}")

    pipe_r, pipe_w = os.pipe()
    child = os.fork()
    if child == 0:
        try:
            os.close(pipe_r)
            _owner_child(log_dir, pipe_w)
        except BaseException:  # pragma: no cover - child only
            os._exit(3)
        os._exit(0)

    os.close(pipe_w)
    spawned: dict = {}
    try:
        raw = os.read(pipe_r, 65536)
        spawned = json.loads(raw.decode())
    except Exception as exc:
        pct_line(f"OWNER-DEATH read child payload error {type(exc).__name__}:{exc}")
    os.close(pipe_r)

    # Parent exit = child's death (SIGKILL). Record surviving PIDs.
    parent_exit_epoch_ms = int(time.time() * 1000)
    pct_line(f"OWNER-DEATH parent_exit owner_pid={spawned.get('owner_pid')} child_rc=None")

    spawned_proxies = sorted(spawned.get("proxies", []))
    spawned_backends = sorted(spawned.get("backends", []))

    observations: list[dict] = []

    def observe(tag: str) -> dict:
        proxies, backends = scan_procs()
        obs = {
            "tag": tag,
            "t_sec": round(time.time() - (parent_exit_epoch_ms / 1000), 2),
            "proxies_alive": sorted(set(proxies) & set(spawned_proxies)),
            "backends_alive": sorted(set(backends) & set(spawned_backends)),
            "wchan": {str(p): _wchan(p) for p in sorted(set(proxies) & set(spawned_proxies))},
        }
        observations.append(obs)
        pct_line(
            f"OWNER-DEATH observe {tag} proxies_alive={obs['proxies_alive']} "
            f"backends_alive={obs['backends_alive']} wchan={obs['wchan']}"
        )
        return obs

    observe("t0_immediate")
    time.sleep(OBSERVE_SECONDS)
    obs_survive = observe("after_observation_interval")

    # Reclamation: TERM survivors, grace, KILL remainder.
    survivors = sorted(set(obs_survive["proxies_alive"] + obs_survive["backends_alive"]))
    term_signals: list[str] = []
    kill_signals: list[str] = []
    if survivors:
        for pid in survivors:
            try:
                os.kill(pid, signal.SIGTERM)
                term_signals.append(str(pid))
            except OSError:
                pass
        deadline = time.time() + RECLAIM_GRACE
        while time.time() < deadline:
            proxies, backends = scan_procs()
            if not (set(proxies) & set(survivors)) and not (set(backends) & set(survivors)):
                break
            time.sleep(0.2)
        proxies_rem, backends_rem = scan_procs()
        remaining = sorted(set(proxies_rem + backends_rem) & set(survivors))
        for pid in remaining:
            try:
                os.kill(pid, signal.SIGKILL)
                kill_signals.append(str(pid))
            except OSError:
                pass
        time.sleep(GRACE_SECONDS)

    proxies_final, backends_final = scan_procs()
    final_zero = {
        "proxy_count": len(proxies_final),
        "proxy_pids": sorted(proxies_final),
        "backend_count": len(backends_final),
        "backend_pids": sorted(backends_final),
    }

    result = {
        "test": "owner-death-lifecycle",
        "purpose": "mcp 2.0.0 stdio connectors orphan on owner death without explicit close (lifecycle finding, report.md Section 9 item 3)",
        "n": N,
        "owner_pid": spawned.get("owner_pid"),
        "spawned_proxies": spawned_proxies,
        "spawned_backends": spawned_backends,
        "parent_exit_epoch_ms": parent_exit_epoch_ms,
        "observation_interval_sec": OBSERVE_SECONDS,
        "observations": observations,
        "survivors_after_interval": survivors,
        "reclaim_signal_termed": term_signals,
        "reclaim_signal_killed": kill_signals,
        "reclaim_grace_sec": RECLAIM_GRACE,
        "final_zero_snapshot": final_zero,
        "versions": versions(),
        "persistence": persistence(),
        "grace_seconds": GRACE_SECONDS,
    }
    write_json(base / "owner-death-lifecycle.json", result)
    pct_line(
        f"OWNER-DEATH done survivors={len(survivors)} final_proxies={final_zero['proxy_count']} "
        f"final_backends={final_zero['backend_count']}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
