---
name: bsky-thread-reader
description: Read Bluesky discussions or public ATProto records through the ATProto Thread Reader Worker. Use for an AT URI, a public Bluesky post, or a readable record/thread—not generic web research.
---

# ATProto Reader

Retrieve a readable public ATProto record or discussion through the deployed Worker. This is a read-only rendering path: do not resolve repositories, call PDS endpoints, or call Tangled/Bobbin directly.

## Inputs and route

Accept either:

- a normal public Bluesky post URL: `https://bsky.app/profile/<actor>/post/<rkey>`
- a complete AT URI: `at://<did-or-handle>/<collection-nsid>/<rkey>`

Keep the supplied identifier intact and percent-encode the **entire** value with a real URL encoder such as JavaScript's `encodeURIComponent`. Send it to the canonical reader route:

```text
https://atproto-thread-reader.rss-tools.workers.dev/read?url=<encoded-input>
```

For example:

```text
https://atproto-thread-reader.rss-tools.workers.dev/read?url=https%3A%2F%2Fbsky.app%2Fprofile%2Falice.bsky.social%2Fpost%2F3abc
https://atproto-thread-reader.rss-tools.workers.dev/read?url=at%3A%2F%2Fdid%3Aplc%3Aexample%2Fapp.bsky.feed.post%2F3abc
```

`/thread` remains a compatible alias, but use `/read` for new requests.

## Fetch and render

Fetch the exact Worker URL with the installed Exa connector's direct-fetch capability. In Codex this is `mcp__codex_apps__exa_web_fetch_exa`; on another OpenAI surface, use that surface's exposed Exa direct-fetch tool. Do not search for the URL first. Request enough characters for the full response; if it is visibly truncated, fetch the same URL once more with a larger `maxCharacters` value.

Return the Worker's Markdown as the readable result and preserve its ordering and adapter metadata. The Worker chooses the presentation:

- `app.bsky.feed.post` renders the complete Bluesky ancestor/reply discussion.
- `sh.tangled.feed.comment` renders its subject and nested comments.
- Any other collection uses the generic readable-record fallback.

Add only a short heading or source link when it helps orient the user.

## Formats

The default `/read?url=...` response is the preferred Markdown output. Add `&format=json` only to debug a failed or ambiguous rendering, or when the user specifically needs raw structured output. Do not use JSON as the normal user-facing format.

## Failure handling

- For a non-post Bluesky URL, ask for a `bsky.app/profile/.../post/...` link. For an invalid AT URI, ask for the full `at://repository/collection/rkey` value. Do not guess an identifier or repository.
- If Exa is unavailable, unauthenticated, or rate-limited, report that condition and ask the user to reconnect or retry Exa. Do not substitute ordinary web retrieval.
- If the Worker returns an error, first verify the exact original input and its encoding, then retry the same direct fetch once for a transient failure. If it still fails, report the Worker response and the supplied identifier.
- If Markdown is empty or malformed, use `format=json` only to inspect the raw response; report the original problem if that does not clarify it.

## Why this route

Do not retrieve the `bsky.app` page with an ordinary browser or generic web-fetch workflow when the goal is a readable conversation; it may be client-rendered and omit reply context. Likewise, do not bypass the Worker with generic ATProto, PDS, or Tangled retrieval when its adapter-aware rendering is the requested result. Exa direct fetch is used solely to retrieve the Worker's rendered response.