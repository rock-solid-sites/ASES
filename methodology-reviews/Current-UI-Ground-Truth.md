# Methodology Review: Current UI Ground Truth for Fast-Moving Product Interfaces

**Date:** 2026-09-26  
**Evaluator:** Strategy Chat / user-observed interface  
**Incident:** Strategy Code Graph plugin setup  
**Scope:** ChatGPT plugin/MCP setup guidance, documentation conflict, evidence hierarchy  
**Status:** Accepted methodological correction

## 1. Overview

During setup of the Strategy Code Graph plugin, Strategy Chat repeatedly gave navigation and account guidance that did not match the user's actual ChatGPT interface. The failure was not a single stale menu label. It was a repeated evidence-ordering error: direct screenshots and live product behavior were available, but guidance continued to privilege remembered or currently published documentation over the interface actually in front of the user.

The incident eventually succeeded technically. A private GitNexus MCP server remained loopback-only on the VPS, was exposed through OpenAI Secure MCP Tunnel, connected through the ChatGPT Plugins interface, and became callable from Strategy Chat. The infrastructure path was verified end to end. The process for reaching that state, however, contained avoidable UI speculation, false product-access conclusions, and unnecessary troubleshooting.

This review extracts a reusable methodology for any rapidly changing UI: ChatGPT, Codex, OpenCode, Cloudflare dashboards, developer consoles, plugin systems, account settings, or similar products.

The central correction is:

> **When direct current observation conflicts with documentation, observed current UI and live behavior are the operational source of truth.**

Official documentation remains valuable for semantics, requirements, security properties, and unsupported states. It must not be used to overwrite direct evidence that the interface has moved, been renamed, or differs by account/surface.

## 2. Incident context

The technical goal was to connect a locally running GitNexus code-graph MCP service to ChatGPT as a personal plugin. The backend had already been heavily verified:

- GitNexus listened only on `127.0.0.1:3010`.
- Bearer authentication was enforced.
- The repository allowlist was exactly `t3-code` and `crosslink`.
- The MCP surface was read-only.
- The default response budget was 4000 tokens.
- OpenAI Secure MCP Tunnel was configured and running.
- A genuine ChatGPT-originated request later traversed the tunnel and reached GitNexus.

The remaining task was expected to be a small ChatGPT-side connection step.

Instead, Strategy Chat repeatedly described menu paths that the user could not find.

## 3. Observations (evidence)

### OBS-01 — Settings search exposed two distinct “developer” surfaces

The user searched ChatGPT Settings for `developer` and showed a screenshot with two results:

- **Developer → Plugins**
- **Developer mode → Cloud browser**

The second item opened a Cloud browser settings page containing browser permissions, website permissions, an Add website control, and browser-data controls. It was unrelated to MCP/plugin connection setup.

### OBS-02 — The documented Developer mode path did not match the observed UI

Current OpenAI plugin documentation stated a path equivalent to:

`Settings → Security and login → Developer mode`

That section did not exist in the user's observed UI.

Relevant current documentation:

- https://developers.openai.com/plugins/deploy/connect-chatgpt
- https://developers.openai.com/plugins/build/app-quickstart

The mismatch persisted even though the plugin capability itself was present.

### OBS-03 — The Plugins page was the real working surface

The user reached the Plugins management page. Observed controls included:

- **Browse directory**
- installed plugin search
- default permission controls
- per-plugin permission settings
- an Add (`+`) control for creating a connection

The Add control opened the MCP/plugin connection modal.

### OBS-04 — The actual connection modal exposed more options than Strategy Chat had described

The observed modal contained:

- **Name**
- **Description (optional)**
- **Connection**
  - `Server URL`
  - `Tunnel`
- **Authentication**
  - `OAuth`
  - `No authentication`
  - `OAuth or no authentication`
- **Advanced OAuth settings**
  - `Client ID (optional)`
  - `Client secret (optional)`
  - `Authorization URL (optional)`
  - `Token URL (optional)`
  - `Scopes (optional, one per line)`
- trust warning
- `I understand and want to continue` checkbox
- `Create`
- `Cancel`

This was direct evidence of the real feature surface.

The underlying authentication choices are consistent with OpenAI's MCP authentication documentation, which describes `noauth`, `oauth2`, and mixed optional-auth tool configurations:

- https://developers.openai.com/plugins/build/auth

### OBS-05 — Tunnel mode worked on the user's actual account

The user selected **Tunnel**, connected the registered Strategy Code Graph tunnel, and the plugin became **Connected**.

Strategy Chat subsequently saw the live `Strategy_Code_Graph` MCP tool namespace and the GitNexus read-only tools.

Therefore, prior claims that the account probably lacked the required MCP capability were false for this account.

### OBS-06 — Live end-to-end behavior confirmed the connection

Host-side corroboration showed:

- genuine ChatGPT-originated requests reached `gitnexus-tunnel.service`;
- dispatch counters increased;
- GitNexus remained loopback-only;
- bearer authentication remained enforced;
- the allowlist remained exactly `t3-code + crosslink`;
- the read-only tool surface was unchanged;
- the 4000-token default budget remained active.

