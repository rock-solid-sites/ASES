import test from 'node:test';
import assert from 'node:assert/strict';
import { cronSlots, minimumLateness, githubReadback, gitlabReadback } from './readback-v2.mjs';

const gh = (payload, asOfUtc='2026-11-03T00:29:00Z') => githubReadback({
  payload, workflowId:404004929, firstEvaluableUtc:'2026-11-02T03:13:00Z',
  periodMinutes:180, asOfUtc
});

test('three-hour UTC cron slots include 21:13, never invented 19:13', () => {
  const s=cronSlots('2026-11-02T03:13:00Z',180,'2026-11-03T00:29:00Z');
  assert.equal(s.length,8);
  assert.ok(s.includes('2026-11-02T21:13:00.000Z'));
  assert.ok(!s.includes('2026-11-02T19:13:00.000Z'));
});

test('21:41 ASES lower bound is 28m32, not 2h28', () => {
  const r=minimumLateness('2026-11-02T03:13:00Z',180,'2026-11-02T21:41:32Z');
  assert.equal(r.latest_possible_slot_utc,'2026-11-02T21:13:00.000Z');
  assert.equal(r.minimum_lateness_ms,1712000);
  assert.equal(r.reason,'LOWER_BOUND_ONLY_SLOT_UNATTRIBUTED');
});

test('21:39 Tripn lower bound is 32m43', () => {
  const r=minimumLateness('2026-11-02T03:07:00Z',180,'2026-11-02T21:39:43Z');
  assert.equal(r.minimum_lateness_ms,1963000);
});

test('10:54 ASES lower bound is 1h41m58', () => {
  assert.equal(minimumLateness('2026-11-02T03:13:00Z',180,'2026-11-02T10:54:58Z').minimum_lateness_ms,6118000);
});

test('run from before first eligible slot has no fake attribution', () => {
  const r=minimumLateness('2026-11-02T03:13:00Z',180,'2026-11-02T00:36:11Z');
  assert.equal(r.minimum_lateness_ms,null);
});

test('repository-wide collection is filtered by exact workflow and schedule event', () => {
  const report=gh({total_count:3,workflow_runs:[
    {id:9,workflow_id:404004929,event:'schedule',created_at:'2026-11-02T21:41:32Z',conclusion:'success'},
    {id:8,workflow_id:404004929,event:'workflow_dispatch',created_at:'2026-11-02T12:00:00Z'},
    {id:7,workflow_id:123,event:'schedule',created_at:'2026-11-02T10:55:00Z'}
  ]});
  assert.equal(report.status,'OK');
  assert.equal(report.run_creations_observed,1);
  assert.equal(report.runs[0].id,9);
  assert.equal(report.slot_attribution,'SLOT_ATTRIBUTION_UNRESOLVED');
});

test('truncated page covering earlier-than-window rows is still complete for window', () => {
  const report=gh({total_count:300,workflow_runs:[
    {id:9,workflow_id:404004929,event:'schedule',created_at:'2026-11-02T21:41:32Z'},
    {id:1,workflow_id:123,event:'schedule',created_at:'2026-11-01T00:00:00Z'}
  ]});
  assert.equal(report.status,'OK');
});

test('truncated page not reaching eligible window is partial, not evidence of absence', () => {
  const report=gh({total_count:300,workflow_runs:[
    {id:9,workflow_id:123,event:'schedule',created_at:'2026-11-02T22:00:00Z'},
    {id:8,workflow_id:123,event:'schedule',created_at:'2026-11-02T20:00:00Z'}
  ]});
  assert.equal(report.status,'OBSERVER_PARTIAL');
  assert.equal(report.run_creations_observed,0);
});

test('unsorted results are partial rather than silently assuming completeness', () => {
  const report=gh({total_count:3,workflow_runs:[
    {id:1,workflow_id:123,event:'schedule',created_at:'2026-11-01T00:00:00Z'},
    {id:2,workflow_id:123,event:'schedule',created_at:'2026-11-02T20:00:00Z'}
  ]});
  assert.equal(report.status,'OBSERVER_PARTIAL');
});

test('missing or malformed collection is observer failure, not scheduler miss', () => {
  assert.equal(gh({}).status,'OBSERVER_UNAVAILABLE');
  assert.equal(gh({total_count:1,workflow_runs:[]}).status,'OBSERVER_PARTIAL');
});

test('duplicate run ID is a data integrity error', () => {
  assert.throws(()=>gh({total_count:2,workflow_runs:[
    {id:11,workflow_id:404004929,event:'schedule',created_at:'2026-11-02T21:41:32Z'},
    {id:11,workflow_id:404004929,event:'schedule',created_at:'2026-11-02T21:41:32Z'}
  ]}),/DUPLICATE_RUN_ID/);
});

