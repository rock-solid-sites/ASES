#!/usr/bin/env python
"""Shared helpers for the output-schema-drift phases.

These scripts are evidence instruments, not a product.  Every harness
line is printed to stdout/stderr prefixed ``HARNESS|`` with an ISO
timestamp (ms) and ``epoch_ms`` so timings can be correlated with the
proxy log (``PROXY|``) and backend log (``BACKEND|``) lines.

Based on the #196 ``tests/common.py`` with the additions this
investigation needs:

* ``make_transport`` accepts ``manifest`` (PROXY_MANIFEST), and
  ``backend_schema_mode`` / ``backend_response_mode`` which are passed
  through the proxy to the backend as ``BACKEND_SCHEMA_MODE`` /
  ``BACKEND_RESPONSE_MODE``.
* ``invoke_recorded`` records the full outcome of ``registry.invoke``:
  success value, OR the ``ErrorResult.message`` VERBATIM (which carries
  the ``"ExceptionType: Error executing <tool>: <msg>"`` string produced
  by ToolRegistry 0.15.0's ``_collect_handle_result`` + ``_ToolError``),
  plus elapsed ms.
* helpers to count ``proxy_started`` and ``backend_spawn_start`` events in
  a proxy log (multiple proxy processes append to the same log file).
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# research/toolregistry-lazy-mcp/output-schema-drift/
HERE = Path(__file__).resolve().parent.parent
PROXY_PATH = HERE / "proxy.py"
BACKEND_PATH = HERE / "backend.py"
LOGS_DIR = HERE / "logs"

PROXY_LOG_RE = re.compile(
    r"^PROXY\|(?P<iso>\S+)\|epoch_ms=(?P<epoch>\d+)\|rel_ms=\s*(?P<rel>\d+)\|(?P<msg>.*)$"
)


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
    manifest: str | None = None,
    backend_schema_mode: str | None = None,
    backend_response_mode: str | None = None,
    backend_pid_file: str | None = None,
) -> dict[str, Any]:
    """Build the stdio transport dict for ``register_from_mcp``.

    The mcp SDK's ``stdio_client`` only inherits a safe env subset
    (HOME/LOGNAME/PATH/SHELL/TERM/USER) plus whatever ``env`` we pass,
    so probe control variables must be passed explicitly here.
    """
    env: dict[str, str] = {
        "PROXY_LOG_FILE": proxy_log_path,
    }
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
        "args": [str(PROXY_PATH)],
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


def backend_pid_from_file(path: str | Path) -> int | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return int(p.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def invoke_recorded(
    registry,
    name: str,
    kwargs: dict[str, Any],
    *,
    label: str,
) -> Any:
    """Invoke a tool and record the FULL outcome with elapsed ms.

    Returns the outcome object (ToolCallResult or ErrorResult).  Records:
    * success: the result value.
    * ErrorResult: ``outcome.message`` VERBATIM (the exact string
      ToolRegistry 0.15.0 builds), plus elapsed ms.
    * raised exception (defensive; invoke() should not raise): type +
      message verbatim.
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
    if hasattr(outcome, "result"):
        hlog(
            f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
            f"ok=True|result={outcome.result!r}|result_type={type(outcome.result).__name__}"
        )
        return outcome
    # ErrorResult or unexpected
    message = getattr(outcome, "message", repr(outcome))
    hlog(
        f"INVOKE|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
        f"ok=False|outcome_type={type(outcome).__name__}|message_verbatim={message!r}"
    )
    return outcome


def validate_input_against_manifest(
    manifest_path: str | Path,
    tool_name: str,
    arguments: dict[str, Any],
) -> tuple[bool, str]:
    """Validate tool arguments against the CACHED manifest input schema.

    Test D's explicit check that the INPUT is valid per the cached schema
    (this is NOT an input-validation failure).  Uses jsonschema (an mcp
    dependency) exactly as mcp/client/session.py does for outputs.
    """
    import jsonschema

    with open(manifest_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = raw.get("tools", raw) if isinstance(raw, dict) else raw
    for t in tools:
        if t.get("name") == tool_name:
            schema = t.get("input_schema") or t.get("inputSchema") or {}
            try:
                jsonschema.validate(instance=arguments, schema=schema)
                return True, "valid per cached input schema"
            except jsonschema.ValidationError as exc:
                return False, f"INVALID: {exc.message}"
    return False, f"tool {tool_name} not found in manifest"


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
