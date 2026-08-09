import { afterEach, expect } from "bun:test"
import { createServer, type Server } from "node:http"
import { streamText } from "ai"
import { LayerNode } from "@opencode-ai/core/effect/layer-node"
import { CrossSpawnSpawner } from "@opencode-ai/core/cross-spawn-spawner"
import { Effect } from "effect"
import { ProviderV2 } from "@opencode-ai/core/provider"
import { ModelV2 } from "@opencode-ai/core/model"
import { disposeAllInstances, provideTmpdirInstance } from "../fixture/fixture"
import { testEffect } from "../lib/effect"
import { testProviderConfig } from "../lib/test-provider"
import { Env } from "@/env"
import { Plugin } from "@/plugin"
import { Provider } from "@/provider/provider"
import { ProviderError } from "@/provider/error"

afterEach(async () => {
  await disposeAllInstances()
})

const it = testEffect(
  LayerNode.compile(LayerNode.group([Provider.node, Env.node, Plugin.node, CrossSpawnSpawner.node])),
)

// Reads the fullStream and returns the first error part (or the thrown error).
// `expect` is used by the caller; this helper keeps each test focused.
async function firstStreamError(result: ReturnType<typeof streamText>): Promise<unknown> {
  try {
    for await (const part of result.fullStream) {
      if (part.type === "error") return part.error
    }
  } catch (error) {
    return error
  }
  return undefined
}

it.live("bodyIdleTimeout raises a response stream error when non-SSE body stalls", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => stalledBodyServer(10_000, "application/json")),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          const error = yield* Effect.promise(() => firstStreamError(result))
          expect(error).toBeInstanceOf(ProviderError.ResponseStreamError)
        }),
      { config: providerConfig(server.url, { bodyIdleTimeout: 100 }) },
    )
  }),
)

it.live("bodyIdleTimeout does not abort slow-but-progressing non-SSE body", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => chunkedBodyServer("application/json", 3, 50)),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          expect(yield* Effect.promise(() => result.text)).toContain("ok")
        }),
      // gaps (50ms) < bodyIdleTimeout (500ms): idle-progress deadline never fires
      { config: providerConfig(server.url, { bodyIdleTimeout: 500 }) },
    )
  }),
)

it.live("bodyAbsoluteTimeout is cleared on completion (no timer leak)", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => chunkedBodyServer("application/json", 2, 50)),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          // Body completes at ~100ms, far below the 400ms absolute cap. If the
          // absolute timer were not cleared on `done`, `fail` would error the
          // already-closed stream and surface as an error part.
          const text = yield* Effect.promise(() => result.text)
          expect(text).toContain("ok")
          const error = yield* Effect.promise(() => firstStreamError(result))
          expect(error).toBeUndefined()
        }),
      {
        config: providerConfig(server.url, { bodyIdleTimeout: 500, bodyAbsoluteTimeout: 400 }),
      },
    )
  }),
)

it.live("bodyAbsoluteTimeout fires deterministically when configured and body stalls", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => stalledBodyServer(10_000, "application/json")),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          const error = yield* Effect.promise(() => firstStreamError(result))
          expect(error).toBeInstanceOf(ProviderError.ResponseStreamError)
          // V3 guard: the stream errors deterministically (consumer read settles)
          expect(String(error)).toContain("Body read deadline exceeded")
        }),
      {
        // idle (10s) >> absolute (200ms): the absolute cap is the mechanism that fires
        config: providerConfig(server.url, { bodyIdleTimeout: 10_000, bodyAbsoluteTimeout: 200 }),
      },
    )
  }),
)

it.live("dispatcher routes SSE bodies through wrapSSE (chunkTimeout), not wrapBodyIdle", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => stalledBodyServer(10_000, "text/event-stream")),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          const error = yield* Effect.promise(() => firstStreamError(result))
          // chunkTimeout (50ms) fires first, well before bodyIdleTimeout (10s)
          expect(error).toBeInstanceOf(ProviderError.ResponseStreamError)
          expect(String(error)).toContain("SSE read timed out")
        }),
      { config: providerConfig(server.url, { chunkTimeout: 50, bodyIdleTimeout: 10_000 }) },
    )
  }),
)