Final host corroboration artifact:

`/tmp/opencode/gitnexus-acceptance/tasks/task21-final-corroboration.md`

Earlier tunnel and validation artifacts remained preserved under:

`/tmp/opencode/gitnexus-acceptance/tasks/`

### OBS-07 — OpenAI's Secure MCP Tunnel documentation correctly described the final connection primitive

OpenAI's current Secure MCP Tunnel documentation states that ChatGPT Plugins can create a developer-mode app and choose **Tunnel** under Connection:

- https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

That documentation correctly described the modal capability, while the preceding settings-navigation guidance elsewhere did not match the observed account UI.

## 4. Strategy Chat guidance failures

### FIN-01 — Documentation was incorrectly treated as stronger evidence than the running product

Once the user supplied screenshots, the interface itself should have become the primary source for navigation.

Instead, Strategy Chat continued trying to reconcile the user's screen with a documented path. This reversed the appropriate evidence order.

The correct response after the first contradiction should have been:

> “The documented navigation does not match your current UI. I will use the interface you are showing as ground truth from here and use documentation only to interpret visible controls.”

### FIN-02 — A similarly named control was misclassified

The Settings search result **Developer mode → Cloud browser** was initially treated as though it might be the documented MCP Developer mode setting.

The user then showed the page, which clearly contained Cloud browser permissions. At that point the classification should have been corrected immediately and permanently.

A label match is not evidence of semantic identity.

### FIN-03 — Product entitlement was inferred from a missing documented path

Strategy Chat inferred that the user's Plus account might not support custom MCP connections because the expected Developer mode menu was absent.

That inference was disproved by the user's later screenshots of the actual MCP connection modal and by the successful live connection.

A missing menu path is ambiguous evidence. Causes can include:

- changed navigation;
- alternate product surfaces;
- feature rollout;
- renamed settings;
- account policy;
- plan entitlement.

No one cause should be selected without independent evidence.

### FIN-04 — The failure compounded through repeated confident instructions

The problem was not merely an initial wrong path. After multiple mismatches, Strategy Chat continued producing new path hypotheses.

Repeated confident guesses are worse than a short uncertainty statement because they:

- consume user time;
- encourage unnecessary account changes;
- create false architectural constraints;
- generate downstream troubleshooting tasks based on premises that may already be wrong.

### FIN-05 — Some subsequent infrastructure research was valid, but UI uncertainty contaminated scope

The Cloudflare-vs-Secure-MCP-Tunnel comparison was technically useful and produced real findings about transport and authentication. It should not be dismissed as wholly wasted work.

However, account-plan speculation and repeated navigation failures expanded the setup effort beyond what the actual Plugins UI required.

The methodology correction is therefore not “never research alternatives.” It is “do not let an unverified UI assumption become an architectural premise.”

## 5. Evidence hierarchy for current-product UI work

For current UI navigation, use this hierarchy:

1. **Observed current interface and live behavior**
   - user screenshots;
   - browser/computer-use observation;
   - exact visible labels;
   - successful/failed live actions.

2. **Current product state exposed through supported APIs/tools**
   - actual account capability returned by the product;
   - discovered plugin/tool surface;
   - server responses and runtime behavior.

3. **Current official documentation**
   - use for semantics, requirements, supported states, security properties, and intended workflows;
   - do not force its navigation path onto a contradictory observed interface.

4. **Historical documentation, remembered paths, prior-conversation knowledge, model memory**
   - useful only as search hypotheses.

This hierarchy is task-specific. For normative API contracts where there is no contradictory live behavior, official documentation can remain authoritative. The special rule applies to **current interface navigation and surface availability**, where deployment can move faster than docs.

## 6. Required operating procedure

### 6.1 Establish the observed state

Before giving multi-screen directions, identify:

- product and surface;
- page title;
- visible navigation items;
- exact button/field labels;
- current selection state;
- account/workspace context only if shown.

If the user provides a screenshot, inspect it before giving the next step.

### 6.2 Detect a documentation mismatch

If a documented path differs from the current UI:

1. record the mismatch;
2. stop repeating the documented path;
3. continue from visible controls;
4. use docs to understand those controls;
5. ask for the next screen only if the branch remains uncertain.

### 6.3 Advance one screen at a time under uncertainty

When navigation is uncertain, prefer:

> “Click the visible Plugins entry. Show me the next screen.”

over:

> “Open A, enable B, go to C, select D, then configure E.”

One-screen progression minimizes compounding errors.

### 6.4 Do not infer capability from absence alone

Do not convert “I cannot find this documented setting” into “your plan/account does not support this” without a separate entitlement source.

If the user later reaches the feature through another path, update the model immediately rather than defending the earlier interpretation.

### 6.5 Prefer browser execution for tedious administration

Where a browser/computer-use agent can operate an authenticated session, repetitive account/dashboard setup should be delegated rather than converted into a long human tutorial.

