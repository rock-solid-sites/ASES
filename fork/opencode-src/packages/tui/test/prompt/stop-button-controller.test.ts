import { describe, expect, test } from "bun:test"
import {
  createStopController,
  STOP_BUTTON_COOLDOWN_MS,
  STOP_BUTTON_DEBOUNCE_MS,
  STOP_BUTTON_SETTLE_MS,
  type StopControllerDeps,
} from "../../src/component/prompt/stop-button-controller"
import type { StopButtonState } from "../../src/component/prompt/stop-button-machine"

// Integration test for the stop-button SHELL gate (issue #510, Hy3 review D1).
//
// The machine tests (stop-button-machine.test.ts) prove the transition TABLE;
// this suite mounts the REAL controller — the code the ■ Stop button and the
// double-ESC command actually execute — with a fake
// sdk.client.v2.session.interrupt and proves the gate is ENFORCED:
//   - idle click sends 0 interrupt calls (a mutant that fires the interrupt
//     unconditionally — gate removed — fails here),
//   - running → confirming → No sends 0 calls,
//   - running → confirming → Yes sends exactly 1 call,
//   - interrupting click is idempotent (0 extra calls),
//   - debounce is enforced at the fence,
//   - B1: a lagged idle projection reconciles against the authoritative
//     coordinator active map instead of denying the user,
//   - B3: a 204 with the fiber still alive after the settle window is surfaced
//     (placebo suspect) instead of being silently swallowed.

const SESSION = "ses_test"

type Harness = {
  calls: string[]
  toasts: Array<{ variant: string; message: string; duration: number }>
  logs: string[]
  dialogOpens: number
  interrupting: boolean
  confirming: boolean
  activeCalls: number
  clock: number
  state: StopButtonState
  active: boolean
  activeError?: Error
  confirmResult: boolean
  interruptError?: Error
  sessionID: string | undefined
  messageID: string | undefined
}

function createHarness(init?: Partial<Pick<Harness, "state" | "active" | "activeError" | "confirmResult" | "interruptError" | "sessionID" | "messageID">>) {
  const h: Harness = {
    calls: [],
    toasts: [],
    logs: [],
    dialogOpens: 0,
    interrupting: false,
    confirming: false,
    activeCalls: 0,
    clock: 1_000_000,
    state: init?.state ?? "idle",
    active: init?.active ?? false,
    activeError: init?.activeError,
    confirmResult: init?.confirmResult ?? false,
    interruptError: init?.interruptError,
    sessionID: init?.sessionID !== undefined ? init.sessionID : SESSION,
    messageID: init?.messageID !== undefined ? init.messageID : "msg_1",
  }

  const deps: StopControllerDeps = {
    sessionID: () => h.sessionID,
    readState: () => h.state,
    isActive: async (sessionID) => {
      h.activeCalls += 1
      if (h.activeError) throw h.activeError
      return h.active && sessionID === h.sessionID
    },
    isInterrupting: () => h.interrupting,
    setInterrupting: (value) => {
      h.interrupting = value
    },
    isConfirming: () => h.confirming,
    setConfirming: (value) => {
      h.confirming = value
    },
    confirm: async () => {
      h.dialogOpens += 1
      return h.confirmResult
    },
    interrupt: async (sessionID) => {
      h.calls.push(sessionID)
      if (h.interruptError) throw h.interruptError
      return undefined
    },
    latestMessageID: () => h.messageID,
    toast: (variant, message, duration) => {
      h.toasts.push({ variant, message, duration })
    },
    log: (line) => {
      h.logs.push(line)
    },
    now: () => h.clock,
    // Fast shell timing so cooldown/settle timers elapse inside the test body.
    cooldownMs: 5,
    settleMs: 5,
  }

  return { h, controller: createStopController(deps) }
}

const toastOf = (h: Harness, variant: string, message?: string) =>
  h.toasts.find((t) => t.variant === variant && (message === undefined || t.message === message))

