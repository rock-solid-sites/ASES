/**
 * Stop-button shell controller — the effectful interpreter for the pure
 * stop-button-machine descriptor.
 *
 * Owns the full stop flow for BOTH user-facing enforcement sites:
 *   - handleStopClick      — ■ Stop button (running → confirming → YES → fence)
 *   - handleEscapeInterrupt — double-ESC bypass (running → ESC_ESC → fence)
 *
 * The machine (stop-button-machine.ts) stays pure and I/O-free; this module is
 * the only place that turns a machine transition into sdk.client.v2.session
 * calls, dialog, toast and log effects. Timing (debounce/cooldown/settle) stays
 * in the shell per Verified Spec §3b.2 — it is injected so tests can drive it
 * deterministically.
 *
 * Review-fix provenance (issue #510, Hy3 review 2026-08-30):
 *   - D1: this extraction makes the real gate code mountable in tests — a
 *     mutant that fires the interrupt unconditionally (gate removed) fails
 *     stop-button-controller.test.ts.
 *   - B1: authoritativeState() reconciles a lagged TUI-local idle projection
 *     against the coordinator active map (GET /api/session/active) before
 *     denying an explicit stop request, so a live fiber is always reachable.
 *   - B3: after a 204, the settle check re-reads the active map and warns when
 *     the session is still active — placebo (204-but-fiber-alive) becomes
 *     visible in the UI instead of being detectable only by the live probe.
 *
 * Conformance mapping (Universal Checklist): §7 Transition Conformance
 * (isPermitted/nextState gate every dispatch), §15 Temporal (debounce at the
 * fence, cooldown, bounded settle reconciliation), §16 Transport (204 is
 * acceptance, not completion — the settle check separates them).
 */

import { isPermitted, nextState } from "./stop-button-machine"
import type { StopButtonState } from "./stop-button-machine"
import { errorMessage } from "../../util/error"

/** 1s minimum between interrupt requests (spec §6 timing; shell-owned). */
export const STOP_BUTTON_DEBOUNCE_MS = 1000
/** 800ms isInterrupting cooldown after a dispatch (spec §6 timing; shell-owned). */
export const STOP_BUTTON_COOLDOWN_MS = 800
/** Settle window before the post-interrupt placebo check (cooldown + drain-settle buffer). */
export const STOP_BUTTON_SETTLE_MS = STOP_BUTTON_COOLDOWN_MS + 400

export type StopToastVariant = "info" | "success" | "warning" | "error"

export type StopControllerDeps = {
  /** Session the button acts on (may be undefined before a session exists). */
  sessionID(): string | undefined
  /** TUI-local projection (deriveStopState) — may lag the coordinator. */
  readState(): StopButtonState
  /**
   * Authoritative coordinator probe: is a drain live for this session?
   * Backed by GET /api/session/active (the active-map HTTP projection).
   */
  isActive(sessionID: string): Promise<boolean>
  isInterrupting(): boolean
  setInterrupting(value: boolean): void
  isConfirming(): boolean
  setConfirming(value: boolean): void
  /** Open the confirm dialog; resolves true (Yes) / false (No, Esc, dismiss). */
  confirm(): Promise<boolean>
  /** The fence: sdk.client.v2.session.interrupt (204 acceptance, idle no-op). */
  interrupt(sessionID: string): Promise<unknown>
  /** Last user message ID — baseline for the placebo false-positive guard. */
  latestMessageID(): string | undefined
  toast(variant: StopToastVariant, message: string, duration: number): void
  log(line: string): void
  now(): number
  debounceMs?: number
  cooldownMs?: number
  settleMs?: number
}