Keep the user in the loop for:

- entering secrets;
- security-sensitive confirmations;
- irreversible actions;
- identity/authentication challenges that require the user.

### 6.6 Preserve time-scoped UI ground truth

For recurring workflows, capture:

- observation date;
- product/surface;
- exact labels;
- working route;
- conflicting documented route;
- screenshots/evidence where appropriate.

Do not present the record as timeless. UI evidence ages.

## 7. Current ChatGPT plugin UI record — 2026-09-26

This section records the interface actually observed in this incident.

### Settings search

Searching `developer` produced:

- **Developer → Plugins**
- **Developer mode → Cloud browser**

The Cloud browser Developer mode page was not an MCP/plugin developer-mode switch.

### Plugins management surface

Observed capabilities included:

- browse plugin directory;
- search installed plugins;
- default plugin permissions;
- per-plugin permission settings;
- Add (`+`) connection flow.

### Add connection modal

Observed fields and choices:

| Area | Observed options |
|---|---|
| Name | text field |
| Description | optional text field |
| Connection | Server URL; Tunnel |
| Authentication | OAuth; No authentication; OAuth or no authentication |
| Advanced OAuth | Client ID; Client secret; Authorization URL; Token URL; Scopes |
| Safety | trust warning + acknowledgement checkbox |
| Actions | Create; Cancel |

### Verified Tunnel behavior

The registered Strategy Code Graph Secure MCP Tunnel was selectable/usable through the connection flow. Once connected, ChatGPT discovered the GitNexus tool surface and Strategy Chat could see and call it.

## 8. Relationship to official documentation

The incident does not establish that OpenAI documentation is generally unreliable.

It establishes a narrower fact:

- the current docs accurately describe important MCP/Tunnel semantics;
- at least one documented ChatGPT navigation path did not match the user's current UI;
- the actual Plugins connection modal contained the required capability.

Useful current references:

- Plugin connection/testing: https://developers.openai.com/plugins/deploy/connect-chatgpt
- Secure MCP Tunnel: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
- Authentication: https://developers.openai.com/plugins/build/auth
- Skills: https://developers.openai.com/plugins/build/skills

When those pages disagree with the running UI on navigation, preserve the discrepancy instead of normalizing the UI back to the documentation.

## 9. Relevance to ASES

This incident reinforces several ASES principles.

### 9.1 Evidence freshness is part of provenance

“Official” and “current” are different dimensions.

A source can be authoritative about intended semantics while stale about interface location. Provenance should therefore capture not only source authority but observation time and directness.

### 9.2 Cheap direct observation should precede broad reasoning

A screenshot answered the navigation question more cheaply than repeated searches, account-plan inference, and architectural speculation.

This is a concrete example of the EDASES efficiency principle: use the cheapest reliable evidence first.

### 9.3 Failed hypotheses should be retired, not defended

Once the observed UI falsifies a path, preserve that negative result and stop recomputing it.

Repeatedly searching for the same nonexistent menu is wasted work and a failure to reuse negative evidence.

### 9.4 Structural constraints should reduce user burden

When browser automation is available, the system should use it for tedious UI work rather than externalizing administrative complexity to the user.

### 9.5 Current-interface observations are ephemeral knowledge

UI notes should not be promoted into timeless canonical ontology. They should be versioned or dated operational knowledge with explicit freshness limits.

## 10. Extracted reusable skill

A reusable `ui-ground-truth` skill was created from this incident.

Its core behavior is:

- inspect current UI first;
- prefer screenshots/live state over conflicting navigation docs;
- record mismatches;
- advance one screen at a time when uncertain;
- avoid entitlement inference from missing controls;
- use docs for semantics after the live surface is established;
- preserve dated UI-ground-truth notes for repeated workflows.

The skill belongs in the user's installable skill library rather than in ASES canonical architecture.

## 11. Acceptance criteria for future UI guidance

UI guidance is acceptable when:

- each navigation step refers to a control actually observed or independently verified;
- documented-but-conflicting paths are explicitly marked as mismatches;
- capability/plan claims have evidence independent of a missing menu;
- the model stops speculating after the first demonstrated mismatch;
- user-supplied screenshots materially change subsequent instructions;
- repeated workflows preserve a dated current-UI note.

UI guidance is not acceptable when:

- it repeats a path the user has shown does not exist;
- it maps a similarly named control to a different feature without inspection;
- it infers product entitlement from absence alone;
- it escalates to architecture changes before validating the visible product surface.

## 12. Outcome

The incident ended successfully:

`ChatGPT Strategy Chat → Strategy Code Graph plugin → Secure MCP Tunnel → GitNexus → private T3/Crosslink indexes`

The important methodological result is independent of that implementation:

> **For fast-moving product interfaces, direct current observation is evidence, not anecdote. Once it conflicts with documentation, navigation must proceed from the observed interface.**

That rule should be applied broadly across ASES-supported workflows involving external products.
