#!/usr/bin/env python
"""Shared helpers for the C2-gap investigation phases (#228).

Evidence instruments, not a product — same conventions as the #213
``common_drift.py`` and #217 ``common_retry.py``, with the additions this
investigation needs:

* ``make_transport`` takes the proxy path explicitly (control runs the
  ORIGINAL #213 drift proxy; Option A runs ``proxy_self_heal.py``; Option B
  registers manually against the original proxy), and passes the self-heal
  proxy's knobs: ``PROXY_HEAL_STATE`` (persisted healed-manifest file),
  ``PROXY_HEAL_THRESHOLD`` (N), ``PROXY_CLASSIFY_SCHEMA`` (whether the
  #217 classification delta is enabled), and ``PROXY_BACKEND_SCRIPT``
  (the intermittent backend variant for the flapping check).
* ``invoke_recorded`` records every outcome class: success value,
  ``ErrorResult.message`` VERBATIM, or the #217-style stringified
  ``ToolCallResult`` repr carrying ``is_error=True`` (the classified
  failure shape) — so a single harness line shows which class each call
  landed in.
* helpers to count ``proxy_started`` / ``backend_spawn_start`` /
  ``self_heal`` / ``backend_schema_validation_failed`` events in a proxy
  log, and to reconstruct per-call spawn increments by comparing
  cumulative counts between calls.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# research/toolregistry-lazy-mcp/c2-gap-investigation/
HERE = Path(__file__).resolve().parent.parent
SELF_HEAL_PROXY = HERE / "proxy_self_heal.py"
BACKEND_PATH = HERE / "backend.py"
INTERMITTENT_BACKEND = HERE / "backend_intermittent.py"
# Run-scoped copy for the #287 re-validation (2026-08-08): logs go to a
# dedicated revalidation directory so the tracked baseline logs are never
# overwritten. The tracked tests/common_c2.py keeps LOGS_DIR = HERE / "logs".
LOGS_DIR = HERE / "logs" / "revalidation-2026-08-08"

# The #213 corpus proxy (UNMODIFIED) — the Option A control / Option B
# reproduction proxy.  Read-only reference into the committed corpus; the
# c2-gap-investigation corpus never modifies it.
DRIFT_PROXY = HERE.parent / "output-schema-drift" / "proxy.py"

PROXY_LOG_RE = re.compile(
    r"^PROXY\|(?P<iso>\S+)\|epoch_ms=(?P<epoch>\d+)\|rel_ms=\s*(?P<rel>\d+)\|(?P<msg>.*)$"
)

# Signature of a classified schema-validation failure inside the
# stringified CallToolResult repr returned by ToolRegistry 0.15.0.
CLASSIFIED_ERROR_MARKERS = ("is_error=True", "Invalid structured content returned by tool")

# The mcp SDK's output-schema validation RuntimeError signature (raised at
# ToolRegistry level in C2 — mcp/client/session.py:1110).
SCHEMA_VALIDATION_MARKER = "Invalid structured content returned by tool"


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
    proxy_path: str | Path = SELF_HEAL_PROXY,
    manifest: str | None = None,
    backend_schema_mode: str | None = None,
    backend_response_mode: str | None = None,
    backend_pid_file: str | None = None,
    heal_state: str | None = None,
    heal_threshold: str = "1",
    classify_schema: bool = False,
    backend_script: str | Path | None = None,
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
    several parallel agents (measured backend init reaches 12.2 s in #217).
    The same values apply to ALL phases so comparisons are like-for-like.
    """
    env: dict[str, str] = {
        "PROXY_LOG_FILE": proxy_log_path,
        "PROXY_BACKEND_TIMEOUT": proxy_backend_timeout,
        "PROXY_CALL_TIMEOUT": proxy_call_timeout,
    }
    if heal_state:
        env["PROXY_HEAL_STATE"] = str(heal_state)
    env["PROXY_HEAL_THRESHOLD"] = heal_threshold
    if classify_schema:
        env["PROXY_CLASSIFY_SCHEMA"] = "1"
    if backend_script:
        env["PROXY_BACKEND_SCRIPT"] = str(backend_script)
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
      ``is_error=True`` + the schema marker: the CLASSIFIED failure shape.
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


def print_manifest_schemas(manifest_path: str | Path) -> None:
    """Log the cached manifest's declared input/output schemas for evidence."""
    with open(manifest_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    for t in tools:
        hlog(
            f"MANIFEST_TOOL name={t.get('name')} "
            f"input_schema={json.dumps(t.get('input_schema'))} "
            f"output_schema={json.dumps(t.get('output_schema'))}"
        )


def extract_served_snapshots(lines: list[tuple[int, str]]) -> list[str]:
    """Extract the proxy's served-manifest snapshot from tools/list logs."""
    out = []
    for _, msg in lines:
        if msg.startswith("request tools/list") and "served=" in msg:
            out.append(msg)
    return out


def extract_heal_events(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    return events(lines, "self_heal")
