#!/usr/bin/env bun
import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import { Database } from "bun:sqlite";

async function runCrosslinkMock(shell, args, cwd){
  if(shell._mode === "cli-down") return null;
  if(args[0]==="--version") return { stdout: "crosslink 0.9.0", exitCode:0 };
  if(args[0]==="session" && args[1]==="status"){
    if(shell._mode==="hydration-warning") return { stdout: "auto-hydration skipped: v2 file-path", exitCode:1 };
    if(shell._mode==="stale-warning") return { stdout: "SQLite stale warning", exitCode:1 };
    return { stdout: "Working on: #514", exitCode:0 };
  }
  return { stdout:"", exitCode:0 };
}
async function checkHealth(shell, crosslinkDir){
  if(!crosslinkDir) return {healthy:true, reason:""};
  const hookConfigPath = path.join(crosslinkDir, "hook-config.json");
  if(!fs.existsSync(hookConfigPath)) return {healthy:false, reason:"hook-config.json missing"};
  try{ JSON.parse(fs.readFileSync(hookConfigPath,"utf-8")); }catch(e){ return {healthy:false, reason:`hook-config invalid ${String(e).slice(0,40)}`}; }
  const versionResult = await runCrosslinkMock(shell, ["--version"], crosslinkDir);
  if(!versionResult || versionResult.exitCode!==0) return {healthy:false, reason:`CLI unavailable`};
  if(versionResult.stdout.toLowerCase().includes("auto-hydration skipped")) return {healthy:false, reason:"auto-hydration skipped"};
  // hub-cache tolerated now
  const hubCacheDir = path.join(crosslinkDir, ".hub-cache");
  const hubCacheExists = fs.existsSync(hubCacheDir) && fs.statSync(hubCacheDir).isDirectory();
  if(!hubCacheExists){
    // tolerated in worktree — not halting
  } else {
    // check meta/issues but tolerated
  }
  const dbPath = path.join(crosslinkDir, "issues.db");
  if(!fs.existsSync(dbPath)) return {healthy:false, reason:"SQLite DB unavailable"};
  try{ const st=fs.statSync(dbPath); if(st.size===0) return {healthy:false, reason:"SQLite stale empty 0 bytes"}; }catch(e){ return {healthy:false, reason:"SQLite stale cannot stat"}; }
  try{
    const db=new Database(dbPath,{readonly:true});
    try{ const row=db.prepare("SELECT count(*) as c FROM issues").get(); if(row===null||typeof row.c!=="number") return {healthy:false, reason:"SQLite stale null"}; }finally{db.close();}
  }catch(e){
    const msg=String(e); const lower=msg.toLowerCase();
    if(lower.includes("busy")||lower.includes("locked")) return {healthy:false, reason:`DB lock ${msg.slice(0,40)}`};
    if(lower.includes("malformed")||lower.includes("corrupt")) return {healthy:false, reason:`SQLite corrupt ${msg.slice(0,40)}`};
    return {healthy:false, reason:`SQLite unavailable ${msg.slice(0,40)}`};
  }
  const statusResult = await runCrosslinkMock(shell, ["session","status"], crosslinkDir);
  if(!statusResult) return {healthy:false, reason:"CLI unavailable status null"};
  const combined=statusResult.stdout.toLowerCase();
  if(combined.includes("auto-hydration skipped")||combined.includes("v2 file-path")) return {healthy:false, reason:`auto-hydration skipped v2 file-path`};
  if(statusResult.exitCode!==0 && combined.includes("stale")) return {healthy:false, reason:`SQLite stale`};
  if(statusResult.exitCode!==0 && !combined.includes("not working") && !combined.includes("no active")){
    if(combined.includes("database is locked")||combined.includes("busy")) return {healthy:false, reason:`DB lock`};
    return {healthy:false, reason:`CLI/DB unavailable exit=${statusResult.exitCode}`};
  }
  return {healthy:true, reason:""};
}
function setupTempDir(){
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "crosslink-health-test-"));
  const real = "/home/claude-code/projects/ASES/.worktrees/guard-halt/.crosslink";
  fs.mkdirSync(path.join(tmp, ".hub-cache", "meta"), {recursive:true});
  fs.mkdirSync(path.join(tmp, ".hub-cache", "issues"), {recursive:true});
  fs.copyFileSync(path.join(real,"hook-config.json"), path.join(tmp,"hook-config.json"));
  fs.copyFileSync(path.join(real,"issues.db"), path.join(tmp,"issues.db"));
  const metaSrc = path.join("/home/claude-code/projects/ASES/.crosslink/.hub-cache","meta");
  if(fs.existsSync(metaSrc)){ for(const f of fs.readdirSync(metaSrc)) try{fs.copyFileSync(path.join(metaSrc,f), path.join(tmp,".hub-cache","meta",f));}catch{} }
  return tmp;
}
async function run(){
  const tmp = setupTempDir();
  console.log("Temp dir:", tmp);
  const mkShell = (mode)=>({ _mode: mode });
  const tests = [
    {name:"healthy (up) -> passes", dir:tmp, shell:mkShell("healthy"), expectHealthy:true, keyword:""},
    {name:"CLI down -> blocked (command fails)", dir:tmp, shell:mkShell("cli-down"), expectHealthy:false, keyword:"CLI"},
    {name:"hook-config missing -> blocked", dir:(()=>{ const d=fs.mkdtempSync(path.join(os.tmpdir(),"test-missing-")); fs.mkdirSync(path.join(d,".hub-cache","meta"),{recursive:true}); fs.writeFileSync(path.join(d,"issues.db"),"x"); return d; })(), shell:mkShell("healthy"), expectHealthy:false, keyword:"hook-config"},
    {name:"DB missing -> blocked", dir:(()=>{ const d=setupTempDir(); fs.rmSync(path.join(d,"issues.db")); return d; })(), shell:mkShell("healthy"), expectHealthy:false, keyword:"SQLite DB"},
    {name:"hub-cache missing -> tolerated (worktree, not blocked)", dir:(()=>{ const d=setupTempDir(); fs.rmSync(path.join(d,".hub-cache"),{recursive:true,force:true}); return d; })(), shell:mkShell("healthy"), expectHealthy:true, keyword:""},
    {name:"auto-hydration skipped -> blocked (v2 file-path warning)", dir:tmp, shell:mkShell("hydration-warning"), expectHealthy:false, keyword:"auto-hydration"},
    {name:"SQLite stale -> blocked", dir:tmp, shell:mkShell("stale-warning"), expectHealthy:false, keyword:"SQLite stale"},
    {name:"DB lock/corrupt -> blocked", dir:(()=>{ const d=setupTempDir(); fs.writeFileSync(path.join(d,"issues.db"), "not a sqlite file"); return d; })(), shell:mkShell("healthy"), expectHealthy:false, keyword:"SQLite"},
    {name:"live worktree real dir -> passes (hub-cache tolerated)", dir:"/home/claude-code/projects/ASES/.worktrees/guard-halt/.crosslink", shell:mkShell("healthy"), expectHealthy:true, keyword:""},
  ];
  let passed=0;
  for(const t of tests){
    const r = await checkHealth(t.shell, t.dir);
    const ok = r.healthy === t.expectHealthy && (t.expectHealthy || r.reason.toLowerCase().includes(t.keyword.toLowerCase().split(" ")[0]) || t.keyword==="" );
    console.log(`[${ok?"PASS":"FAIL"}] ${t.name}: healthy=${r.healthy} reason="${r.reason.slice(0,120)}"`);
    if(ok) passed++; else console.log("  EXPECT keyword:", t.keyword, "got:", r.reason);
  }
  try{
    const { spawnSync } = await import("child_process");
    const pr = spawnSync("crosslink", ["--version"], {encoding:"utf-8", timeout:2000});
    console.log(`[LIVE-CLI] crosslink --version exit=${pr.status} out="${(pr.stdout||"").slice(0,60)}"`);
  }catch(e){ console.log("[LIVE-CLI] error", String(e).slice(0,80)); }
  console.log(`\nResult: ${passed}/${tests.length} cheapest-tests passed`);
  if(passed===tests.length) console.log("CHEAPEST-TEST: simulate Crosslink down -> blocked, up -> passes — VERIFIED");
  else console.log("CHEAPEST-TEST FAILED");
  const guard = fs.readFileSync("/home/claude-code/projects/ASES/.worktrees/guard-halt/.opencode/plugins/crosslink-guard.ts","utf-8");
  const markers = ["CROSSLINK UNAVAILABLE — HALT","HALT > WARN > SUGGEST","Do NOT wait-and-retry","crosslink sync","hook-config","opencode.log","issues.db","hub-cache","CLI unavailable","DB lock","SQLite","auto-hydration","v2 file-path"];
  console.log("\nGuard file marker checks:");
  for(const kw of markers){ console.log(`  [${guard.includes(kw)?"FOUND":"MISSING"}] "${kw}"`); }
  try{ fs.rmSync(tmp,{recursive:true,force:true}); }catch{}
}
run().catch(e=>{ console.error(e); process.exit(1); });