export function createStopController(deps: StopControllerDeps) {
  const debounceMs = deps.debounceMs ?? STOP_BUTTON_DEBOUNCE_MS
  const cooldownMs = deps.cooldownMs ?? STOP_BUTTON_COOLDOWN_MS
  const settleMs = deps.settleMs ?? STOP_BUTTON_SETTLE_MS
  let lastInterruptAt = 0

  const ts = () => new Date(deps.now()).toISOString()

  /**
   * B1: the SSE status projection can lag the coordinator (fiber live,
   * projection still "idle"). Before denying an explicit stop request on an
   * "idle" projection, reconcile once against the authoritative active map.
   * A single round-trip is paid only in the ambiguous case; any other state is
   * returned untouched. If the authoritative source is unreachable, the local
   * projection stands (never block the UI on a request that may never resolve).
   */
  async function authoritativeState(): Promise<StopButtonState> {
    const cur = deps.readState()
    const sessionID = deps.sessionID()
    if (cur !== "idle" || !sessionID) return cur
    try {
      if (await deps.isActive(sessionID)) {
        deps.log(`${ts()} stop-button authoritative override idle->running session=${sessionID}`)
        return "running"
      }
    } catch {
      deps.log(`${ts()} stop-button authoritative check unavailable session=${sessionID} (local projection stands)`)
    }
    return cur
  }

  /**
   * B3: a 204 is acceptance, not completion. After the settle window, re-read
   * the authoritative active map; a still-active session with no new user
   * message since the interrupt is a placebo suspect (204-but-fiber-alive) and
   * is surfaced to the user instead of being silently swallowed.
   */
  function scheduleSettleCheck(sessionID: string, baselineMessageID: string | undefined, source: string) {
    setTimeout(() => {
      void (async () => {
        try {
          if (!(await deps.isActive(sessionID))) {
            deps.log(`${ts()} stop-button settle verified session=${sessionID} source=${source}`)
            return
          }
          if (deps.latestMessageID() !== baselineMessageID) return
          deps.log(
            `${ts()} stop-button PLACEBO SUSPECT session=${sessionID} source=${source} still active ${settleMs}ms after 204`,
          )
          deps.toast("warning", "Session still active after interrupt", 3000)
        } catch {
          deps.log(`${ts()} stop-button settle check unavailable session=${sessionID} source=${source}`)
        }
      })()
    }, settleMs)
  }

  /**
   * Shared fence dispatch: cooldown/idempotence guard, 1s debounce, interrupt
   * call, feedback, cooldown reset, settle check. Returns true iff dispatched.
   */
  async function requestInterrupt(source: string, opts: { announce: boolean }): Promise<boolean> {
    const sessionID = deps.sessionID()
    if (!sessionID) return false
    if (deps.isInterrupting()) {
      deps.log(`${ts()} stop-button ${source} debounced interrupting session=${sessionID}`)
      return false
    }
    const now = deps.now()
    if (now - lastInterruptAt < debounceMs) {
      deps.log(`${ts()} stop-button ${source} debounced 1s session=${sessionID}`)
      return false
    }
    lastInterruptAt = now
    deps.setInterrupting(true)
    const baselineMessageID = deps.latestMessageID()
    deps.log(`${ts()} stop-button interrupt request source=${source} session=${sessionID}`)
    try {
      await deps.interrupt(sessionID)
      deps.log(`${ts()} stop-button interrupt success source=${source} session=${sessionID}`)
      if (opts.announce) deps.toast("success", "Interrupted", 2000)
    } catch (e) {
      deps.log(`${ts()} stop-button interrupt error source=${source} session=${sessionID} error=${String(e)}`)
      if (opts.announce) deps.toast("error", errorMessage(e), 3000)
    } finally {
      setTimeout(() => deps.setInterrupting(false), cooldownMs)
      scheduleSettleCheck(sessionID, baselineMessageID, source)
    }
    return true
  }

  /** ■ Stop button flow — machine-gated at every step. */
  async function handleStopClick(): Promise<void> {
    const sessionID = deps.sessionID()
    if (!sessionID) {
      // No session is idle-equivalent for the machine.
      deps.log(`${ts()} stop-button no sessionID machine=${deps.readState()}`)
      deps.toast("info", "No active run", 2000)
      return
    }

    const cur = await authoritativeState()

    // Gate via pure machine — cheapest discriminating check before any effect.
    if (!isPermitted(cur, "STOP_CLICK")) {
      deps.log(`${ts()} stop-button STOP_CLICK forbidden cur=${cur} session=${sessionID}`)
      return
    }
    const next = nextState(cur, "STOP_CLICK")
    // idle STOP_CLICK is the typed 204 no-op (stays idle); interrupting
    // STOP_CLICK is idempotent debounce.
    if (next === "idle") {
      deps.toast("info", "No active run", 2000)
      deps.log(`${ts()} stop-button no active run session=${sessionID} machine=${cur}->idle`)
      return
    }
    if (next === "interrupting") {
      if (deps.isInterrupting()) return
      if (deps.now() - lastInterruptAt < debounceMs) return
      deps.log(`${ts()} stop-button STOP_CLICK debounced cur=${cur} session=${sessionID}`)
      return
    }
    // next must be "confirming" (running -> confirming) to reach dialog.
    if (next !== "confirming") return
    // Do NOT gate dialog open on lastInterruptAt — that orphans debounce after
    // cancel (No). Debounce is enforced at the fence (YES -> interrupting).
    deps.setConfirming(true)
    let confirmed: boolean
    try {
      confirmed = await deps.confirm()
    } finally {
      deps.setConfirming(false)
    }
    deps.log(`${ts()} stop-button dialog confirmed=${confirmed} session=${sessionID} machine=confirming`)
    // Shell interprets confirming -> YES/NO via pure machine.
    const dialogEvent = confirmed ? ("YES" as const) : ("NO" as const)
    if (!isPermitted("confirming", dialogEvent)) {
      deps.log(`${ts()} stop-button dialog event forbidden event=${dialogEvent} session=${sessionID}`)
      return
    }
    const afterDialog = nextState("confirming", dialogEvent)
    if (afterDialog === "running") {
      deps.log(`${ts()} stop-button cancelled session=${sessionID} machine=confirming->running`)
      return
    }
    if (afterDialog !== "interrupting") return
    // confirming --YES--> interrupting: fence invoked.
    await requestInterrupt("YES", { announce: true })
  }

  /**
   * Double-ESC bypass flow — machine-gated (running --ESC_ESC--> interrupting,
   * idle ESC_ESC stays idle) with the same B1 reconciliation as the button.
   */
  async function handleEscapeInterrupt(): Promise<void> {
    const cur = await authoritativeState()
    if (!isPermitted(cur, "ESC_ESC")) {
      deps.log(`${ts()} stop-button ESC_ESC forbidden cur=${cur} session=${deps.sessionID()}`)
      return
    }
    const next = nextState(cur, "ESC_ESC")
    if (next === "idle") {
      deps.log(`${ts()} stop-button ESC_ESC idle no-op session=${deps.sessionID()}`)
      return
    }
    if (next !== "interrupting") return
    if (deps.isConfirming()) deps.setConfirming(false)
    await requestInterrupt("ESC_ESC", { announce: false })
  }

  return { handleStopClick, handleEscapeInterrupt }
}
