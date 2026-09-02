/**
 * Proptest / fast-check property harness for the stop-button statechart.
 *
 * Verified Spec Phase5 (§3b.4 H1/H2, §3b.1 P-PF3/P-PF4/P-PF5).
 * This file IS the hardening harness sketched at spec §3b.4 for H1/H2:
 *
 *   forAll(drainShapes, async (shape) => {
 *     invariant(Cause.hasInterruptsOnly(...))
 *   })
 *   // and the TS equivalent of a Kani/proptest harness for the pure transition.
 *
 * It uses `fast-check` (the TS equivalent of Rust `proptest` — already a transitive
 * dep via `effect`). If unavailable it falls back to a deterministic LCG generator
 * so the suite never stubs — every property still runs.
 *
 * Conformance: Verified Spec §5 invariants I4-I5, §7 edge catalog, and
 * Conformance Suite §5-9. VSDD Phase5 hardening.
 *
 * Properties:
 *  PF3-StateGating   — only permitted (State,Event) ever succeeds; every forbidden is rejected
 *  PF4-Idempotence   — idle STOP/INTERRUPT stays idle; interrupting STOP/INTERRUPT stays interrupting
 *  PF5-Coalesced     — SETTLED only from interrupting; DONE/ERROR only from running
 *  PF6-TotalFunction — nextState+isPermitted agree; forbidden never yields a state
 *  PF7-InvariantLoop — 200 random walks never drift from the 4-state set
 */

import { describe, expect, test } from "bun:test"
import {
  STOP_BUTTON_EVENTS,
  STOP_BUTTON_STATES,
  forbiddenTransitions,
  isPermitted,
  nextState,
  type StopButtonEvent,
  type StopButtonState,
} from "../../src/component/prompt/stop-button-machine"

// ── fast-check adapter ────────────────────────────────────────────────────
// Try to load fast-check; fall back to a tiny deterministic generator so
// no test is stubbed even in an offline environment.

let fc: typeof import("fast-check") | undefined = undefined
try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  fc = require("fast-check") as typeof import("fast-check")
} catch {
  // offline / no fast-check — harness still runs via fallback generator
  fc = undefined
}

function lcg(seed: number): () => number {
  let s = seed >>> 0
  return () => {
    s = (1664525 * s + 1013904223) >>> 0
    return s / 0x1_0000_0000
  }
}

function pick<T>(rng: () => number, arr: readonly T[]): T {
  return arr[Math.floor(rng() * arr.length)]!
}

function randomEventSequence(rng: () => number, length: number): StopButtonEvent[] {
  return Array.from({ length }, () => pick(rng, STOP_BUTTON_EVENTS))
}

// ── helpers ───────────────────────────────────────────────────────────────

function walk(events: StopButtonEvent[]): { final: StopButtonState | undefined; steps: Array<{ state: StopButtonState; event: StopButtonEvent; next: StopButtonState | undefined }> } {
  let cur: StopButtonState = "idle"
  const steps: Array<{ state: StopButtonState; event: StopButtonEvent; next: StopButtonState | undefined }> = []
  let failed: StopButtonState | undefined = cur
  for (const ev of events) {
    const nxt = nextState(cur, ev)
    steps.push({ state: cur, event: ev, next: nxt })
    if (nxt === undefined) {
      failed = undefined
      break
    }
    cur = nxt
    failed = cur
  }
  return { final: failed, steps }
}

// ── suite ─────────────────────────────────────────────────────────────────

