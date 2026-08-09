export * as AISDK from "./aisdk"

import { makeLocationNode } from "./effect/app-node"
import type { LanguageModelV3 } from "@ai-sdk/provider"
import { Cause, Context, Effect, Layer, Schema, Scope } from "effect"
import { ModelV2 } from "./model"
import { ProviderV2 } from "./provider"
import { State } from "./state"

type SDK = any

export interface SDKEvent {
  readonly model: ModelV2.Info
  readonly package: string
  readonly options: Record<string, any>
  sdk?: SDK
}

export interface LanguageEvent {
  readonly model: ModelV2.Info
  readonly sdk: SDK
  readonly options: Record<string, any>
  language?: LanguageModelV3
}

function wrapSSE(res: Response, ms: number, ctl: AbortController) {
  if (typeof ms !== "number" || ms <= 0) return res
  if (!res.body) return res
  if (!res.headers.get("content-type")?.includes("text/event-stream")) return res

  const reader = res.body.getReader()
  const body = new ReadableStream<Uint8Array>({
    async pull(ctrl) {
      const part = await new Promise<Awaited<ReturnType<typeof reader.read>>>((resolve, reject) => {
        const id = setTimeout(() => {
          const err = new Error("SSE read timed out")
          ctl.abort(err)
          void reader.cancel(err)
          reject(err)
        }, ms)

        reader.read().then(
          (part) => {
            clearTimeout(id)
            resolve(part)
          },
          (err) => {
            clearTimeout(id)
            reject(err)
          },
        )
      })

      if (part.done) {
        ctrl.close()
        return
      }

      ctrl.enqueue(part.value)
    },
    async cancel(reason) {
      ctl.abort(reason)
      await reader.cancel(reason)
    },
  })

  return new Response(body, {
    headers: new Headers(res.headers),
    status: res.status,
    statusText: res.statusText,
  })
}

// NEW: idle-progress deadline for non-SSE response bodies (Option A').
// Mirrors the v1 provider.ts wrapBodyIdle but uses this file's plain-Error
// style (matching wrapSSE's `new Error("SSE read timed out")`).
function wrapBodyIdle(res: Response, ms: number, ctl: AbortController, absoluteMs?: number) {
  if (typeof ms !== "number" || ms <= 0) return res
  if (!res.body) return res
  const reader = res.body.getReader()
  let settled = false
  let streamCtl: ReadableStreamDefaultController<Uint8Array> | undefined
  let idleId: ReturnType<typeof setTimeout> | undefined
  let absoluteId: ReturnType<typeof setTimeout> | undefined

  const fail = (err: Error) => {
    if (settled) return
    settled = true
    if (idleId) clearTimeout(idleId)
    if (absoluteId) clearTimeout(absoluteId)
    ctl.abort(err)
    streamCtl?.error(err)
    void reader.cancel(err).catch(() => {})
  }

  const body = new ReadableStream<Uint8Array>({
    start(ctrl) {
      streamCtl = ctrl
    },
    async pull(ctrl) {
      if (settled) return
      const part = await new Promise<Awaited<ReturnType<typeof reader.read>>>((resolve, reject) => {
        idleId = setTimeout(() => {
          const err = new Error("Body read timed out")
          fail(err)
          reject(err)
        }, ms)
        reader.read().then(
          (part) => {
            if (idleId) clearTimeout(idleId)
            idleId = undefined
            resolve(part)
          },
          (err) => {
            if (idleId) clearTimeout(idleId)
            idleId = undefined
            reject(err)
          },
        )
      })
      if (settled) return
      if (part.done) {
        settled = true
        if (absoluteId) clearTimeout(absoluteId)
        ctrl.close()
        return
      }
      ctrl.enqueue(part.value)
    },
    async cancel(reason) {
      fail(reason instanceof Error ? reason : new Error(String(reason)))
    },
  })

  if (typeof absoluteMs === "number" && absoluteMs > 0) {
    absoluteId = setTimeout(() => {
      fail(new Error("Body read deadline exceeded"))
    }, absoluteMs)
  }

  const headers = new Headers(res.headers)
  headers.delete("content-length")
  headers.delete("content-encoding")
  return new Response(body, {
    headers,
    status: res.status,
    statusText: res.statusText,
  })
}

