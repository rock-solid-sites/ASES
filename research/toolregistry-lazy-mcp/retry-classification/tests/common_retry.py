#!/usr/bin/env python
"""Shared helpers for the retry-classification phases (#217).

Evidence instruments, not a product -- same conventions as the #213
``common_drift.py``, with the additions this investigation needs:

* ``make_transport`` takes an explicit ``proxy_path`` so Test 1 runs the
  ORIGINAL unmodified #213 drift proxy (control) and Tests 2/3 run
  ``proxy_classified.py`` (the single-variable delta).  The classified
  proxy's caller-visible outcome is a ``ToolCallResult`` whose ``result``
  is the stringified ``CallToolResult`` repr (ToolRegistry 0.15.0
  ``_finalize_result`` stringifies isError responses), so
  ``invoke_recorded`` detects a classified failure by the embedded
  ``is_error=True`` + schema-error signature and captures it verbatim --
  it does NOT mistake it for a success.
* ``wait_for_persistent_proxy_pid`` + ``kill_proxy_mid_call`` support
  Test 3 (kill the persistent proxy while the first call is in flight).
"""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path
from typing import Any

# research/toolregistry-lazy-mcp/retry-classification/
HERE = Path(__file__).resolve().parent.parent
CLASSIFIED_PROXY = HERE / "proxy_classified.py"
BACKEND_PATH = HERE / "backend.py"
LOGS_DIR = HERE / "logs"

# The #213 corpus proxy (UNMODIFIED) -- the Test 1 control.
DRIFT_PROXY = HERE.parent / "output-schema-drift" / "proxy.py"

PROXY_LOG_RE = __import__("re").compile(
    r"^PROXY\|(?P<iso>\S+)\|epoch_ms=(?P<epoch>\d+)\|rel_ms=\s*(?P<rel>\d+)\|(?P<msg>.*)$"
)

# Signature of a classified schema-validation failure inside the
# stringified CallToolResult repr returned by ToolRegistry 0.15.0.
CLASSIFIED_ERROR_MARKERS = ("is_error=True", "Invalid structured content returned by tool")


def now_ms() -> int:
    return int(time.time() * 1000)


def iso_ms() -> str:
    now = time.time()
    epoch_ms = int(now * 1000)
    return (
        time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now))
        + f".{epoch_ms % 1000:03d}Z"
    )


def hlog(msg: str) -> None:
    print(f"HARNESS|{iso_ms()}|epoch_ms={now_ms()}|{msg}", flush=True)


def versions_line() -> str:
    import importlib.metadata as md

    try:
        tr = md.version("toolregistry")
    except md.PackageNotFoundError:
        tr = "not-installed"
    try:
        mcp = md.version("mcp")
    except md.PackageNotFoundError:
        mcp = "not-installed"
    return (
        f"versions toolregistry={tr} mcp={mcp} "
        f"python={sys.version.split()[0]} platform={sys.platform}"
    )


def make_transport(
    proxy_log_path: str,
    *,
    proxy_path: str | Path = CLASSIFIED_PROXY,
    manifest: str | None = None,
    backend_schema_mode: str | None = None,
    backend_response_mode: str | None = None,
    backend_pid_file: str | None = None,
    proxy_pid_file: str | None = None,
    proxy_backend_timeout: str = "45.0",
    proxy_call_timeout: str = "120.0",
) -> dict[str, Any]:
    """Build the stdio transport dict for ``register_from_mcp``.

    The mcp SDK's ``stdio_client`` only inherits a safe env subset
    (HOME/LOGNAME/PATH/SHELL/TERM/USER) plus whatever ``env`` we pass,
    so probe control variables must be passed explicitly here.

    ``proxy_backend_timeout`` / ``proxy_call_timeout`` are the proxy's
    documented ``PROXY_BACKEND_TIMEOUT`` / ``PROXY_CALL_TIMEOUT`` knobs,
    raised from the proxy defaults (10.0/15.0 s) because this host runs
    several parallel agents: measured backend initialize handshakes reach
    12.2 s (vs 773-1555 ms in #213's normal-load runs), which exceeds the
    defaults and would abort the call with ``backend did not become ready``
    instead of exercising the tested failure class.  The same values are
    used for ALL phases (control and modified) so the comparison stays
    like-for-like; this is test-environment tuning, not proxy behaviour.
    """
    env: dict[str, str] = {
        "PROXY_LOG_FILE": proxy_log_path,
        "PROXY_BACKEND_TIMEOUT": proxy_backend_timeout,
        "PROXY_CALL_TIMEOUT": proxy_call_timeout,
    }
    if proxy_pid_file:
        env["PROXY_PID_FILE"] = proxy_pid_file
    if manifest:
        env["PROXY_MANIFEST"] = str(manifest)
    if backend_schema_mode:
        env["BACKEND_SCHEMA_MODE"] = backend_schema_mode
    if backend_response_mode:
        env["BACKEND_RESPONSE_MODE"] = backend_response_mode
    if backend_pid_file:
        env["BACKEND_PID_FILE"] = backend_pid_file
    return {
        "command": sys.executable,
        "args": [str(proxy_path)],
        "env": env,
    }


