// ASES research-only scheduler clock. Never probes production or writes GitHub issues.
// External dispatch is OFF until both an opt-in flag and a scoped secret are installed.
const TARGET = "https://api.github.com/repos/rock-solid-sites/ASES/actions/workflows/ases-schedule-probe.yml/dispatches";

export default {
  async scheduled(controller, env) {
    const scheduledMs = Number(controller.scheduledTime);
    if (!Number.isSafeInteger(scheduledMs)) throw new Error("Invalid scheduledTime");

    const slot = new Date(scheduledMs);
    const observedMs = Date.now();
    const isDispatchSlot = slot.getUTCMinutes() === 9 && slot.getUTCHours() % 3 === 0;
    const dispatchEnabled = env.DISPATCH_ENABLED === "true";
    const initialStatus = !isDispatchSlot ? "not_dispatch_slot"
      : dispatchEnabled ? "pending" : "disabled";

    // Atomic claim keeps duplicate Cron deliveries from dispatching twice.
    const claim = await env.DB.prepare(
      "INSERT OR IGNORE INTO ticks (scheduled_ms, observed_ms, last_seen_ms, cron, dispatch_status) VALUES (?, ?, ?, ?, ?)"
    ).bind(scheduledMs, observedMs, observedMs, controller.cron, initialStatus).run();

    if (claim.meta?.changes !== 1) {
      await env.DB.prepare(
        "UPDATE ticks SET duplicate_count = duplicate_count + 1, last_seen_ms = ? WHERE scheduled_ms = ?"
      ).bind(observedMs, scheduledMs).run();
      console.log(JSON.stringify({ event: "duplicate", scheduled_utc: slot.toISOString() }));
      return;
    }

    if (!isDispatchSlot || !dispatchEnabled) {
      console.log(JSON.stringify({
        event: "heartbeat", scheduled_utc: slot.toISOString(),
        observed_utc: new Date(observedMs).toISOString(), dispatch: initialStatus
      }));
      return;
    }

    let status = "missing_token", httpCode = null, errorCode = null;
    if (env.GITHUB_ACTIONS_TOKEN) {
      try {
        const response = await fetch(TARGET, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${env.GITHUB_ACTIONS_TOKEN}`,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "ases-schedule-research-clock"
          },
          body: JSON.stringify({ ref: "main", inputs: { slot_utc: slot.toISOString() } }),
          signal: AbortSignal.timeout(10000)
        });
        httpCode = response.status;
        status = response.status === 204 ? "accepted" : "rejected";
      } catch (e) {
        status = "error";
        errorCode = String(e?.name || "unknown").slice(0,60);
      }
    }
    await env.DB.prepare(
      "UPDATE ticks SET dispatch_status = ?, http_code = ?, error_code = ? WHERE scheduled_ms = ?"
    ).bind(status, httpCode, errorCode, scheduledMs).run();

    // Never log bearer tokens or response bodies.
    console.log(JSON.stringify({
      event: "dispatch_result", scheduled_utc: slot.toISOString(), status, http_code: httpCode
    }));
  },
  async fetch() {
    return new Response("Not found", { status: 404 });
  }
};