function prepareOptions(model: ModelV2.Info, pkg: string) {
  const options: Record<string, any> = {
    name: model.providerID,
    ...(model.api.type === "aisdk" ? (model.api.settings ?? {}) : {}),
    ...model.request.body,
  }
  if (model.api.type === "aisdk" && model.api.url) options.baseURL = model.api.url

  const customFetch = options.fetch
  const chunkTimeout = options.chunkTimeout
  const bodyIdleTimeout = options.bodyIdleTimeout
  const bodyAbsoluteTimeout = options.bodyAbsoluteTimeout
  delete options.chunkTimeout
  delete options.bodyIdleTimeout
  delete options.bodyAbsoluteTimeout
  options.fetch = async (input: Parameters<typeof fetch>[0], init?: RequestInit) => {
    const opts = { ...(init ?? {}) }
    const chunkAbortCtl = typeof chunkTimeout === "number" && chunkTimeout > 0 ? new AbortController() : undefined
    const bodyIdleAbortCtl =
      typeof bodyIdleTimeout === "number" && bodyIdleTimeout > 0 ? new AbortController() : undefined
    const abortSignals = [
      opts.signal,
      chunkAbortCtl ? chunkAbortCtl.signal : undefined,
      bodyIdleAbortCtl ? bodyIdleAbortCtl.signal : undefined,
      options.timeout !== undefined && options.timeout !== null && options.timeout !== false
        ? AbortSignal.timeout(options.timeout)
        : undefined,
    ].filter((item): item is AbortSignal => Boolean(item))
    if (abortSignals.length === 1) opts.signal = abortSignals[0]
    if (abortSignals.length > 1) opts.signal = AbortSignal.any(abortSignals)

    if (
      (pkg === "@ai-sdk/openai" || pkg === "@ai-sdk/azure" || pkg === "@ai-sdk/amazon-bedrock/mantle") &&
      opts.body &&
      opts.method === "POST"
    ) {
      const body = JSON.parse(opts.body as string)
      if (body.store !== true && Array.isArray(body.input)) {
        for (const item of body.input) {
          if ("id" in item) delete item.id
        }
        opts.body = JSON.stringify(body)
      }
    }

    const res = await (typeof customFetch === "function" ? customFetch : fetch)(input, {
      ...opts,
      timeout: false,
    })
    const isSSE = res.headers.get("content-type")?.includes("text/event-stream")
    if (isSSE) {
      if (!chunkAbortCtl || typeof chunkTimeout !== "number") return res
      return wrapSSE(res, chunkTimeout, chunkAbortCtl)
    }
    if (!bodyIdleAbortCtl || typeof bodyIdleTimeout !== "number") return res
    return wrapBodyIdle(res, bodyIdleTimeout, bodyIdleAbortCtl, bodyAbsoluteTimeout)
  }

  return options
}

export class InitError extends Schema.TaggedErrorClass<InitError>()("AISDK.InitError", {
  providerID: ProviderV2.ID,
  cause: Schema.Defect(),
}) {}

function initError(providerID: ProviderV2.ID) {
  return Effect.catchCause((cause) => Effect.fail(new InitError({ providerID, cause: Cause.squash(cause) })))
}

export interface Interface {
  readonly hook: {
    readonly sdk: (
      callback: (event: SDKEvent) => Effect.Effect<void> | void,
    ) => Effect.Effect<State.Registration, never, Scope.Scope>
    readonly language: (
      callback: (event: LanguageEvent) => Effect.Effect<void> | void,
    ) => Effect.Effect<State.Registration, never, Scope.Scope>
  }
  readonly runSDK: (event: SDKEvent) => Effect.Effect<SDKEvent>
  readonly runLanguage: (event: LanguageEvent) => Effect.Effect<LanguageEvent>
  readonly language: (model: ModelV2.Info) => Effect.Effect<LanguageModelV3, InitError>
}

export class Service extends Context.Service<Service, Interface>()("@opencode/v2/AISDK") {}

export const locationLayer = Layer.effect(
  Service,
  Effect.gen(function* () {
    let sdkHooks: ((event: SDKEvent) => Effect.Effect<void> | void)[] = []
    let languageHooks: ((event: LanguageEvent) => Effect.Effect<void> | void)[] = []
    const languages = new Map<string, LanguageModelV3>()
    const sdks = new Map<string, SDK>()

    const register = <Event>(
      hooks: () => ((event: Event) => Effect.Effect<void> | void)[],
      update: (hooks: ((event: Event) => Effect.Effect<void> | void)[]) => void,
    ) =>
      Effect.fn("AISDK.hook")(function* (callback: (event: Event) => Effect.Effect<void> | void) {
        const scope = yield* Scope.Scope
        let active = true
        update([...hooks(), callback])
        const dispose = Effect.sync(() => {
          if (!active) return
          active = false
          update(hooks().filter((item) => item !== callback))
        })
        yield* Scope.addFinalizer(scope, dispose)
        return { dispose }
      })

    const run = Effect.fnUntraced(function* <Event>(
      hooks: readonly ((event: Event) => Effect.Effect<void> | void)[],
      event: Event,
    ) {
      for (const hook of hooks) {
        const result = hook(event)
        if (Effect.isEffect(result)) yield* result
      }
      return event
    })

    const service = Service.of({
      hook: {
        sdk: register(
          () => sdkHooks,
          (next) => (sdkHooks = next),
        ),
        language: register(
          () => languageHooks,
          (next) => (languageHooks = next),
        ),
      },
      runSDK: (event) => run(sdkHooks, event),
      runLanguage: (event) => run(languageHooks, event),
      language: Effect.fn("AISDK.language")(function* (model) {
        const key = `${model.providerID}/${model.id}/${model.request.variant ?? "default"}`
        const existing = languages.get(key)
        if (existing) return existing
        if (model.api.type !== "aisdk")
          return yield* new InitError({
            providerID: model.providerID,
            cause: new Error(`Unsupported api ${model.api.type}`),
          })

        const options = prepareOptions(model, model.api.package)
        const sdkKey = JSON.stringify({
          providerID: model.providerID,
          api: model.api,
          options,
        })
        const sdk =
          sdks.get(sdkKey) ??
          (yield* service.runSDK({ model, package: model.api.package, options }).pipe(initError(model.providerID))).sdk
        if (!sdk)
          return yield* new InitError({
            providerID: model.providerID,
            cause: new Error("No AISDK provider plugin returned an SDK"),
          })
        sdks.set(sdkKey, sdk)
        const result = yield* service.runLanguage({ model, sdk, options }).pipe(initError(model.providerID))
        const language = yield* Effect.sync(() => result.language ?? sdk.languageModel(model.api.id)).pipe(
          initError(model.providerID),
        )
        languages.set(key, language)
        return language
      }),
    })
    return service
  }),
)

export const node = makeLocationNode({ service: Service, layer: locationLayer, deps: [] })
