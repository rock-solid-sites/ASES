/** Experimental, deterministic and read-only placement planner (no cloud credentials or launch code). */
export type DataClass = 'public' | 'internal' | 'production';
export type ResourceKind = 'persistent-host' | 'workspace' | 'batch' | 'managed-agent';
export type Availability = 'verified' | 'candidate' | 'retired';

export interface IdentityDomain {
  id: string;
  githubAccount?: string;
  githubStatus: 'existing' | 'planned';
}

export interface ProviderAccount {
  id: string;
  domainId: string;
  provider: string;
  remainingIncludedMinutes: number;
  maxAdditionalSpendUsd: number;
}

export interface Resource {
  id: string;
  accountId: string;
  kind: ResourceKind;
  availability: Availability;
  cpu: number;
  ramGiB: number;
  startupMinutes: number;
  usdPerMinute: number;
  transferGiBPerMinute: number;
  egressUsdPerGiB: number;
  riskScore: number;
  accepts: DataClass[];
  harnesses: string[];
  maxSessionMinutes?: number;
  warm?: boolean;
}

export interface Stage {
  id: string;
  after: string[];
  estimatedMinutes: number;
  minCpu: number;
  minRamGiB: number;
  dataClass: DataClass;
  harness: string;
  kind: ResourceKind[];
  transferGiBFrom?: Record<string, number>;
  independentFrom?: string[];
}

export interface ObservedStage {
  stageId: string;
  resourceId: string;
  finishedAtMinute: number;
  actualMinutes: number;
  actualCashUsd: number;
  /** True only if a completed job's original workspace still exists. */
  reusableSession: boolean;
}

export interface PlanningInput {
  domains: IdentityDomain[];
  accounts: ProviderAccount[];
  resources: Resource[];
  domainId: string;
  stages: Stage[];
  maxNewSpendUsd: number;
  observations?: ObservedStage[];
  maxAssignments?: number;
}

export interface StagePlacement {
  stageId: string;
  resourceId: string;
  startMinute: number;
  finishMinute: number;
  chargeableMinutes: number;
  state: 'observed' | 'estimated';
}

export interface Proposal {
  objective: 'lowest-cash' | 'fastest' | 'lowest-risk';
  projectedNewSpendUsd: number;
  recordedSpendUsd: number;
  projectedFinishMinutes: number;
  riskExposure: number;
  transfersGiB: number;
  placements: StagePlacement[];
  estimatedMinutesByAccount: Record<string, number>;
}

export interface PlanningResult {
  status: 'ok' | 'no-feasible-plan';
  evaluatedAssignments: number;
  proposals: Proposal[];
  diagnostic?: string;
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}
function validNonnegative(n: number, label: string): void {
  assert(Number.isFinite(n) && n >= 0, `${label} must be a nonnegative finite number`);
}
function finitePositive(n: number, label: string): void {
  assert(Number.isFinite(n) && n > 0, `${label} must be a positive finite number`);
}
function uniqueMap<T extends {id: string}>(values: T[], category: string): Map<string, T> {
  const map = new Map<string, T>();
  for (const value of values) {
    assert(typeof value.id === 'string' && value.id.length > 0, `invalid ${category} ID`);
    assert(!map.has(value.id), `duplicate ${category} ID ${value.id}`);
    map.set(value.id, value);
  }
  return map;
}

function topologicalSort(stages: Stage[]): Stage[] {
  const byId = uniqueMap(stages, 'stage');
  const result: Stage[] = [];
  const states = new Map<string, 'visiting' | 'visited'>();
  const visit = (id: string): void => {
    const current = states.get(id);
    assert(current !== 'visiting', `cycle detected at stage ${id}`);
    if (current === 'visited') return;
    const stage = byId.get(id);
    assert(stage, `missing dependency ${id}`);
    states.set(id, 'visiting');
    for (const parent of stage.after) visit(parent);
    states.set(id, 'visited');
    result.push(stage);
  };
  for (const s of stages) visit(s.id);
  return result;
}

