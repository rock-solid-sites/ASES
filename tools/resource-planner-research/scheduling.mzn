% Research-only common model for unary compute resources, alternative modes,
% fixed account quotas, per-mode cash, dependency transfer and independence.
int: n;
int: r;
int: kmax;
int: horizon;
int: budget;
array[1..n] of int: kcount;
array[1..n,1..kmax] of int: mode_resource;
array[1..n,1..kmax] of int: mode_duration;
array[1..n,1..kmax] of int: mode_cost;
array[1..r] of int: quota;
array[1..n,1..n] of bool: depends;
array[1..n,1..n] of bool: independent;
array[1..n] of int: move_penalty;
array[1..n] of var 1..kmax: chosen;
array[1..n] of var 0..horizon: st;
array[1..n] of var 1..horizon: du;
array[1..n] of var 1..r: use_res;
array[1..n] of var 0..budget: price;
array[1..n] of var 0..horizon: fin;
var 0..horizon: makespan;
constraint forall(i in 1..n)(
  chosen[i]<=kcount[i] /\
  use_res[i]=mode_resource[i,chosen[i]] /\
  du[i]=mode_duration[i,chosen[i]] /\
  price[i]=mode_cost[i,chosen[i]] /\
  fin[i]=st[i]+du[i] /\
  fin[i]<=horizon
);
constraint forall(i in 1..n,j in i+1..n)(
  (use_res[i]==use_res[j] -> (fin[i]<=st[j] \/ fin[j]<=st[i]))
);
constraint forall(i in 1..n,j in 1..n where depends[i,j])(
  st[j]>=fin[i]+bool2int(use_res[i]!=use_res[j])*move_penalty[j]
);
constraint forall(i in 1..n,j in 1..n where independent[i,j])(
  use_res[i]!=use_res[j]
);
constraint forall(q in 1..r)(
  sum(i in 1..n)(bool2int(use_res[i]==q)*du[i])<=quota[q]
);
constraint sum(i in 1..n)(price[i])<=budget;
constraint makespan=max(fin);
solve minimize makespan;
output ["RESULT ",show(makespan),"|",show(st),"|",show(chosen),"\n"];
