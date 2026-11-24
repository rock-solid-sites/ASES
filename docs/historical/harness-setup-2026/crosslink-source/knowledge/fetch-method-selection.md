---
title: Fetch Method Selection
tags: webfetch,git,curl,bulk-ingestion,failure-class
---

# Fetch Method Selection

Local fetch = substrate. WebFetch = query.

If you will read most of an external resource (repository, paper, multi-page docs), acquire it locally: git clone --depth 1 or curl -o into /tmp/opencode/, then read and grep files. Repeat access is free, failures are loud and retryable, and committed copies are citable evidence paths.

If you want one answer from one page, WebFetch is appropriate: single round-trip, no cleanup.

Never chain sequential WebFetch calls as bulk ingestion. Each call re-opens a stream-resumption window; four consecutive research-agent freezes on 2026-08-23 followed this exact pattern (evidence: issue #429 termination records, #423 forensics).

Historical note: WebFetch superseded the Fetch-MCP server (removed #202/#203 after measured token savings) and remains the correct tool for interactive spot-checks and exploratory discovery. This page governs volume, not tool loyalty.