test('GitLab missing schedule metadata cannot establish activation denominator', () => {
  const r=gitlabReadback({pipelines:[{id:3016894193,source:'api',status:'success'}]});
  assert.equal(r.status,'CONFIGURATION_UNVERIFIED');
  assert.equal(r.expected_slots,null);
  assert.equal(r.scheduled_pipelines.length,0);
});

test('GitLab scheduled pipeline can be observed without claiming slot identity', () => {
  const r=gitlabReadback({pipelines:[{id:123,source:'schedule',created_at:'2026-11-03T03:23:00Z',status:'success'}]});
  assert.equal(r.scheduled_pipelines.length,1);
  assert.equal(r.slot_attribution,'SLOT_ATTRIBUTION_UNRESOLVED');
  assert.equal(r.status,'CONFIGURATION_UNVERIFIED');
});

test('GitLab failed pipeline API query is an observer failure', () => {
  assert.equal(gitlabReadback({pipelineQueryStatus:'ERROR'}).status,'OBSERVER_UNAVAILABLE');
});

test('classify integrates new readback evidence without altering frozen snapshot', async () => {
  const {classify}=await import('./classify.mjs');
  const input={
    schema_version:'0.1',as_of_utc:'2026-11-03T00:29:00Z',
    cloud:{first_evaluable_utc:'2026-11-02T01:39:00Z',interval_minutes:30,source:{status:'ERROR'}},
    github:[{id:'ases',first_evaluable_utc:'2026-11-02T03:13:00Z',interval_minutes:180,source:{status:'OK'},runs:[
      {id:41530651460,event:'schedule',created_at:'2026-11-02T21:41:32Z',conclusion:'success',status:'completed'}
    ]}],
    gitlab:{source:{status:'OK'},schedule_source:{status:'UNAVAILABLE'},pipelines:[{id:3016894193,source:'api',status:'success'}]},
    external_dispatch:{enabled:false}
  };
  const result=classify(input);
  assert.equal(result.github[0].run_events[0].minimum_lateness_ms,1712000);
  assert.equal(result.github[0].run_events[0].latest_possible_slot_utc,'2026-11-02T21:13:00.000Z');
  assert.equal(result.gitlab.status,'CONFIGURATION_UNVERIFIED');
  assert.equal(result.gitlab.expected_slots,null);
  assert.equal(result.external_dispatch.execution,'NOT_RUN_BY_DESIGN');
});

test('one of two GitLab schedules is insufficient to verify full configuration', () => {
  const expectedSchedules=[
    {description:'ases-clock-gitlab-A-17m-3h',cron:'17 */3 * * *',timezone:'UTC'},
    {description:'ases-clock-gitlab-B-47m-3h',cron:'47 */3 * * *',timezone:'UTC'}
  ];
  const a={id:1,active:true,description:expectedSchedules[0].description,
    cron:expectedSchedules[0].cron,cron_timezone:'UTC',
    ref:'research/scheduler-clock-gitlab-2026-11-02',
    created_at:'2026-11-02T12:00:00Z',next_run_at:'2026-11-03T06:17:00Z'};
  const opts={pipelines:[],schedules:[a],expectedSchedules,
    expectedRef:'research/scheduler-clock-gitlab-2026-11-02',scheduleQueryStatus:'OK'};
  assert.equal(gitlabReadback(opts).status,'CONFIGURATION_UNVERIFIED');
  const b={...a,id:2,description:expectedSchedules[1].description,cron:expectedSchedules[1].cron};
  assert.equal(gitlabReadback({...opts,schedules:[a,b]}).status,'CONFIGURATION_OBSERVED');
  assert.equal(gitlabReadback({...opts,schedules:[a,{...b,active:false}]}).status,'CONFIGURATION_UNVERIFIED');
});
test('GitLab schedule metadata does not imply verified activation time or missing slots', () => {
  const r=gitlabReadback({pipelines:[],schedules:[{
    id:1,active:true,description:'A',cron:'17 */3 * * *',cron_timezone:'UTC',
    ref:'main',created_at:'2026-11-02T12:00:00Z',next_run_at:'2026-11-03T06:17:00Z'
  }],expectedSchedules:[{description:'A',cron:'17 */3 * * *',timezone:'UTC',ref:'main'}],scheduleQueryStatus:'OK'});
  assert.equal(r.status,'CONFIGURATION_OBSERVED');
  assert.equal(r.expected_slots,null);
});
