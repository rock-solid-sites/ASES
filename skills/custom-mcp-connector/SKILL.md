---
name: custom-mcp-connector
version: 0.1
summary: Set up and troubleshoot custom MCP connectors in ChatGPT using the live Plugins UI as ground truth. Use when creating or repairing a custom MCP connection, especially when current ChatGPT menus differ from documentation.
---

# Custom MCP Connector

Use this skill when creating, connecting, or troubleshooting a custom MCP connector in ChatGPT.

This skill exists because MCP setup has repeatedly failed when guidance followed stale or mismatched UI documentation instead of the actual Plugins interface.

## Core rule

For custom MCP setup, treat the **current Plugins UI and live connector behavior as primary evidence**.

Evidence order:

1. the current ChatGPT Plugins UI visible to the user or browser agent;
2. live connector/tunnel/tool behavior;
3. current official OpenAI documentation for semantics and requirements;
4. remembered or historical menu paths.

If documentation conflicts with the current UI, record the mismatch and continue from the observed interface. Do not keep searching for a documented menu that the user has already shown is absent.

## Current observed ChatGPT MCP connection surface

Observed 2026-09-26 on the working Strategy Code Graph setup.

The working entry point was the **Plugins** page and its **Add (+)** control.

Do not assume that a separate settings page called "Developer mode" is required. In the observed UI, the settings result named **Developer mode** was for **Cloud browser** permissions and was unrelated to MCP connector creation.

The Add connection modal exposed:

- **Name**
- **Description (optional)**
- **Connection**
  - `Server URL`
  - `Tunnel`
- **Authentication** when applicable
  - `OAuth`
  - `No authentication`
  - `OAuth or no authentication`
- **Advanced OAuth settings**
  - Client ID
  - Client secret
  - Authorization URL
  - Token URL
  - Scopes
- trust warning
- `I understand and want to continue`
- `Create`
- `Cancel`

Treat these as dated observed controls, not a permanent UI contract. If the live UI differs, use the live UI and update the record rather than forcing these labels onto it.

## Setup procedure

### 1. Start from Plugins

Open the ChatGPT **Plugins** management surface and look for the Add (`+`) control.

If the documented route to Plugins does not match the current account UI, use the route actually visible in the product. Do not infer that MCP is unavailable merely because a documented settings path is missing.

### 2. Choose the connection type

Use **Server URL** when ChatGPT should reach a public HTTPS MCP endpoint directly.

Use **Tunnel** when the MCP service is private/local and connected through OpenAI Secure MCP Tunnel.

Do not redesign the transport until the actual connection options in the current UI have been inspected.

### 3. Choose authentication based on the real architecture

Do not add OAuth just because OAuth fields are visible.

Use **No authentication** at the ChatGPT plugin layer when authentication is already handled elsewhere in the connection path, such as a Secure MCP Tunnel client injecting a private upstream Authorization header.

Use OAuth only when the MCP server itself requires an OAuth flow that ChatGPT must participate in.

Do not expose static secrets in URLs or ask the user to paste backend bearer tokens into ChatGPT connector fields unless the product explicitly supports and requires that mechanism.

### 4. Create, then verify tool discovery

After Create:

- confirm the connection reports Connected;
- inspect the discovered MCP tools;
- compare them with the expected allowlisted/read-only surface;
- make one small real tool call;
- corroborate the request on the backend when the connector path is security-sensitive.

Do not treat successful creation alone as end-to-end proof.

## Troubleshooting rules

### When the user says a menu does not exist

Do not provide another guessed path.

Ask for or inspect the current Plugins/settings screen, then continue from visible controls only.

### When a screenshot contradicts documentation

The screenshot wins for navigation.

Use documentation only to explain the visible controls or confirm product semantics.

### When a similarly named control exists

Do not assume semantic identity from the label alone.

Example from this incident: `Developer mode` opened Cloud browser permissions and was not the MCP connector setup control.

### When a connector option appears missing

Do not infer plan entitlement from absence alone. Possible causes include changed navigation, rollout, account policy, or a different product surface.

Check the current Plugins UI and account capability independently before concluding the feature is unavailable.

### When setup becomes architecturally complicated

First verify that the difficulty is not merely a UI/navigation mistake.

Do not build an alternate gateway, OAuth layer, proxy, or transport solely because a connector control could not be found in stale documentation.

## Minimal acceptance test

A custom MCP connector is operational only when all applicable checks pass:

- ChatGPT shows the connection as Connected;
- expected tools are discovered;
- one genuine ChatGPT-originated MCP call succeeds;
- the backend receives that call through the intended path;
- security boundaries remain intact after connection.

For a private read-only code service, also verify where relevant:

- backend remains private/loopback-only;
- authentication remains enforced upstream;
- repository/resource allowlists remain unchanged;
- no mutation tools appeared unexpectedly;
- response bounds remain active.

## Strategy Code Graph example

The working connection path was:

`ChatGPT Strategy Chat -> Strategy Code Graph plugin -> Secure MCP Tunnel -> GitNexus -> private T3/Crosslink indexes`

The ChatGPT connection used the Plugins Add (`+`) flow and **Tunnel** connection mode. The backend bearer token was injected by the tunnel client, so ChatGPT did not need a separate OAuth flow to GitNexus.

A successful ChatGPT-originated request was later corroborated on the VPS while GitNexus remained loopback-only, bearer-authenticated, read-only, allowlisted, and bounded.

## Detailed incident reference

The longer incident analysis belongs in the ASES repository and should be consulted when the failure mode itself matters:

`rock-solid-sites/ASES/methodology-reviews/Current-UI-Ground-Truth.md`

Use that document for the chronology, evidence hierarchy, failure analysis, and broader ASES implications. Keep this skill operational and connector-specific.