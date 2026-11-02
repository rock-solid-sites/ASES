import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { classify } from './classify.mjs';

const baseline=JSON.parse(readFileSync(new URL('./snapshot-2026-11-02T0349Z.json', import.meta.url)));
const copied=()=>structuredClone(baseline);

test('verified Cloudflare ticks use nominal minute, not provider timestamp, and exclude propagation warmup',()=>{
  const report=classify(baseline);
  assert.equal(report.cloud.expected_slots_elapsed,5);
  assert.equal(report.cloud.observed_slots,5);
  assert.equal(report.cloud.excluded_warmup_rows.length,1);
  assert.equal(report.cloud.slots[0].scheduled_offset_ms,31387);
  assert.equal(report.cloud.slots[0].end_to_end_from_nominal_ms,32218);
  assert.equal(report.cloud.slots[0].execution_after_provider_scheduled_ms,831);
});
test('GitHub no-run-visible is not a failed job or a proven dropped event',()=>{
  const report=classify(baseline);
  for(const arm of report.github){
    assert.equal(arm.expected_slots_elapsed,1);
    assert.equal(arm.run_creations_since_first_slot,0);
    assert.equal(arm.slot_observations[0].observation,'NO_RUN_VISIBLE_AS_OF_QUERY');
    assert.equal(arm.provider_root_cause,'UNRESOLVED');
  }
  assert.equal(report.interpretation.permanent_dropped_event_claim,'NOT_ESTABLISHED');
});
test('later run is observed but not attributed to a specific nominal slot',()=>{
  const x=copied();
  x.as_of_utc='2026-11-02T06:50:00Z';
  x.github[0].runs.push({id:7,event:'schedule',created_at:'2026-11-02T06:18:00Z',status:'completed',conclusion:'success'});
  const r=classify(x).github[0];
  assert.equal(r.run_creations_since_first_slot,1);
  assert.equal(r.run_to_nominal_slot_attribution,'UNAVAILABLE_FROM_GITHUB_RUN_LIST');
  assert.equal(r.slot_observations[0].observation,'SLOT_ATTRIBUTION_UNRESOLVED');
  assert.equal(r.slot_observations[1].observation,'SLOT_ATTRIBUTION_UNRESOLVED');
});
test('unavailable query produces observer failure, not scheduler failure',()=>{
  const x=copied();x.cloud.source.status='ERROR';x.github[0].source.status='ERROR';
  const r=classify(x);
  assert.equal(r.cloud.slots[0].observation,'OBSERVER_UNAVAILABLE');
  assert.equal(r.github[0].slot_observations[0].observation,'OBSERVER_UNAVAILABLE');
});
test('missing D1 row remains no observation and causal attribution unresolved',()=>{
  const x=copied();x.cloud.rows.splice(3,1);const r=classify(x);
  assert.equal(r.cloud.observed_slots,4);
  assert.equal(r.cloud.slots[2].observation,'NO_ROW_VISIBLE_AS_OF_QUERY');
  assert.equal(r.cloud.slots[2].causal_status,'UNRESOLVED');
});
test('disabled dispatch is NOT_RUN_BY_DESIGN, never PASS or a 204',()=>{
  const r=classify(baseline);
  assert.equal(r.external_dispatch.execution,'NOT_RUN_BY_DESIGN');
  assert.equal(r.external_dispatch.claimed_success,'NOT_EVALUATED');
});
test('snapshot before any GitHub first slot has no denominator, not a missed run',()=>{
  const x=copied();x.as_of_utc='2026-11-02T02:49:00Z';
  const r=classify(x);
  assert.equal(r.github[0].expected_slots_elapsed,0);
  assert.equal(r.github[1].expected_slots_elapsed,0);
});
test('duplicate count carried without confusing it with an additional logical slot',()=>{
  const x=copied();x.cloud.rows[2].duplicate_count=2;const r=classify(x);
  assert.equal(r.cloud.slots[1].duplicates,2);
  assert.equal(r.cloud.observed_slots,5);
});