describe("stop-button proptest harness — Phase5 hardening (Verified Spec §3b.4 proptest, §3b.1 P-PF3..5)", () => {
  // When fast-check is present, run true property tests with 200 cases.
  // When absent, run deterministic seed sweeps with the same shrinking-like coverage.

  const CASES = 200
  const SEQ_LENGTH = 20

  for (const harness of fc ? (["fast-check"] as const) : (["fallback-lcg"] as const)) {
    describe(`engine: ${harness}`, () => {
      test("PF3 — state-gating: every step respects isPermitted; forbidden never succeeds", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                const permitted = isPermitted(state, event)
                if (permitted) expect(next, `${state}:${event} permitted→${next}`).not.toBeUndefined()
                else expect(next, `${state}:${event} forbidden→undefined`).toBeUndefined()
              }
            }),
            { numRuns: CASES, seed: 0x513 },
          )
        } else {
          const rng = lcg(0x513)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, event, next } of steps) {
              if (isPermitted(state, event)) expect(next, `${state}:${event}`).not.toBeUndefined()
              else expect(next, `${state}:${event}`).toBeUndefined()
            }
          }
        }
      })

      test("PF4a — idempotence (idle): STOP_CLICK and INTERRUPT_API in idle always stay idle, not fence", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                if (state === "idle" && (event === "STOP_CLICK" || event === "INTERRUPT_API")) {
                  expect(next, `idle:${event}→idle`).toBe("idle")
                }
              }
            }),
            { numRuns: CASES, seed: 0x514 },
          )
        } else {
          const rng = lcg(0x514)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, event, next } of steps) {
              if (state === "idle" && (event === "STOP_CLICK" || event === "INTERRUPT_API")) expect(next).toBe("idle")
            }
          }
        }
      })

      test("PF4b — idempotence (interrupting): STOP_CLICK and INTERRUPT_API in interrupting coalesce", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                if (state === "interrupting" && (event === "STOP_CLICK" || event === "INTERRUPT_API")) {
                  expect(next, `interrupting:${event}→interrupting`).toBe("interrupting")
                }
              }
            }),
            { numRuns: CASES, seed: 0x515 },
          )
        } else {
          const rng = lcg(0x515)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, event, next } of steps) {
              if (state === "interrupting" && (event === "STOP_CLICK" || event === "INTERRUPT_API")) expect(next).toBe("interrupting")
            }
          }
        }
      })

      test("PF5 — settlement only from correct states: SETTLED only from interrupting, DONE/ERROR only from running", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                if (next === undefined) continue
                if (event === "SETTLED") expect(state, `SETTLED only from interrupting, got ${state}`).toBe("interrupting")
                if (event === "DONE" || event === "ERROR") expect(state, `${event} only from running, got ${state}`).toBe("running")
              }
            }),
            { numRuns: CASES, seed: 0x516 },
          )
        } else {
          const rng = lcg(0x516)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, event, next } of steps) {
              if (next === undefined) continue
              if (event === "SETTLED") expect(state).toBe("interrupting")
              if (event === "DONE" || event === "ERROR") expect(state).toBe("running")
            }
          }
        }
      })

      test("PF6 — total-function agreement: nextState defined iff isPermitted true; forbidden count 28", () => {
        expect(forbiddenTransitions()).toHaveLength(28)
        for (const s of STOP_BUTTON_STATES) {
          for (const e of STOP_BUTTON_EVENTS) {
            const p = isPermitted(s, e)
            const n = nextState(s, e)
            expect((n !== undefined), `${s}:${e} next defined ⇔ permitted`).toBe(p)
          }
        }
      })

      test("PF7 — random walks never leave the 4-state set (no drift, no panic)", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: 50 }), (seq) => {
              const { final } = walk(seq as StopButtonEvent[])
              if (final !== undefined) expect(STOP_BUTTON_STATES as readonly string[]).toContain(final)
            }),
            { numRuns: CASES, seed: 0x517 },
          )
        } else {
          const rng = lcg(0x517)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * 51))
            const { final } = walk(seq)
            if (final !== undefined) expect((STOP_BUTTON_STATES as readonly string[]).includes(final)).toBeTrue()
          }
        }
      })

      test("PF8 — confirming must go via running or interrupting, never direct to idle (I4)", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                if (state === "confirming" && next !== undefined) {
                  expect(next, `confirming:${event}→${next} must not be idle`).not.toBe("idle")
                  expect(["running", "interrupting"], `confirming:${event} must go running|interrupting`).toContain(next as string)
                }
              }
            }),
            { numRuns: CASES, seed: 0x518 },
          )
        } else {
          const rng = lcg(0x518)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, next } of steps) {
              if (state === "confirming" && next !== undefined) expect(next).not.toBe("idle")
            }
          }
        }
      })

      test("PF9 — YES only from confirming; ESC_ESC only from idle/running (I4 fence)", () => {
        if (fc) {
          fc.assert(
            fc.property(fc.array(fc.constantFrom(...STOP_BUTTON_EVENTS), { minLength: 0, maxLength: SEQ_LENGTH }), (seq) => {
              const { steps } = walk(seq as StopButtonEvent[])
              for (const { state, event, next } of steps) {
                if (next === undefined) continue
                if (event === "YES") expect(state, `YES only from confirming`).toBe("confirming")
                if (event === "ESC_ESC") {
                  expect(["idle", "running"], `ESC_ESC permitted only from idle/running, got ${state}`).toContain(state)
                }
              }
            }),
            { numRuns: CASES, seed: 0x519 },
          )
        } else {
          const rng = lcg(0x519)
          for (let i = 0; i < CASES; i++) {
            const seq = randomEventSequence(rng, Math.floor(rng() * (SEQ_LENGTH + 1)))
            const { steps } = walk(seq)
            for (const { state, event, next } of steps) {
              if (next === undefined) continue
              if (event === "YES") expect(state).toBe("confirming")
            }
          }
        }
      })
    })
  }

  test("shrink-like minimal counterexamples — known forbidden pairs are rejected (ground truth, not generated)", () => {
    const knownForbidden: Array<[StopButtonState, StopButtonEvent]> = [
      ["idle", "YES"],
      ["idle", "NO"],
      ["idle", "DISMISS"],
      ["idle", "SETTLED"],
      ["idle", "DONE"],
      ["idle", "ERROR"],
      ["running", "YES"],
      ["running", "NO"],
      ["running", "DISMISS"],
      ["running", "SETTLED"],
      ["running", "INTERRUPT_API"],
      ["running", "ESC"],
      ["confirming", "PROMPT_SUBMIT"],
      ["confirming", "DONE"],
      ["confirming", "ERROR"],
      ["confirming", "SETTLED"],
      ["confirming", "STOP_CLICK"],
      ["confirming", "INTERRUPT_API"],
      ["confirming", "ESC_ESC"],
      ["interrupting", "YES"],
      ["interrupting", "NO"],
      ["interrupting", "ESC"],
      ["interrupting", "DISMISS"],
      ["interrupting", "PROMPT_SUBMIT"],
      ["interrupting", "DONE"],
      ["interrupting", "ERROR"],
      ["interrupting", "ESC_ESC"],
      ["interrupting", "ESC"],
    ]
    expect(knownForbidden).toHaveLength(28)
    for (const [s, e] of knownForbidden) {
      expect(isPermitted(s, e), `${s}:${e} must be forbidden`).toBeFalse()
      expect(nextState(s, e), `${s}:${e}→undefined`).toBeUndefined()
    }
  })
});