it.live("dispatcher routes absent content-type through wrapBodyIdle", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => stalledBodyServer(10_000, undefined)),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          const error = yield* Effect.promise(() => firstStreamError(result))
          expect(error).toBeInstanceOf(ProviderError.ResponseStreamError)
          expect(String(error)).toContain("Body read timed out")
        }),
      { config: providerConfig(server.url, { bodyIdleTimeout: 100 }) },
    )
  }),
)

it.live("unconfigured (opt-in): stalling non-SSE body is NOT aborted by a short deadline", () =>
  Effect.gen(function* () {
    const server = yield* Effect.acquireRelease(
      Effect.promise(() => stalledBodyServer(10_000, "application/json")),
      (server) => Effect.sync(() => server.server.close()),
    )

    yield* provideTmpdirInstance(
      () =>
        Effect.gen(function* () {
          const provider = yield* Provider.Service
          const model = yield* provider.getModel(ProviderV2.ID.make("test"), ModelV2.ID.make("test-model"))
          const result = streamText({
            model: yield* provider.getLanguage(model),
            onError() {},
            messages: [{ role: "user", content: "hello" }],
          })

          // No bodyIdleTimeout / chunkTimeout configured: unwrapped. A 400ms
          // probe window must find no error part (the pre-fix silent hang shape).
          const error = yield* Effect.promise(() =>
            Promise.race([
              firstStreamError(result),
              new Promise((resolve) => setTimeout(() => resolve("PROBE_ELAPSED"), 400)),
            ]),
          )
          expect(error).toBe("PROBE_ELAPSED")
        }),
      { config: providerConfig(server.url, {}) },
    )
  }),
)

function providerConfig(url: string, options: Record<string, unknown> = {}) {
  const config = testProviderConfig(url)
  return {
    ...config,
    provider: {
      test: {
        ...config.provider.test,
        options: { ...config.provider.test.options, ...options },
      },
    },
  }
}

async function stalledBodyServer(stallMs: number, contentType: string | undefined): Promise<{ server: Server; url: string }> {
  const server = createServer((_, res) => {
    if (contentType !== undefined) {
      res.writeHead(200, { "content-type": contentType })
    } else {
      res.writeHead(200)
    }
    res.flushHeaders()
    // Never send a body; keep the socket open beyond the deadline
    setTimeout(() => {
      res.end()
    }, stallMs)
  })
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve))
  const address = server.address()
  if (!address || typeof address === "string") throw new Error("server did not bind to a TCP port")
  return { server, url: `http://127.0.0.1:${address.port}` }
}

// Sends an SSE-shaped body (so the AI SDK can parse it) under an arbitrary
// content-type, in `chunks` parts separated by `gapMs`. Used to prove the
// idle-progress deadline discriminates by gap size on the non-SSE branch.
async function chunkedBodyServer(
  contentType: string | undefined,
  chunks: number,
  gapMs: number,
): Promise<{ server: Server; url: string }> {
  const server = createServer((_, res) => {
    if (contentType !== undefined) {
      res.writeHead(200, { "content-type": contentType })
    } else {
      res.writeHead(200)
    }
    res.flushHeaders()
    for (let i = 0; i < chunks; i++) {
      setTimeout(() => {
        res.write('data: {"choices":[{"delta":{"content":"ok"}}]}\n\n')
        if (i === chunks - 1) {
          res.write("data: [DONE]\n\n")
          res.end()
        }
      }, (i + 1) * gapMs)
    }
  })
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve))
  const address = server.address()
  if (!address || typeof address === "string") throw new Error("server did not bind to a TCP port")
  return { server, url: `http://127.0.0.1:${address.port}` }
}
