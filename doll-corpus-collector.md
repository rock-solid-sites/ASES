---
title: "Doll Corpus Collector — ATProto AppView Bulk Collector"
tags: ["doll-corpus", "collector", "atproto", "appview", "dollspace.gay", "bulk-collector"]
sources: []
contributors: ["ASES", "OL2r"]
created: 2026-08-27
updated: 2026-08-27
---


# Doll Corpus Collector — ATProto AppView Bulk Collector

## Summary

Cheap, unauthenticated, resumable bulk collector for `dollspace.gay` via the public ATProto AppView (`public.api.bsky.app`). Resolves handle → DID (`did:plc:dzvxvsiy3maw4iarpvizsj67`), paginates `app.bsky.feed.getAuthorFeed` with opaque cursor (`limit=100`) until exhaustion — **205 pages / 19,932 posts** (21,413 scanned, deduped by AT URI) in the canonical Doll run — using atomic writes (temp-then-rename), cursor advanced only after safe write, and strict local git boundary (`raw/`/`normalized/`/`state/`/`corpus/`/`derived/`/`__pycache__/` ignored). Standard library only (`urllib`), no auth, no browser, no LLM.

## Usage

```bash
python3 research/doll-corpus/collector.py collect|classify|hydrate|render|all [options]
```

| Subcommand | What it does |
|------------|--------------|
| `collect`  | Paginate `getAuthorFeed` → byte-faithful `raw/author-feed/NNNNNN.json` |
| `classify` | Normalize + dedup by AT URI → `normalized/posts.jsonl` (full `source` preserved) + local relevance → `normalized/relevant-posts.jsonl` (reposts flagged, never treated as authored) |
| `hydrate`  | `getPostThread` for every relevant authored post → `raw/threads/` + `normalized/thread-posts.jsonl`; `getPosts` for quoted posts → `raw/quoted/` + `normalized/quoted-posts.jsonl` |
| `render`   | Emit `corpus/index.md`, `corpus/chronology.md`, `corpus/relevant-posts.md`, `corpus/threads.md` + `stats.json` |
| `all`      | Full pipeline: `collect → classify → hydrate → render` |

**Options (via `add_common_options`):**

- `--author` (default `dollspace.gay`), `--output` (default `research/doll-corpus`), `--base` (default `https://public.api.bsky.app`)
- `--since` / `--until` ISO timestamps — narrowing only, raw stays complete
- `--resume` — resume from persisted cursor (`state/collector.json`); fresh run without it clears `raw/` dirs
- `--filter` — internal `posts_with_replies` vs `posts_and_author_threads`; Gate 0 probe pages both filters one page each — **68/100 gap** observed (`posts_and_author_threads` omits author's replies to others), fallback is `posts_with_replies` (verified against `postsCount 14,333`)
- `--delay` (default `0.35`, floor `0.2` → ~5 req/s ceiling) / `--concurrency` (default `2`, clamped 1–8) — global `RateLimiter` serializes all request starts
- `--max-retries` (default `5`), `--max-pages` (probe mode), `--rehydrate` / `--no-hydrate`

## Key Design

- **Raw lossless:** every `getAuthorFeed` page stored byte-faithful; no parsing before write.
- **Normalized with full source:** `build_post_record()` dedups by AT URI, preserves complete `source` item, flags `item_type: repost|post` (reposts never treated as authored, authored appearance wins on duplicate).
- **Dedup:** AT URI primary key; `collected_uris` index in `state/collector.json`; pagination duplicates collapsed with `source_pages` provenance.
- **Thread hydration:** `getPostThread` with `depth=1000, parentHeight=1000` per relevant authored URI; concurrent via `ThreadPoolExecutor` but globally rate-limited; skipped `notFoundPost`/`blockedPost` nodes counted.
- **Quoted posts:** `getPosts` batched `GETPOSTS_BATCH=25` for every `quote_ref` in relevant posts.
- **Rate limit:** shared `RateLimiter` ≤ 5 req/s (default ~2–3 req/s); `REQUEST_TIMEOUT=30s`.
- **Retries:** exponential backoff `BACKOFF_BASE=1.0, BACKOFF_CAP=60` + jitter `0–0.5s`; HTTP 429 honours `Retry-After`; 408/5xx retried, 4xx (except 408/429) is `FatalRequestError`.
- **Resumable:** `state/collector.json` persists `cursor`, `pages`, `page_files`, `collected_uris`, `threads_index`, `cumulative` counters; `cursor` advanced only after atomic page write; re-run with `--resume`.
- **No auth / browser / LLM:** public AppView only (`xrpc_get` via `urllib`), `USER_AGENT=doll-corpus-collector/<version>`.

## Resilience

- **Streaming:** never hold full corpus in RAM; page-by-page `jsonl_stream` / `jsonl_write` with `atomic_write_bytes` (tmp→rename + `fsync`).
- **<2 m checkpoint:** state flushed after every page and every 25 thread fetches; `save_state()` is atomic JSON.
- **Strict `.gitignore`:** `research/doll-corpus/.gitignore` ignores `raw/`, `normalized/`, `state/`, `corpus/`, `derived/`, `__pycache__/` — derived bulk disk-only, never staged; verify with `git check-ignore -v -- <path>`.
- **Disk:** ~293 MB canonical run (raw pages + normalized + threads + derived); stays below 500 MB streaming budget.
- **Errors never silent:** `MAX_ERRORS_KEPT=2000` in `state/collector.json` + `stats.json`; `stats.json` reports `http_requests / retries / api_errors`.

## Links

- Design Gate 0: `.design/doll-corpus-extraction.md` (probe & scope — filter behaviour, 68/100 gap)
- Collector: `research/doll-corpus/collector.py` (subcommands `collect|classify|hydrate|render|all`)
- Layout & state: `research/doll-corpus/README.md` (if present), `research/doll-corpus/state/collector.json`, `research/doll-corpus/stats.json` (rendered), `research/doll-corpus/derived/gate1/stats.json`
- Retrospective: `docs/research/doll-corpus-retrospective.md` (full §1–§9, resilience forensics)
- Extraction method: `.crosslink/knowledge/doll-corpus-extraction.md` (Gates 0–10, vocab `d8cca707`)
- Issues: #491 (Doll Corpus extraction), #471 (AppView probe — filter evidence `posts_with_replies`)

## Quick Lookup

| Need | Value |
|------|-------|
| Endpoint | `https://public.api.bsky.app` (unauthenticated) |
| DID | `did:plc:dzvxvsiy3maw4iarpvizsj67` |
| Pages / posts | 205 / 19,932 (21,413 scanned) |
| Cursor | opaque, persisted per page |
| Filter | `posts_with_replies` (fallback after 68/100 probe gap) |
| Thread hydration | `depth=1000, parentHeight=1000`, batch `25` for quotes |
| Rate | `0.35s` default (floor `0.2s` → 5/s), timeout `30s` |
| Retries | `5`, backoff `1.0*2^(n-1)` cap `60` + jitter |
| State | `research/doll-corpus/state/collector.json` |
| Git boundary | `raw/ normalized/ state/ corpus/ derived/ __pycache__/` |
