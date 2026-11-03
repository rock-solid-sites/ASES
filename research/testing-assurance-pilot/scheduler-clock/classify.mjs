/**
 * ASES scheduler evidence classifier v0.1 (research-only).
 * No network access; no production side effects; zero implicit slot-to-run attribution.
 * Input: an immutable provider-read snapshot (see snapshot-2026-11-02T0349Z.json).
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { minimumLateness, gitlabReadback } from './readback-v2.mjs';

const iso = (ms) => new Date(ms).toISOString();
function timestamp(value, label) {
  const ms = Date.parse(value);
  if (!Number.isFinite(ms)) throw Error(`invalid timestamp: ${label}`);
  return ms;
}
function evidenceSlots(first, everyMinutes, asOf) {
  const start = timestamp(first, 'first_evaluable_utc');
  if (!Number.isInteger(everyMinutes) || everyMinutes < 1 || everyMinutes > 10080)
    throw Error('invalid slot interval');
  const result = [];
  for (let ms = start; ms <= asOf; ms += everyMinutes * 60_000) {
    if (result.length >= 10000) throw Error('snapshot exceeds 10,000 slots');
    result.push({ slot_utc: iso(ms), slot_ms: ms });
  }
  return result;
}

export function classify(snapshot) {
  const asOf = timestamp(snapshot.as_of_utc, 'as_of_utc');
  if (snapshot.schema_version !== '0.1') throw Error('unsupported snapshot schema');
  if (!snapshot.cloud || !Array.isArray(snapshot.github)) throw Error('missing evidence arms');
  const clock = snapshot.cloud;
  const slots = evidenceSlots(clock.first_evaluable_utc, clock.interval_minutes, asOf);
  const cloudSourceOK = clock.source?.status === 'OK';
  const rows = cloudSourceOK ? clock.rows || [] : [];
  const bySlot = new Map();
  for (const row of rows) {
    if (!Number.isSafeInteger(row.scheduled_ms) || !Number.isSafeInteger(row.observed_ms))
      throw Error('invalid raw Cloudflare row');
    const nominal = Math.floor(row.scheduled_ms / 60000) * 60000;
    if (bySlot.has(nominal)) throw Error('duplicate raw D1 row primary slot; preserve evidence, investigate');
    bySlot.set(nominal, row);
  }
  const cloudSlots = slots.map(s => {
    const row = bySlot.get(s.slot_ms);
    if (!cloudSourceOK) return { slot_utc:s.slot_utc, observation:'OBSERVER_UNAVAILABLE' };
    if (!row) return { slot_utc:s.slot_utc, observation:'NO_ROW_VISIBLE_AS_OF_QUERY', causal_status:'UNRESOLVED' };
    return {
      slot_utc:s.slot_utc,
      observation:'EXECUTION_RECORD_OBSERVED',
      d1_scheduled_utc:iso(row.scheduled_ms), observed_utc:iso(row.observed_ms),
      scheduled_offset_ms:row.scheduled_ms-s.slot_ms,
      execution_after_provider_scheduled_ms:row.observed_ms-row.scheduled_ms,
      end_to_end_from_nominal_ms:row.observed_ms-s.slot_ms,
      duplicates:row.duplicate_count,
      dispatch_telemetry:row.dispatch_status,
      delivery_cause:'NOT_INFERRED'
    };
  });
  const cloudOutsideWindow = rows.filter(r => {
    const nominal = Math.floor(r.scheduled_ms / 60000)*60000;
    return nominal < timestamp(clock.first_evaluable_utc,'first_evaluable_utc') || nominal > asOf;
  }).map(r=>({ d1_scheduled_utc:iso(r.scheduled_ms), observed_utc:iso(r.observed_ms), note:'excluded from completeness denominator' }));

  const github = snapshot.github.map(arm=>{
    const armSlots = evidenceSlots(arm.first_evaluable_utc,arm.interval_minutes,asOf);
    const sourceOK = arm.source?.status === 'OK';
    const runs = sourceOK ? (arm.runs || []) : [];
    const start = timestamp(arm.first_evaluable_utc,'github.first_evaluable_utc');
    const afterStart = runs.filter(x=>timestamp(x.created_at,'run.created_at') >= start && timestamp(x.created_at,'run.created_at') <= asOf);
    // GitHub schedule-event run payloads lack the intended UTC cron slot ID.
    // NEVER match runs to an intended slot solely by a nearest/interval heuristic.
    const slotReport=armSlots.map(s=>({
      slot_utc:s.slot_utc,
      observation:!sourceOK ? 'OBSERVER_UNAVAILABLE' : afterStart.length ? 'SLOT_ATTRIBUTION_UNRESOLVED' : 'NO_RUN_VISIBLE_AS_OF_QUERY',
      causal_status:'UNRESOLVED'
    }));
    return {
      id:arm.id, source_status:arm.source?.status || 'UNKNOWN',
      expected_slots_elapsed:armSlots.length,
      run_creations_since_first_slot:afterStart.length,
      run_events:afterStart.map(x=>({id:x.id, event:x.event, created_at:x.created_at, run_started_at:x.run_started_at || null, job_started_at:'NOT_OBSERVED_FROM_RUN_LIST', status:x.status, conclusion:x.conclusion, url:x.html_url, ...minimumLateness(arm.first_evaluable_utc,arm.interval_minutes,x.created_at)})),
      slot_observations:slotReport,
      run_to_nominal_slot_attribution:'UNAVAILABLE_FROM_GITHUB_RUN_LIST',
      execution_summary:afterStart.length ? 'RUN_CREATION_OBSERVED_NOT_SLOT_ATTRIBUTED' : 'NO_NEW_RUN_AS_OF_QUERY',
      provider_root_cause:'UNRESOLVED',
      instrument_quality:'PARTIALLY_QUALIFIED',
      note:'Missing observations can reflect delay, event non-delivery, incomplete provider data or observer faults; not automatically a failed executed job.'
    };
  });
  const gitlab = snapshot.gitlab ? gitlabReadback({
    pipelines:snapshot.gitlab.pipelines,
    schedules:snapshot.gitlab.schedules,
    scheduleQueryStatus:snapshot.gitlab.schedule_source?.status || 'UNAVAILABLE',
    pipelineQueryStatus:snapshot.gitlab.source?.status || 'ERROR'
  }) : null;
  return {
    schema_version:'0.1', as_of_utc:snapshot.as_of_utc,
    claim:'Compare source-attributed scheduling observations without collapsing execution into claim confidence or acceptance',
    cloud:{source_status:clock.source?.status || 'UNKNOWN', expected_slots_elapsed:slots.length,
      observed_slots:cloudSlots.filter(x=>x.observation==='EXECUTION_RECORD_OBSERVED').length,
      slots:cloudSlots, excluded_warmup_rows:cloudOutsideWindow,
      quality:'PARTIALLY_QUALIFIED',
      limitations:['D1 receipt verifies durable ingestion within Cloudflare, not independently complete Cron delivery',
        'Provider scheduled timestamp may be offset from nominal UTC cron minute',
        'No independent evidence of events absent from D1']},
    github,
    ...(gitlab ? {gitlab} : {}),
    external_dispatch:{execution:snapshot.external_dispatch?.enabled===false ? 'NOT_RUN_BY_DESIGN':'REQUIRES_DISPATCH_EVIDENCE',
      claimed_success:'NOT_EVALUATED'},
    archive:{source_metadata_snapshot:'RECORDED_IN_PROJECT_REPOSITORY_ON_COMMIT',
      github_complete_logs:'NOT_INDEPENDENTLY_ARCHIVED',
      cloudflare_d1_export:'SNAPSHOT_ONLY_NOT_AUTOMATED',
      completeness:'PARTIAL'},
    interpretation:{clock_operational_claim:'SUPPORTED_WITHIN_RECORDED_WINDOW',
      github_reliability_claim:'UNRESOLVED',
      permanent_dropped_event_claim:'NOT_ESTABLISHED',
      cause_of_regression:'NOT_ESTABLISHED',
      tripn_production_health:'NOT_TESTED_BY_THIS_EXPERIMENT',
      acceptance:'NOT_DECIDED_BY_CLASSIFIER'}
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const path=process.argv[2];
  if (!path) { console.error('Usage: node classify.mjs snapshot.json'); process.exitCode=2; }
  else {
    const bytes=readFileSync(path), input=JSON.parse(bytes.toString('utf8'));
    const report=classify(input);
    report.archive.input_sha256=createHash('sha256').update(bytes).digest('hex');
    console.log(JSON.stringify(report,null,2));
  }
}