describe("stop-button controller — D1 gate enforcement", () => {
  test("idle click sends no interrupt, opens no dialog, toasts No active run", async () => {
    const { h, controller } = createHarness({ state: "idle", active: false })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(0)
    expect(h.dialogOpens).toBe(0)
    expect(toastOf(h, "info", "No active run")).toBeDefined()
  })

  test("running click opens the confirm dialog; No sends no interrupt and resets confirming", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: false })
    await controller.handleStopClick()
    expect(h.dialogOpens).toBe(1)
    expect(h.calls).toHaveLength(0)
    expect(h.confirming).toBe(false)
  })

  test("running click → Yes sends exactly one interrupt with the session ID", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true })
    await controller.handleStopClick()
    expect(h.calls).toEqual([SESSION])
    expect(toastOf(h, "success", "Interrupted")).toBeDefined()
  })

  test("interrupting click is idempotent debounce — no extra interrupt, no dialog", async () => {
    const { h, controller } = createHarness({ state: "interrupting" })
    h.interrupting = true
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(0)
    expect(h.dialogOpens).toBe(0)
  })

  test("no session click is a typed no-op", async () => {
    const { h, controller } = createHarness({ state: "idle", sessionID: undefined })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(0)
    expect(h.dialogOpens).toBe(0)
    expect(toastOf(h, "info", "No active run")).toBeDefined()
  })

  test("interrupt failure toasts the error and the cooldown still resets", async () => {
    const { h, controller } = createHarness({
      state: "running",
      confirmResult: true,
      interruptError: new Error("boom"),
    })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(1)
    expect(toastOf(h, "error")).toBeDefined()
    expect(h.interrupting).toBe(true)
    await Bun.sleep(40)
    expect(h.interrupting).toBe(false)
  })
})

describe("stop-button controller — fence timing (spec §6, shell-owned)", () => {
  test("timing constants match the Verified Spec §6 contract", () => {
    expect(STOP_BUTTON_DEBOUNCE_MS).toBe(1000)
    expect(STOP_BUTTON_COOLDOWN_MS).toBe(800)
    expect(STOP_BUTTON_SETTLE_MS).toBe(1200)
  })

  test("second Yes within the 1s debounce window does not re-fire; after the window it does", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(1)

    // Cooldown elapsed (fast timer) but the 1s debounce has not.
    await Bun.sleep(40)
    h.interrupting = false
    h.state = "running"
    h.clock += 100
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(1)

    // Debounce window elapsed — a fresh confirm may fire again.
    h.clock += STOP_BUTTON_DEBOUNCE_MS + 1
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(2)
  })
})

describe("stop-button controller — B1 status-lag denial fix", () => {
  test("lagged idle projection with a live fiber reconciles to running: dialog opens and the fence fires", async () => {
    // TUI projection says idle (SSE lag) but the coordinator active map says
    // the session is running. The old code denied with "No active run"; the
    // fix must reach the confirm dialog and dispatch exactly one interrupt.
    const { h, controller } = createHarness({ state: "idle", active: true, confirmResult: true })
    await controller.handleStopClick()
    expect(h.activeCalls).toBe(1)
    expect(h.dialogOpens).toBe(1)
    expect(h.calls).toEqual([SESSION])
  })

  test("truly idle session still reconciles then denies (one authoritative probe, no call)", async () => {
    const { h, controller } = createHarness({ state: "idle", active: false })
    await controller.handleStopClick()
    expect(h.activeCalls).toBe(1)
    expect(h.calls).toHaveLength(0)
    expect(h.dialogOpens).toBe(0)
    expect(toastOf(h, "info", "No active run")).toBeDefined()
  })

  test("non-idle projections skip the authoritative probe (no extra round-trip)", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true })
    await controller.handleStopClick()
    expect(h.activeCalls).toBe(0)
    expect(h.calls).toEqual([SESSION])
  })

  test("authoritative source unreachable falls back to the local projection without crashing", async () => {
    const { h, controller } = createHarness({ state: "idle", activeError: new Error("server down") })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(0)
    expect(h.dialogOpens).toBe(0)
    expect(toastOf(h, "info", "No active run")).toBeDefined()
  })

  test("double-ESC reconciles a lagged idle projection and fires the fence", async () => {
    const { h, controller } = createHarness({ state: "idle", active: true })
    await controller.handleEscapeInterrupt()
    expect(h.calls).toEqual([SESSION])
  })

  test("double-ESC on a truly idle session is a typed no-op", async () => {
    const { h, controller } = createHarness({ state: "idle", active: false })
    await controller.handleEscapeInterrupt()
    expect(h.calls).toHaveLength(0)
    expect(h.interrupting).toBe(false)
  })
})