/** Fails closed when fixture/registry data is invalid or ownership is ambiguous. */
function validate(input: PlanningInput): {
  stages: Stage[];
  accounts: Map<string, ProviderAccount>;
  resources: Map<string, Resource>;
  completed: Map<string, ObservedStage>;
} {
  const domains = uniqueMap(input.domains, 'domain');
  assert(domains.has(input.domainId), `unknown domain ${input.domainId}`);
  const accounts = uniqueMap(input.accounts, 'account');
  for (const account of accounts.values()) {
    assert(domains.has(account.domainId), `unknown account owner ${account.domainId}`);
    validNonnegative(account.remainingIncludedMinutes, `${account.id}.remainingIncludedMinutes`);
    validNonnegative(account.maxAdditionalSpendUsd, `${account.id}.maxAdditionalSpendUsd`);
  }
  const resources = uniqueMap(input.resources, 'resource');
  for (const r of resources.values()) {
    assert(accounts.has(r.accountId), `resource ${r.id} refers to unknown account`);
    finitePositive(r.cpu, `${r.id}.cpu`);
    finitePositive(r.ramGiB, `${r.id}.ramGiB`);
    validNonnegative(r.startupMinutes, `${r.id}.startupMinutes`);
    validNonnegative(r.usdPerMinute, `${r.id}.usdPerMinute`);
    finitePositive(r.transferGiBPerMinute, `${r.id}.transferGiBPerMinute`);
    validNonnegative(r.egressUsdPerGiB, `${r.id}.egressUsdPerGiB`);
    validNonnegative(r.riskScore, `${r.id}.riskScore`);
    if (r.maxSessionMinutes !== undefined) finitePositive(r.maxSessionMinutes, `${r.id}.maxSessionMinutes`);
  }
  validNonnegative(input.maxNewSpendUsd, 'maxNewSpendUsd');
  if (input.maxAssignments !== undefined) finitePositive(input.maxAssignments, 'maxAssignments');
  const stages = topologicalSort(input.stages);
  const stageById = new Map(stages.map(s => [s.id, s]));
  for (const s of stages) {
    finitePositive(s.estimatedMinutes, `${s.id}.estimatedMinutes`);
    finitePositive(s.minCpu, `${s.id}.minCpu`);
    finitePositive(s.minRamGiB, `${s.id}.minRamGiB`);
    assert(['public','internal','production'].includes(s.dataClass), `${s.id} invalid dataClass`);
    for (const id of s.independentFrom || []) {
      assert(stageById.has(id), `${s.id} unknown independentFrom ${id}`);
      assert(id !== s.id, `${s.id} cannot be independent of itself`);
    }
    for (const [id, gb] of Object.entries(s.transferGiBFrom || {})) {
      assert(s.after.includes(id), `${s.id} transfer source ${id} is not a predecessor`);
      validNonnegative(gb, `${s.id}.transferGiBFrom.${id}`);
    }
  }
  const completed = uniqueMap((input.observations || []).map(o => ({ ...o, id: o.stageId })), 'observed stage');
  for (const o of completed.values()) {
    assert(stageById.has(o.stageId), `unknown observed stage ${o.stageId}`);
    const resource = resources.get(o.resourceId);
    assert(resource, `unknown observed resource ${o.resourceId}`);
    assert(accounts.get(resource.accountId)?.domainId === input.domainId, `observed stage ${o.stageId} crossed identity boundary`);
    validNonnegative(o.finishedAtMinute, `${o.stageId}.finishedAtMinute`);
    validNonnegative(o.actualMinutes, `${o.stageId}.actualMinutes`);
    validNonnegative(o.actualCashUsd, `${o.stageId}.actualCashUsd`);
    assert(o.reusableSession === true || o.reusableSession === false, 'reusableSession must be boolean');
    for (const predecessor of stageById.get(o.stageId)!.after) {
      assert(completed.has(predecessor), `cannot complete ${o.stageId} ahead of unfinished dependency ${predecessor}`);
    }
  }
  return {stages, accounts, resources, completed};
}

function feasibleResource(stage: Stage, r: Resource, account: ProviderAccount, domainId: string): boolean {
  return account.domainId === domainId && r.availability === 'verified'
    && r.cpu >= stage.minCpu && r.ramGiB >= stage.minRamGiB
    && r.accepts.includes(stage.dataClass) && r.harnesses.includes(stage.harness)
    && stage.kind.includes(r.kind) && (r.maxSessionMinutes === undefined || r.maxSessionMinutes >= stage.estimatedMinutes + (r.warm ? 0 : r.startupMinutes));
}