def read_proxy_log(path: str | Path) -> list[tuple[int, str]]:
    """Return [(epoch_ms, message), ...] parsed from a proxy log file."""
    out: list[tuple[int, str]] = []
    p = Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        m = PROXY_LOG_RE.match(line)
        if m:
            out.append((int(m.group("epoch")), m.group("msg")))
    return out


def count_events(lines: list[tuple[int, str]], prefix: str) -> int:
    return sum(1 for _, msg in lines if msg.startswith(prefix))


def first_event(lines: list[tuple[int, str]], prefix: str) -> tuple[int, str] | None:
    for epoch, msg in lines:
        if msg.startswith(prefix):
            return epoch, msg
    return None


def events(lines: list[tuple[int, str]], prefix: str) -> list[tuple[int, str]]:
    return [(e, m) for e, m in lines if m.startswith(prefix)]


def proxy_pids(lines: list[tuple[int, str]]) -> list[int]:
    """Pids of every proxy process that appended to this log."""
    pids: list[int] = []
    for _, msg in lines:
        if msg.startswith("proxy_started"):
            for token in msg.split():
                if token.startswith("pid="):
                    try:
                        pids.append(int(token.split("=", 1)[1]))
                    except ValueError:
                        pass
    return pids


def invoke_recorded(
    registry,
    name: str,
    kwargs: dict[str, Any],
    *,
    label: str,
) -> Any:
    """Invoke a tool and record the FULL outcome with elapsed ms.

    Returns the outcome object.  Records, per branch:
    * ``ToolCallResult`` with a normal value: success.
    * ``ToolCallResult`` whose stringified ``result`` carries
      ``is_error=True``: the CLASSIFIED failure path (ToolRegistry 0.15.0
      returns the isError CallToolResult stringified -- see report) --
      captured verbatim, logged as a failure.
    * ``ErrorResult``: ``outcome.message`` verbatim.
    * raised exception (defensive; invoke() should not raise).
    """
    start_ms = now_ms()
    try:
        outcome = registry.invoke(name, kwargs)
    except Exception as exc:
        end_ms = now_ms()
        hlog(
            f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
            f"raised={type(exc).__name__}|msg={exc!r}"
        )
        return None
    end_ms = now_ms()
    if hasattr(outcome, "message"):
        hlog(
            f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
            f"ok=False|outcome_type={type(outcome).__name__}|message_verbatim={outcome.message!r}"
        )
        return outcome
    if hasattr(outcome, "result"):
        result = outcome.result
        result_str = repr(result)
        if all(marker in result_str for marker in CLASSIFIED_ERROR_MARKERS):
            hlog(
                f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
                f"ok=False|outcome_type={type(outcome).__name__}|classified_error=yes|"
                f"result_verbatim={result_str!r}"
            )
        else:
            hlog(
                f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
                f"ok=True|result={result!r}|result_type={type(result).__name__}"
            )
        return outcome
    hlog(
        f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
        f"ok=False|outcome_type={type(outcome).__name__}|outcome_repr={outcome!r}"
    )
    return outcome


def wait_for_persistent_proxy_pid(
    proxy_pid_file: str | Path,
    proxy_log: str | Path,
    *,
    timeout_s: float = 60.0,
) -> int | None:
    """Wait until the persistent proxy has started processing a call.

    The pid file is written by every proxy process; the registration-time
    temporary proxy exits after ``tools/list``, so once ``backend_spawn_start``
    appears in the proxy log (which only happens inside the persistent
    proxy's ``on_call_tool``), the ALIVE pid in the pid file must be the
    persistent proxy.  Returns its pid or None on timeout.
    """
    deadline = time.time() + timeout_s
    seen_backend_spawn = False
    while time.time() < deadline:
        if Path(proxy_log).exists():
            lines = read_proxy_log(proxy_log)
            if first_event(lines, "backend_spawn_start") is not None:
                seen_backend_spawn = True
        if seen_backend_spawn:
            p = Path(proxy_pid_file)
            if p.exists():
                try:
                    pid = int(p.read_text(encoding="utf-8").strip())
                except (ValueError, OSError):
                    pid = None
                if pid is not None:
                    try:
                        os.kill(pid, 0)
                        return pid
                    except ProcessLookupError:
                        pass
        time.sleep(0.05)
    return None


def kill_proxy_mid_call(
    proxy_pid_file: str | Path,
    proxy_log: str | Path,
) -> int | None:
    """Kill the persistent proxy while the first call is in flight.

    Returns the killed pid, or None if the wait timed out.
    """
    pid = wait_for_persistent_proxy_pid(proxy_pid_file, proxy_log)
    if pid is None:
        hlog(f"KILL_MID_CALL proxy_pid=NOT_FOUND (timeout waiting for backend_spawn_start)")
        return None
    hlog(f"KILL_MID_CALL killing_persistent_proxy pid={pid}")
    os.kill(pid, signal.SIGKILL)
    return pid


def print_manifest_schemas(manifest_path: str | Path) -> None:
    """Log the cached manifest's declared input/output schemas for evidence."""
    import json

    with open(manifest_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    for t in tools:
        hlog(
            f"MANIFEST_TOOL name={t.get('name')} "
            f"input_schema={json.dumps(t.get('input_schema'))} "
            f"output_schema={json.dumps(t.get('output_schema'))}"
        )
