#!/usr/bin/env python
"""Option B PoC: ToolRegistry-client interception of the C2 schema-validation failure.

Investigation deliverable for #228 Option B — the SMALLEST proof-of-concept
that intercepts the mcp-SDK ``RuntimeError("Invalid structured content
returned by tool ...")`` raised at ToolRegistry level (C2: the proxy passed
the internally-consistent backend response through; the SDK's
``validate_tool_result`` — ``mcp/client/session.py:1110`` — raised against
the STALE cached manifest) and prevents it from reaching ToolRegistry's
reconnect-retry logic (``toolregistry/integrations/mcp/connection.py:106``).

Mechanism (no fork, no monkeypatch of installed sources):

1. :class:`SchemaAwareConnectionManager` subclasses the PUBLIC
   ``MCPConnectionManager`` and overrides the private ``_call_persistent``
   method.  The override replicates the original's connect+call+retry
   semantics EXCEPT: a ``RuntimeError`` whose message carries the SDK's
   schema-validation marker is classified as TERMINAL — it is re-raised
   WITHOUT the reconnect + fresh-proxy + retry cycle.  Genuine connection
   failures (``MCPError(-32000, ...)`` and anything else) keep the original
   reconnect-retry behaviour.

2. Because ``register_from_mcp`` hardcodes ``MCPConnectionManager``
   construction internally (``integration.py:323``) with no injection point,
   :func:`register_with_connection` replicates the small registration loop
   using ONLY public API: ``MCPClient`` (discovery), ``MCPTool.from_tool_json``
   and ``ToolRegistry.register``.  This is the wrapper-code cost the report
   must size.

Consequence for the C2 gap: the caller-visible outcome is still an
``ErrorResult`` (the schema mismatch is real — the call cannot succeed while
the manifest is stale), but the cost drops from 2 backend spawns / 2
persistent proxies / reconnect-retry to 1 backend spawn / 1 persistent proxy
/ no reconnect — the same single-spawn residual that proxy-side
retry-classification achieved for the Test C variant, now reached from the
ToolRegistry side without touching the proxy or the SDK.

Environment: this module is imported by the Option B phase script, which
passes the transport dict and registry.  Logging follows the harness
conventions via ``common_c2.hlog`` (imported lazily to keep the module
importable standalone for the report's line-count).
"""

from __future__ import annotations

import asyncio
from typing import Any

from toolregistry.integrations.mcp.client import MCPClient
from toolregistry.integrations.mcp.connection import MCPConnectionManager
from toolregistry.integrations.mcp.integration import MCPTool

# The mcp SDK's output-schema validation RuntimeError signature
# (mcp/client/session.py:1110) — the exact class the C2 reproduction raises.
SCHEMA_VALIDATION_MARKER = "Invalid structured content returned by tool"


def _is_schema_validation_error(exc: BaseException) -> bool:
    return (
        isinstance(exc, RuntimeError)
        and SCHEMA_VALIDATION_MARKER in str(exc)
    )


class SchemaAwareConnectionManager(MCPConnectionManager):
    """Subclass of the public MCPConnectionManager that classifies the C2
    schema-validation RuntimeError as terminal (no reconnect/retry).

    Overrides the private ``_call_persistent`` seam that contains the
    reconnect-retry logic (connection.py:103-111).  Everything else —
    ``call_tool`` dispatch, ``list_tools``, lifecycle, pickling — is
    inherited unchanged.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.schema_validation_failures = 0

    async def _call_persistent(
        self, name: str, arguments: dict[str, Any]
    ) -> Any:
        """Connect, call, and retry exactly like the base class — EXCEPT a
        schema-validation RuntimeError is terminal: re-raise without the
        reconnect+retry, so connection.py:106's amplification never runs.
        """
        async with self._lock:
            await self._ensure_connected()
        try:
            assert self._client is not None
            return await self._client.call_tool(name, arguments)
        except Exception as exc:
            if _is_schema_validation_error(exc):
                self.schema_validation_failures += 1
                # Terminal: the tool returned structured content that does
                # not conform to the schema ToolRegistry's client absorbed
                # from the (stale) served manifest.  NOT a connection loss.
                raise
            # Original behaviour: any other failure is treated as connection
            # loss -> reconnect + retry once.
            async with self._lock:
                await self._connect()
            assert self._client is not None
            return await self._client.call_tool(name, arguments)


async def _register_async(
    registry,
    transport: dict[str, Any],
    connection: SchemaAwareConnectionManager,
    namespace: bool | str = False,
) -> None:
    """Register tools against a custom connection using public API only.

    Mirrors ``MCPIntegration.register_mcp_tools_async`` (integration.py:
    330-352) except the connection manager is the caller's subclass — the
    one injection point ``register_from_mcp`` does not expose.
    """
    async with MCPClient(transport) as client:
        server_info = client.server_info
        if isinstance(namespace, str):
            resolved_ns = namespace
        elif namespace:
            resolved_ns = server_info.name if server_info else "MCP sse service"
        else:
            resolved_ns = None
        tools_response = await client.list_tools()
        for tool_spec in tools_response:
            mcp_tool = MCPTool.from_tool_json(
                tool_spec=tool_spec,
                connection=connection,
                namespace=resolved_ns,
            )
            registry.register(mcp_tool, namespace=resolved_ns)


def register_with_connection(
    registry,
    transport: dict[str, Any],
    connection: SchemaAwareConnectionManager,
    namespace: bool | str = False,
) -> None:
    """Sync entry point: run :func:`_register_async` on the shared runtime."""
    from toolregistry._async_runtime import AsyncRuntime

    AsyncRuntime.run_sync(
        _register_async(registry, transport, connection, namespace)
    )