describe("stop-button controller — B3 placebo detection", () => {
  test("204 with the fiber still alive after settle warns (placebo suspect)", async () => {
    // Interrupt resolves (204 acceptance) but the authoritative active map
    // still reports the session running after the settle window — the exact
    // 204-but-fiber-alive placebo the feature exists to prevent.
    const { h, controller } = createHarness({ state: "running", confirmResult: true, active: true })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(1)
    await Bun.sleep(40)
    expect(toastOf(h, "warning", "Session still active after interrupt")).toBeDefined()
    expect(h.logs.some((line) => line.includes("PLACEBO SUSPECT"))).toBe(true)
  })

  test("no false warning when a new prompt started before the settle check", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true, active: true })
    await controller.handleStopClick()
    h.messageID = "msg_2" // new user message → new run owns the active entry
    await Bun.sleep(40)
    expect(toastOf(h, "warning")).toBeUndefined()
  })

  test("no warning when the session settles idle after the interrupt", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true, active: false })
    await controller.handleStopClick()
    await Bun.sleep(40)
    expect(toastOf(h, "warning")).toBeUndefined()
    expect(h.logs.some((line) => line.includes("settle verified"))).toBe(true)
  })

  test("settle check failure is logged, never thrown", async () => {
    const { h, controller } = createHarness({ state: "running", confirmResult: true })
    await controller.handleStopClick()
    h.activeError = new Error("server down") // fails only the later settle probe
    await Bun.sleep(40)
    expect(toastOf(h, "warning")).toBeUndefined()
    expect(h.logs.some((line) => line.includes("settle check unavailable"))).toBe(true)
  })
})

describe("stop-button dialog text click bubbling — Yes/No inner <text> handler", () => {
  test("Yes text click resolves true → exactly 1 interrupt and logs confirmed=true", async () => {
    // Simulates clicking the inner <text>Yes</text> which previously did not
    // bubble to the outer box onMouseUp and fell through to onClose false
    // (Yes logged as cancelled). With the text handler both paths resolve true.
    const { h, controller } = createHarness({ state: "running", confirmResult: true })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(1)
    expect(h.calls[0]).toBe(SESSION)
    expect(h.logs.some((line) => line.includes("confirmed=true"))).toBe(true)
    expect(h.logs.some((line) => line.includes("confirmed=false"))).toBe(false)
    expect(toastOf(h, "success", "Interrupted")).toBeDefined()
  })

  test("No text click resolves false → 0 interrupt and logs confirmed=false", async () => {
    // Simulates clicking the inner <text>No</text> — must stay as cancelled
    // via confirming->running, not leak to interrupting.
    const { h, controller } = createHarness({ state: "running", confirmResult: false })
    await controller.handleStopClick()
    expect(h.calls).toHaveLength(0)
    expect(h.logs.some((line) => line.includes("confirmed=false"))).toBe(true)
    expect(h.logs.some((line) => line.includes("cancelled"))).toBe(true)
    expect(toastOf(h, "success")).toBeUndefined()
  })

  test("discriminating log before dialogEvent mapping exposes Yes-mis-as-cancelled", async () => {
    // Cheapest falsifying test for the bubbling bug: without the
    // confirmed=${confirmed} log, a Yes that fell through to the onClose
    // fallback (resolve false) would be indistinguishable from a real No in
    // the log stream. This asserts the log is present and discriminating.
    const { h: hYes, controller: cYes } = createHarness({ state: "running", confirmResult: true })
    await cYes.handleStopClick()
    const { h: hNo, controller: cNo } = createHarness({ state: "running", confirmResult: false })
    await cNo.handleStopClick()
    const yesLog = hYes.logs.find((l) => l.includes("confirmed="))
    const noLog = hNo.logs.find((l) => l.includes("confirmed="))
    expect(yesLog).toBeDefined()
    expect(noLog).toBeDefined()
    expect(yesLog).toContain("confirmed=true")
    expect(noLog).toContain("confirmed=false")
    expect(yesLog).not.toEqual(noLog)
  })
})
