/**
 * Stop-button state machine — two-primitive bounded machine.
 *
 * Primitives: State + Permitted Transition. No debounce/timing is smuggled into
 * the pure transition; timing (1s lastInterruptAt, 800ms isInterrupting cooldown,
 * 5s Esc window) stays in the effectful shell (prompt/index.tsx). If timing
 * proves load-bearing for correctness, the fallback is to increase primitive
 * count rather than layer states — see Verified Spec §4/§5 and operator
 * adjustment 2026-08-29 13:40.
 *
 * Pure, side-effect-free, I/O-free. The shell (TUI) interprets the transition
 * descriptor and performs sdk.client.v2.session.interrupt / dialog / toast / log.
 *
 * Conformance mapping (Universal Checklist):
 *  §5 State Model Completeness — STATES, EVENTS, TRANSITIONS, FORBIDDEN enumeration
 *  §6 State Conformance — per-state isPermitted/nextState entry-exit semantics
 *  §7 Transition Conformance — isPermitted/nextState as authoritative gate
 *  §8 Forbidden Transitions — FORBIDDEN set + barrier (absence from TRANSITIONS)
 */

export const STOP_BUTTON_STATES = ["idle", "running", "confirming", "interrupting"] as const

export type StopButtonState = (typeof STOP_BUTTON_STATES)[number]

export type StopButtonEvent =
  | "PROMPT_SUBMIT"
  | "STOP_CLICK"
  | "YES"
  | "NO"
  | "ESC"
  | "DISMISS"
  | "ESC_ESC"
  | "INTERRUPT_API"
  | "DONE"
  | "ERROR"
  | "SETTLED"

export const STOP_BUTTON_EVENTS: readonly StopButtonEvent[] = [
  "PROMPT_SUBMIT",
  "STOP_CLICK",
  "YES",
  "NO",
  "ESC",
  "DISMISS",
  "ESC_ESC",
  "INTERRUPT_API",
  "DONE",
  "ERROR",
  "SETTLED",
] as const

type TransitionKey = `${StopButtonState}:${StopButtonEvent}`

const TRANSITIONS: ReadonlyMap<TransitionKey, StopButtonState> = new Map<TransitionKey, StopButtonState>([
  // idle — §4.3 (initial state; terminal reachable via DONE/ERROR/SETTLED)
  ["idle:PROMPT_SUBMIT", "running"],
  ["idle:STOP_CLICK", "idle"],
  ["idle:INTERRUPT_API", "idle"],
  ["idle:ESC", "idle"],
  ["idle:ESC_ESC", "idle"],

  // running — §4.3
  ["running:STOP_CLICK", "confirming"],
  ["running:ESC_ESC", "interrupting"],
  ["running:DONE", "idle"],
  ["running:ERROR", "idle"],

  // confirming — §4.3 (YES → interrupting, No/Esc/Dismiss → running)
  ["confirming:YES", "interrupting"],
  ["confirming:NO", "running"],
  ["confirming:ESC", "running"],
  ["confirming:DISMISS", "running"],

  // interrupting — idempotent until SETTLED → idle (§4.3 + invariants I5/I6)
  ["interrupting:STOP_CLICK", "interrupting"],
  ["interrupting:INTERRUPT_API", "interrupting"],
  ["interrupting:SETTLED", "idle"],
])

/** Authoritative permitted transition table — read-only view for conformance audits (§7). */
export const STOP_BUTTON_TRANSITIONS: ReadonlyMap<TransitionKey, StopButtonState> = TRANSITIONS

/** Forbidden set is the complement of permitted over STATES×EVENTS (§8). */
export function forbiddenTransitions(): Array<[StopButtonState, StopButtonEvent]> {
  const out: Array<[StopButtonState, StopButtonEvent]> = []
  for (const s of STOP_BUTTON_STATES)
    for (const e of STOP_BUTTON_EVENTS) if (!TRANSITIONS.has(`${s}:${e}` as TransitionKey)) out.push([s, e])
  return out
}

export function nextState(state: StopButtonState, event: StopButtonEvent): StopButtonState | undefined {
  return TRANSITIONS.get(`${state}:${event}` as TransitionKey)
}

export function isPermitted(state: StopButtonState, event: StopButtonEvent): boolean {
  return TRANSITIONS.has(`${state}:${event}` as TransitionKey)
}
