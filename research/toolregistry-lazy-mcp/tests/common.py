#!/usr/bin/env python
"""Shared helpers for the ToolRegistry lazy-proxy validation phases.

These scripts are evidence instruments, not a product.  Every harness
line is printed to stdout/stderr prefixed ``HARNESS|`` with an ISO
timestamp (ms) and ``epoch_ms`` so timings can be correlated with the
proxy log (``PROXY|``) and backend log (``BACKEND|``) lines.

Environment expectation: this module runs inside the pinned test venv
(``/tmp/toolregistry-venv``), so ``sys.executable`` is the venv python.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# research/toolregistry-lazy-mcp/
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
    backend_pid_file: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the stdio transport dict for ``register_from_mcp``.

    The mcp SDK's ``stdio_client`` only inherits a safe env subset
    (HOME/LOGNAME/PATH/SHELL/TERM/USER) plus whatever ``env`` we pass,
    so probe control variables must be passed explicitly here.
    """
    env: dict[str, str] = {
        "PROXY_LOG_FILE": proxy_log_path,
    }
    if backend_pid_file:
        env["BACKEND_PID_FILE"] = backend_pid_file
    if extra_env:
        env.update(extra_env)
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


def backend_pid_from_file(path: str | Path) -> int | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return int(p.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def print_registry_json(registry) -> None:
    """Print registry repr (JSON schema dump) as evidence for Test 1."""
    try:
        text = repr(registry)
    except Exception as exc:  # pragma: no cover
        hlog(f"registry_repr_error type={type(exc).__name__} msg={exc!r}")
        return
    hlog("registry_repr_begin")
    for line in text.splitlines():
        print(f"REGISTRY|{line}", flush=True)
    hlog("registry_repr_end")


def summarize_call(
    label: str,
    start_ms: int,
    end_ms: int,
    result: Any,
    expected: Any,
) -> None:
    ok = result == expected
    hlog(
        f"CALL|{label}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
        f"result={result!r}|result_type={type(result).__name__}|expected={expected!r}|pass={ok}"
    )


def safe_invoke(registry, name: str, kwargs: dict[str, Any], expected: Any) -> Any:
    """Invoke a tool, returning the outcome value (never raising).

    ``registry.invoke`` returns ``ToolCallResult`` on success and
    ``ErrorResult`` on failure; only the former has ``.result``.
    """
    start_ms = now_ms()
    try:
        outcome = registry.invoke(name, kwargs)
    except Exception as exc:  # pragma: no cover - defensive
        end_ms = now_ms()
        hlog(
            f"CALL|{name}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
            f"raised={type(exc).__name__}:{exc}|expected={expected!r}|pass=False"
        )
        return None
    end_ms = now_ms()
    if hasattr(outcome, "result"):
        value = outcome.result
        summarize_call(name, start_ms, end_ms, value, expected)
        return value
    # ErrorResult or unexpected shape
    hlog(
        f"CALL|{name}|start_ms={start_ms}|end_ms={end_ms}|delta_ms={end_ms - start_ms}|"
        f"outcome_type={type(outcome).__name__}|outcome={outcome!r}|expected={expected!r}|pass=False"
    )
    return None