type Candidate = Omit<Proposal, 'objective'> & { signature: string };

function evaluate(input: PlanningInput, orderedStages: Stage[], accountMap: Map<string, ProviderAccount>, resourceMap: Map<string, Resource>, completed: Map<string, ObservedStage>, assignment: Map<string, string>): Candidate | null {
  const placements: StagePlacement[] = [];
  const byStage = new Map<string, StagePlacement>();
  const byResourceUsed = new Map<string, number>();
  const sessionStarted = new Map<string, number>();
  const billables: Array<{accountId:string; rate:number; billable:number}> = [];
  let recordedSpendUsd = 0;
  let transferCost = 0;
  let transfersGiB = 0;
  let riskExposure = 0;
  for (const stage of orderedStages) {
    const obs = completed.get(stage.id);
    const rid = obs?.resourceId || assignment.get(stage.id);
    assert(rid, `missing placement for ${stage.id}`);
    const res = resourceMap.get(rid)!;
    const account = accountMap.get(res.accountId)!;
    const parentPlacements = stage.after.map(p => byStage.get(p)!);
    let ready = parentPlacements.reduce((acc, p) => Math.max(acc, p.finishMinute), 0);
    for (const parent of parentPlacements) {
      // Completed work is immutable history: predicted transfer time and cost are not re-billed.
      if (obs || parent.resourceId === rid) continue;
      const source = resourceMap.get(parent.resourceId)!;
      const gb = stage.transferGiBFrom?.[parent.stageId] || 0;
      transfersGiB += gb;
      ready = Math.max(ready, parent.finishMinute + gb / Math.min(source.transferGiBPerMinute, res.transferGiBPerMinute));
      transferCost += gb * source.egressUsdPerGiB;
    }
    for (const prior of orderedStages) {
      const current = byStage.get(prior.id);
      if (current?.resourceId === rid && ((stage.independentFrom || []).includes(prior.id) || (prior.independentFrom || []).includes(stage.id))) return null;
    }
    if (obs) {
      const fixed: StagePlacement = {stageId:stage.id, resourceId:rid,startMinute:Math.max(0, obs.finishedAtMinute - obs.actualMinutes),finishMinute:obs.finishedAtMinute,chargeableMinutes:0,state:'observed'};
      if (fixed.finishMinute < parentPlacements.reduce((acc,p)=>Math.max(acc,p.finishMinute),0)) return null;
      placements.push(fixed);
      byStage.set(stage.id, fixed);
      recordedSpendUsd += obs.actualCashUsd;
      byResourceUsed.set(rid, Math.max(byResourceUsed.get(rid) || 0, fixed.finishMinute));
      if (obs.reusableSession) sessionStarted.set(rid, fixed.startMinute);
      continue;
    }
    const firstUse = !sessionStarted.has(rid);
    const startup = firstUse && !res.warm ? res.startupMinutes : 0;
    const begin = Math.max(ready, byResourceUsed.get(rid) || 0);
    const start = begin + startup;
    const finish = start + stage.estimatedMinutes;
    const started = sessionStarted.get(rid) ?? begin;
    if (res.maxSessionMinutes !== undefined && finish - started > res.maxSessionMinutes) return null;
    sessionStarted.set(rid, started);
    byResourceUsed.set(rid, finish);
    const p: StagePlacement = {stageId:stage.id,resourceId:rid,startMinute:start,finishMinute:finish,chargeableMinutes:stage.estimatedMinutes+startup,state:'estimated'};
    placements.push(p);
    byStage.set(stage.id, p);
    billables.push({accountId:account.id,rate:res.usdPerMinute,billable:p.chargeableMinutes});
    riskExposure += res.riskScore * p.chargeableMinutes;
  }
  const minuteUsage: Record<string, number> = {};
  const additionalSpend: Record<string,number> = {};
  for (const b of billables) minuteUsage[b.accountId] = (minuteUsage[b.accountId]||0)+b.billable;
  // Allocate each account's included minutes to the most expensive work first.
  let projectedCash = transferCost;
  for (const [accountId, account] of accountMap) {
    let allowance = account.remainingIncludedMinutes;
    let spend = 0;
    const jobs = billables.filter(b=>b.accountId===accountId).sort((a,b)=>b.rate-a.rate);
    for (const job of jobs) {
      const covered = Math.min(allowance,job.billable);
      allowance-=covered;
      spend += (job.billable-covered)*job.rate;
    }
    additionalSpend[accountId]=spend;
    if (spend > account.maxAdditionalSpendUsd+1e-9) return null;
    projectedCash+=spend;
  }
  if (projectedCash > input.maxNewSpendUsd+1e-9) return null;
  const signature = orderedStages.map(s=>`${s.id}:${completed.get(s.id)?.resourceId||assignment.get(s.id)}`).join('|');
  return {projectedNewSpendUsd:projectedCash, recordedSpendUsd,projectedFinishMinutes:Math.max(0,...placements.map(p=>p.finishMinute)),riskExposure,transfersGiB,placements,estimatedMinutesByAccount:minuteUsage,signature};
}

