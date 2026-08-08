#!/usr/bin/env python
"""Shared measurement library for the catalog-scale residency validation.

Common
------
- Builds stdio transport dicts for the catalog-scale lazy proxy.
- Classifies live processes by /proc cmdline into PROXY and BACKEND buckets
  (always separate — never collapsed into one "connector process" count).
- Samples peak counts during acquisition; measures resident-after after a
  recorded grace period; sums VmRSS per bucket.
- Records the calling mode's daemon-thread profile (AsyncRuntime) and pinned
  versions per run (addendum B).

Run from the pinned venv (/tmp/toolregistry-venv). Stdio transport only.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # .../catalog-scale
VENV_PY = sys.executable

GRACE_SECONDS = 2.5  # settlement wait before resident-after measurement (recorded per run)


def versions() -> dict[str, str]:
    from importlib.metadata import version

    return {
        "python": sys.version.split()[0],
        "toolregistry": version("toolregistry"),
        "mcp": version("mcp"),
    }


def build_transport(conn_id: str, log_dir: Path) -> dict:
    """Stdio transport dict for connector `conn_id` (sync/async compatible)."""
    return {
        "command": VENV_PY,
        "args": [str(HERE / "proxy.py")],
        "env": {
            "PROXY_LOG_FILE": str(log_dir / f"{conn_id}-proxy.log"),
            "BACKEND_PID_FILE": str(log_dir / f"{conn_id}-backend.pid"),
        },
    }


def scan_procs(extra_basename: str | None = None) -> tuple[list[int], list[int]]:
    """Return (proxy_pids, backend_pids) for processes whose argv[1] is a
    catalog-scale script. Extra basenames (e.g. backend_5a.py) supported."""
    proxy_names = {"proxy.py", "proxy_5a.py"}
    backend_names = {"backend.py", "backend_5a.py"}
    if extra_basename:
        backend_names.add(extra_basename)
    proxies: list[int] = []
    backends: list[int] = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                raw = fh.read()
        except OSError:
            continue
        parts = [p.decode(errors="replace") for p in raw.split(b"\0") if p]
        if len(parts) < 2:
            continue
        script = parts[1]
        base = os.path.basename(script)
        if base in proxy_names and script.startswith(str(HERE)):
            proxies.append(int(pid))
        elif base in backend_names and script.startswith(str(HERE)):
            backends.append(int(pid))
    return proxies, backends


def rss_kb(pids: list[int]) -> int:
    """Sum VmRSS (kB) across pids, ignoring processes that vanished."""
    total = 0
    for pid in pids:
        try:
            with open(f"/proc/{pid}/status") as fh:
                for line in fh:
                    if line.startswith("VmRSS"):
                        total += int(line.split()[1])
                        break
        except OSError:
            pass
    return total


def thread_summary() -> dict:
    """Record the harness process's thread profile (addendum B).

    AsyncRuntime runs ONE shared daemon thread named 'async-runtime' for all
    sync entry points (source: toolregistry/_async_runtime.py:65). Async-only
    runs should show zero 'async-runtime' threads in the harness.
    """
    threads = [t.name for t in threading.enumerate()]
    return {
        "thread_count": len(threads),
        "thread_names": sorted(threads),
        "async_runtime_threads": sum(1 for n in threads if n == "async-runtime"),
    }


def snapshot(extra_basename: str | None = None) -> dict:
    """One full residency snapshot: proxy/backend counts + RSS + thread profile."""
    proxies, backends = scan_procs(extra_basename)
    return {
        "proxy_count": len(proxies),
        "proxy_pids": sorted(proxies),
        "proxy_rss_kb": rss_kb(proxies),
        "backend_count": len(backends),
        "backend_pids": sorted(backends),
        "backend_rss_kb": rss_kb(backends),
        "threads": thread_summary(),
    }


class PeakMonitor:
    """Sampled peak tracking during acquisition (50 ms cadence)."""

    def __init__(self, extra_basename: str | None = None) -> None:
        self.extra = extra_basename
        self.peak_proxies = 0
        self.peak_backends = 0
        self.peak_proxy_rss = 0
        self.peak_backend_rss = 0
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        while not self._stop:
            proxies, backends = scan_procs(self.extra)
            self.peak_proxies = max(self.peak_proxies, len(proxies))
            self.peak_backends = max(self.peak_backends, len(backends))
            self.peak_proxy_rss = max(self.peak_proxy_rss, rss_kb(proxies))
            self.peak_backend_rss = max(self.peak_backend_rss, rss_kb(backends))
            time.sleep(0.05)

    def stop(self) -> dict:
        self._stop = True
        self._thread.join(timeout=2)
        return {
            "peak_proxies": self.peak_proxies,
            "peak_backends": self.peak_backends,
            "peak_proxy_rss_kb": self.peak_proxy_rss,
            "peak_backend_rss_kb": self.peak_backend_rss,
        }


def parse_proxy_log(path: Path) -> list[dict]:
    """Parse one PROXY_LOG_FILE into ordered (rel_ms, msg, epoch_ms) records."""
    records: list[dict] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line.startswith("PROXY|"):
                    continue
                parts = line.split("|", 4)
                if len(parts) < 5:
                    continue
                # PROXY | iso | epoch_ms=... | rel_ms=... | msg
                meta = parts[2] + "|" + parts[3]
                rel_ms = int(meta.split("rel_ms=")[1].split("|")[0]) if "rel_ms=" in meta else -1
                epoch_ms = int(meta.split("epoch_ms=")[1].split("|")[0]) if "epoch_ms=" in meta else -1
                records.append({"rel_ms": rel_ms, "epoch_ms": epoch_ms, "msg": parts[4]})
    except OSError:
        pass
    return records


def count_events(log_files: list[Path], prefixes: list[str]) -> dict[str, int]:
    """Count log lines starting with each prefix across connector proxy logs."""
    counts = {p: 0 for p in prefixes}
    for path in log_files:
        for rec in parse_proxy_log(path):
            for prefix in prefixes:
                if rec["msg"].startswith(prefix):
                    counts[prefix] += 1
    return counts


def connector_timings(log_dir: Path, conn_ids: list[str]) -> dict:
    """Per-connector timing decomposition from proxy logs (epoch-derived).

    spawn_ms   = proxy_started - (process start, not observable) -> use
                 acquisition-start timestamps instead where possible.
    connect_ms = request tools/list - proxy_started
    list_ms    = response tools/list - request tools/list
    close_ms   = connection_closed - response tools/list
    """
    out: dict[str, dict] = {}
    for cid in conn_ids:
        recs = parse_proxy_log(log_dir / f"{cid}-proxy.log")
        times: dict[str, int | None] = {
            "proxy_started": None, "request_list": None, "response_list": None,
            "connection_closed": None, "backend_spawn": None,
        }
        for r in recs:
            if r["msg"].startswith("proxy_started") and times["proxy_started"] is None:
                times["proxy_started"] = r["epoch_ms"]
            elif r["msg"].startswith("request tools/list") and times["request_list"] is None:
                times["request_list"] = r["epoch_ms"]
            elif r["msg"].startswith("response tools/list") and times["response_list"] is None:
                times["response_list"] = r["epoch_ms"]
            elif r["msg"].startswith("connection_closed") and times["connection_closed"] is None:
                times["connection_closed"] = r["epoch_ms"]
            elif r["msg"].startswith("backend_spawn_start") and times["backend_spawn"] is None:
                times["backend_spawn"] = r["epoch_ms"]
        if times["proxy_started"] is None:
            continue
        out[cid] = {
            "connect_ms": _delta(times["request_list"], times["proxy_started"]),
            "list_ms": _delta(times["response_list"], times["request_list"]),
            "close_ms": _delta(times["connection_closed"], times["response_list"]),
            "lifetime_ms": _delta(times["connection_closed"], times["proxy_started"]),
            "backend_spawn_epoch": times["backend_spawn"],
        }
    return out


def _delta(a: int | None, b: int | None) -> int | None:
    if a is None or b is None:
        return None
    return max(0, a - b)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, default=str)


def pct_line(msg: str) -> None:
    print(f"HARNESS|{msg}", flush=True)


def clean_orphans(timeout: float = 6.0) -> int:
    """Kill any catalog-scale proxy/backend processes left over from earlier
    phases.

    The mcp 2.0.0 stdio server can hang at exit (observed: stdin EOF but the
    process blocked in ep_poll indefinitely), so a phase that did not close
    its connectors can leave orphans that would otherwise contaminate the
    next phase's baseline. Each test script calls this BEFORE measuring so
    every baseline starts at zero; the number killed is recorded per run.

    Returns the number of processes killed.
    """
    import signal

    killed = 0
    for _ in range(2):
        proxies, backends = scan_procs("backend_5a.py")
        pids = proxies + backends
        if not pids:
            return killed
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
        deadline = time.time() + timeout
        while time.time() < deadline:
            proxies, backends = scan_procs("backend_5a.py")
            if not proxies and not backends:
                break
            time.sleep(0.1)
        else:
            for pid in proxies + backends:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        killed += len(pids)
    return killed
