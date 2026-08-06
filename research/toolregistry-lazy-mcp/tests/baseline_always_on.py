#!/usr/bin/env python
"""Baseline: register directly against the real backend (no proxy).

Provides the "always-on registration" latency comparison for Test 3.
With ToolRegistry 0.15.0 the persistent MCP connection is lazy even for
a direct backend, so call 1 still cold-starts the backend process; the
meaningful comparison is steady-state calls 2-4 (proxy hop overhead vs
direct).

Evidence only; not part of the five numbered tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from common import (  # noqa: E402
    BACKEND_PATH,
    hlog,
    now_ms,
    safe_invoke,
    versions_line,
)
from toolregistry import ToolRegistry  # noqa: E402


def main() -> None:
    hlog(f"phase_start phase=baseline-always-on {versions_line()}")
    registry = ToolRegistry(name="baseline")
    transport = {
        "command": sys.executable,
        "args": [str(BACKEND_PATH)],
        "env": {},
    }
    hlog("BASELINE_REGISTER_BEGIN")
    try:
        registry.register_from_mcp(transport)
        hlog("BASELINE_REGISTER result=ok")
    except Exception as exc:
        hlog(f"BASELINE_REGISTER result=FAILED error={exc!r}")
        sys.exit(2)

    safe_invoke(registry, "add", {"a": 2, "b": 3}, "5.0")  # cold (spawns backend)
    for i, (a, b, expected) in enumerate(
        [(4, 5, "9.0"), (10, 20, "30.0"), (0, 0, "0.0"), (1, 1, "2.0")],
        start=1,
    ):
        safe_invoke(registry, "add", {"a": a, "b": b}, expected)

    registry.close()
    hlog("phase_done phase=baseline-always-on")


if __name__ == "__main__":
    main()