/** Searches all feasible placements up to a safe explicit bound; never launches resources. */
export function proposePlans(input: PlanningInput): PlanningResult {
  const {stages,accounts,resources,completed}=validate(input);
  const candidateResources = [...resources.values()].sort((a,b)=>a.id.localeCompare(b.id));
  const options = stages.filter(s=>!completed.has(s.id)).map(s=>({stage:s,choices:candidateResources.filter(r=>feasibleResource(s,r,accounts.get(r.accountId)!,input.domainId))}));
  if (options.some(o=>o.choices.length===0)) return {status:'no-feasible-plan',evaluatedAssignments:0,proposals:[],diagnostic:`No eligible resource for ${options.filter(o=>!o.choices.length).map(o=>o.stage.id).join(', ')} under identity ${input.domainId}`};
  const limit=input.maxAssignments??4096;
  const count=options.reduce((n,o)=>n*o.choices.length,1);
  assert(Number.isSafeInteger(count)&&count<=limit, `assignment search space ${count} exceeds maxAssignments=${limit}; reduce stage/target scope rather than returning misleading optimum`);
  const assignment=new Map<string,string>();
  const results:Candidate[]=[];
  const run=(i:number):void=>{
    if(i===options.length){const p=evaluate(input,stages,accounts,resources,completed,assignment);if(p)results.push(p);return;}
    const option = options[i]!;
    for(const resource of option.choices){assignment.set(option.stage.id,resource.id);run(i+1);}
  };
  run(0);
  if(results.length===0) return {status:'no-feasible-plan',evaluatedAssignments:count,proposals:[],diagnostic:'All assignments failed cost, isolation, session-lifetime or independence constraints'};
  const comparators:{objective:Proposal['objective'];cmp:(a:Candidate,b:Candidate)=>number}[]=[
    {objective:'lowest-cash',cmp:(a,b)=>a.projectedNewSpendUsd-b.projectedNewSpendUsd||a.projectedFinishMinutes-b.projectedFinishMinutes||a.riskExposure-b.riskExposure},
    {objective:'fastest',cmp:(a,b)=>a.projectedFinishMinutes-b.projectedFinishMinutes||a.projectedNewSpendUsd-b.projectedNewSpendUsd||a.riskExposure-b.riskExposure},
    {objective:'lowest-risk',cmp:(a,b)=>a.riskExposure-b.riskExposure||a.projectedNewSpendUsd-b.projectedNewSpendUsd||a.projectedFinishMinutes-b.projectedFinishMinutes},
  ];
  const proposals:Proposal[]=[];
  const seen=new Set<string>();
  for(const {objective,cmp} of comparators){
    const winner=[...results].sort((a,b)=>cmp(a,b)||a.signature.localeCompare(b.signature))[0]!;
    if(!seen.has(winner.signature)){
      seen.add(winner.signature);
      const {signature,...plan}=winner;
      proposals.push({...plan,objective});
    }
  }
  return {status:'ok',evaluatedAssignments:count,proposals};
}