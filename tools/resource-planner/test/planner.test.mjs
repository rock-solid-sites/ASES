import test from 'node:test';
import assert from 'node:assert/strict';
import { proposePlans } from '../dist/planner.js';

const domains = [
  { id: 'ases', githubStatus: 'planned' },
  { id: 'hms', githubStatus: 'planned' },
  { id: 'tripn', githubStatus: 'existing', githubAccount: 'tripn-chill-zone' }
];
const accounts = [
  { id: 'a-ases', domainId: 'ases', provider: 'fixture-provider', remainingIncludedMinutes: 0, maxAdditionalSpendUsd: 100 },
  { id: 'a-hms', domainId: 'hms', provider: 'fixture-provider', remainingIncludedMinutes: 1000, maxAdditionalSpendUsd: 100 },
  { id: 'a-tripn', domainId: 'tripn', provider: 'fixture-provider', remainingIncludedMinutes: 1000, maxAdditionalSpendUsd: 100 }
];
const resource = (id, accountId, overrides = {}) => ({
  id, accountId, kind: 'workspace', availability: 'verified', cpu: 4, ramGiB: 16,
  startupMinutes: 0, usdPerMinute: 0.1, transferGiBPerMinute: 1,
  egressUsdPerGiB: 0, riskScore: 1, accepts: ['public','internal'],
  harnesses: ['opencode','none'], ...overrides
});
const resources = [
  resource('ases-remote', 'a-ases', { usdPerMinute: 0.1 }),
  resource('hms-remote', 'a-hms', { usdPerMinute: 0.0 }),
  resource('tripn-prod', 'a-tripn', { usdPerMinute: 0, accepts: ['public','internal','production'] })
];
const stage = (id, after = [], overrides={}) => ({
  id, after, estimatedMinutes: 10, minCpu: 2, minRamGiB: 4,
  dataClass: 'public', harness: 'none', kind: ['workspace'], ...overrides
});
const input = (domainId, stages, overrides={}) => ({domains,accounts,resources,domainId,stages,maxNewSpendUsd:100,...overrides});
const placements = (result) => result.proposals.flatMap(p=>p.placements);

test('three independent identities: never silently pool free account allowances', () => {
  for (const [domain, target] of [['ases','ases-remote'],['hms','hms-remote'],['tripn','tripn-prod']]) {
    const r = proposePlans(input(domain,[stage('build')]));
    assert.equal(r.status,'ok');
    assert.deepEqual(new Set(placements(r).map(p=>p.resourceId)), new Set([target]));
  }
});

test('Tripn production workload is scoped to existing Tripn production account', () => {
  const s=stage('deploy',[],{dataClass:'production'});
  assert.deepEqual(new Set(placements(proposePlans(input('tripn',[s]))).map(p=>p.resourceId)),new Set(['tripn-prod']));
  assert.equal(proposePlans(input('hms',[s])).status,'no-feasible-plan');
  assert.equal(proposePlans(input('ases',[s])).status,'no-feasible-plan');
});

test('unverified cloud capacity is rejected even when it is cheaper', () => {
  const r=proposePlans(input('ases',[stage('build')],{resources:[...resources,resource('cheap','a-ases',{usdPerMinute:0,availability:'candidate'})]}));
  assert.equal(r.status,'ok');
  assert.ok(placements(r).every(p=>p.resourceId!=='cheap'));
});

test('colocation can beat cheaper per-stage rate when transfer/setup is expensive', () => {
  const rs=[
    resource('warm','a-ases',{usdPerMinute:0.2,warm:true,transferGiBPerMinute:0.1,egressUsdPerGiB:1}),
    resource('cheap','a-ases',{usdPerMinute:0.05,startupMinutes:10,transferGiBPerMinute:0.1,egressUsdPerGiB:1})
  ];
  const stages=[stage('implement'),stage('verify',['implement'],{transferGiBFrom:{implement:10}})];
  const p=proposePlans(input('ases',stages,{resources:rs}));
  assert.equal(p.status,'ok');
  const cheapest=p.proposals.find(x=>x.objective==='lowest-cash');
  assert.ok(cheapest);
  assert.deepEqual(cheapest.placements.map(x=>x.resourceId),['cheap','cheap']);
  assert.equal(cheapest.transfersGiB,0);
});

test('fastest plan can differ from cheapest plan for parallel stages',()=>{
  const rs=[resource('expensive-fast','a-ases',{usdPerMinute:0.2,warm:true}),resource('cheap-slow','a-ases',{usdPerMinute:0.01,startupMinutes:20})];
  const p=proposePlans(input('ases',[stage('a'),stage('b')],{resources:rs}));
  assert.equal(p.status,'ok');
  assert.ok(p.proposals.find(x=>x.objective==='fastest'));
  assert.ok(p.proposals.find(x=>x.objective==='lowest-cash'));
  assert.ok(p.proposals.find(x=>x.objective==='fastest').projectedFinishMinutes <= p.proposals.find(x=>x.objective==='lowest-cash').projectedFinishMinutes);
});

test('an independent reviewer cannot run on its builder workspace',()=>{
  const p=proposePlans(input('ases',[stage('build'),stage('review',['build'],{independentFrom:['build']})],{
    resources:[resource('a','a-ases'),resource('b','a-ases')]
  }));
  assert.equal(p.status,'ok');
  assert.ok(p.proposals.every(x=>x.placements[0].resourceId!==x.placements[1].resourceId));
});

test('hard spend budget can make an otherwise possible assignment impossible',()=>{
  const p=proposePlans(input('ases',[stage('build')],{maxNewSpendUsd:0,resources:[resource('a','a-ases')]}));
  assert.equal(p.status,'no-feasible-plan');
});

test('replanning preserves completed stage and uses new duration estimate',()=>{
  const params=input('ases',[stage('design'),stage('test',['design'],{estimatedMinutes:30})],{
    resources:[resource('a','a-ases',{warm:true}),resource('b','a-ases',{warm:true})],
    observations:[{stageId:'design',resourceId:'a',finishedAtMinute:8,actualMinutes:8,actualCashUsd:0.8,reusableSession:true}]
  });
  const p=proposePlans(params);
  assert.equal(p.status,'ok');
  for(const plan of p.proposals){
    assert.equal(plan.placements[0].state,'observed');
    assert.equal(plan.placements[0].resourceId,'a');
    assert.equal(plan.placements[0].finishMinute,8);
    assert.equal(plan.recordedSpendUsd,0.8);
    assert.equal(plan.placements[1].chargeableMinutes,30);
  }
});

test('cycle detection and ambiguous observed identity fail closed',()=>{
  assert.throws(()=>proposePlans(input('ases',[stage('a',['b']),stage('b',['a'])])),/cycle/);
  assert.throws(()=>proposePlans(input('ases',[stage('a')],{
    observations:[{stageId:'a',resourceId:'tripn-prod',finishedAtMinute:5,actualMinutes:5,actualCashUsd:0,reusableSession:false}]
  })),/crossed identity boundary/);
});

test('unbounded search is rejected instead of presenting an incomplete optimum',()=>{
  const rs=Array.from({length:7},(_,i)=>resource('a'+i,'a-ases'));
  assert.throws(()=>proposePlans(input('ases',[stage('a'),stage('b'),stage('c'),stage('d'),stage('e')],{resources:rs})),/assignment search space/);
});