#!/usr/bin/env python3
"""Reproduce bounded RTL correspondence, boundary proofs, and synthesis evidence.

Requires Linux/Python >=3.10, Icarus Verilog, Yosys and Berkeley ABC.
No network, downloads, services, or changes to the frozen semantic inputs.
"""
import argparse
from collections import Counter, deque
from dataclasses import asdict, replace
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
import time

from correspondence import (BASE, SOURCES, PROFILES, model, valid_states, requests,
                            encode_state, decode_state, encode_request, decode_request)

HERE = Path(__file__).resolve().parent


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sequence_vectors(profile, path):
    Q = model.Request
    establish = Q("establish")
    grant = Q("grant", target=0, value=7)
    traces = {
        "positive_two_replacements": [establish, grant, Q("set",0,0,1), Q("accept",0,value=1),
            Q("replace",target=0,other=1), Q("resume",1,value=1), Q("flip",1,0),
            Q("replace",target=1,other=2), Q("set",2,0,1), Q("grant",target=3,value=2),
            Q("set",3,1,1), Q("set",0,0,0), Q("set",1,0,0)],
        "write_before_replace": [establish, grant, Q("set",0,0,1), Q("replace",target=0,other=1)],
        "replace_before_write": [establish, grant, Q("replace",target=0,other=1), Q("set",0,0,1)],
        "write_before_revoke": [establish, grant, Q("set",0,0,1), Q("restrict",target=0)],
        "revoke_before_write": [establish, grant, Q("restrict",target=0), Q("set",0,0,1)],
        "reuse": [establish, grant, Q("restrict",target=0), Q("grant",target=0,value=7)],
        "delegate_cascade": [establish, grant, Q("delegate",0,3,7),
            Q("restrict",target=0,value=1), Q("set",3,1,1), Q("restrict",target=0)],
        "delegate_replace": [establish, grant, Q("delegate",0,3,7), Q("replace",target=0,other=1)],
        "amplify": [establish, Q("grant",target=0,value=1), Q("delegate",0,3,7)],
        "mixed_and_pair": [establish, grant, Q("mixed",0), Q("pair",0,value=3)],
        "forgery": [replace(establish,authentic=False), establish, grant,
            Q("set",0,0,1,authentic=False), Q("restrict",target=0,authentic=False)],
        "lost_ack_replay": [establish, grant, Q("flip",0,0), Q("flip",0,0)],
        "copied_content_after_loss": [establish, grant, Q("accept",0,value=1), None,
            Q("replace",target=0,other=1), Q("resume",1,value=0), Q("resume",1,value=1)],
        "conflicting_fields": [establish, grant, Q("grant",target=3,value=2),
            Q("set",0,0,1), Q("set",3,1,1)],
        "conflicting_fields_reverse": [establish, grant, Q("grant",target=3,value=2),
            Q("set",3,1,1), Q("set",0,0,1)],
        "exclusive_grant_reverse": [establish, Q("grant",target=3,value=2), grant],
    }
    states = {model.State()}
    recorded = []
    cycles = 0
    with path.open("w") as f:
        for name, trace in traces.items():
            s = model.State()
            f.write("1 1 7fff 000000 0 0\n")  # Reset wins over a presented request.
            cycles += 1
            steps = []
            for q in trace:
                states.add(s)
                # Absent proposal: source may disappear/change every request bit.
                f.write(f"0 0 7fff {encode_state(s):06x} 0 0\n")
                cycles += 1
                if q is None:
                    steps.append({"event":"executor loss / idle", "state":asdict(s)})
                    continue
                before = s
                s, outcome = model.resolve(s,q,profile)
                model.check_edge(before,q,s,outcome,profile)
                f.write(f"0 1 {encode_request(q):04x} {encode_state(s):06x} 1 {int(outcome=='commit')}\n")
                cycles += 1
                states.add(s)
                steps.append({"request":asdict(q), "before":asdict(before),
                              "after":asdict(s), "outcome":outcome})
            recorded.append({"name":name,"steps":steps})
    return states, cycles, recorded


def main():
    if not __debug__:
        raise SystemExit("Verification requires assertions: do not use -O")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build",type=Path,default=HERE/"build")
    ap.add_argument("--evidence",type=Path,default=HERE/"evidence")
    ap.add_argument("--iverilog",default="iverilog")
    ap.add_argument("--ivl-base",default=None,help="Only for a relocated Icarus package")
    ap.add_argument("--vvp",default="vvp")
    ap.add_argument("--yosys",default="yosys")
    ap.add_argument("--abc",default="berkeley-abc")
    args = ap.parse_args()
    build, evidence = args.build.resolve(), args.evidence.resolve()
    build.mkdir(parents=True,exist_ok=True)
    evidence.mkdir(parents=True,exist_ok=True)
    commands = []
    metrics = {"format":1,"baseline":BASE,"status":"INCOMPLETE",
               "profiles":[],"measurements":{},"tools":{},
               "host":{"system":platform.system(),"machine":platform.machine(),
                       "python":platform.python_version()}}
    dump(evidence/"results.json",metrics)  # Failed/interrupted runs cannot retain PASS.

    def run(name, argv, expected_failure=False):
        log = build/(name+".log")
        started = time.monotonic()
        with log.open("w") as out:
            proc = subprocess.Popen(list(map(str,argv)),stdout=out,stderr=subprocess.STDOUT)
            _, status, usage = os.wait4(proc.pid,0)
            proc.returncode = os.waitstatus_to_exitcode(status)
        wall = time.monotonic()-started
        metrics["measurements"][name] = {"wall_seconds":round(wall,6),
            "user_seconds":round(usage.ru_utime,6),"system_seconds":round(usage.ru_stime,6),
            "max_rss_kib":usage.ru_maxrss,"exit_code":proc.returncode}
        commands.append({"name":name,"argv":list(map(str,argv)),
                         "expected_failure":expected_failure})
        output = log.read_text()
        if (proc.returncode!=0) != expected_failure:
            raise RuntimeError(f"{name}: unexpected exit {proc.returncode}\n{output[-5000:]}")
        return output

    compiler = [args.iverilog]
    if args.ivl_base:
        compiler += ["-B",args.ivl_base]
    compiler += ["-g2012"]
    metrics["tools"]["yosys"] = run("yosys-version",[args.yosys,"-V"]).strip()
    metrics["tools"]["iverilog"] = run("iverilog-version",compiler[:len(compiler)-1]+["-V"]).splitlines()[0]
    metrics["tools"]["abc"] = run("abc-version",[args.abc,"-c","version"]).strip()
    # Verify both Git blob identity and actual working file contents at the frozen ref.
    manifest = {}
    for name in SOURCES:
        path = HERE.parent/name
        rel = str(path.relative_to(HERE.parents[3]))
        frozen = subprocess.check_output(["git","show",f"{BASE}:{rel}"],cwd=HERE)
        assert frozen == path.read_bytes(), f"source changed: {name}"
        manifest[name] = digest(path)
    dump(evidence/"source-manifest.json",{"baseline":BASE,"sha256":manifest})
    output = run("reference-model",["python3",HERE.parent/"kernel0_finite_model.py",
                                   "--output",evidence/"reference-model.json"])
    print(output.strip(),flush=True)
    catalog = requests()
    assert len({encode_request(q) for q in catalog}) == 296
    assert all(decode_request(encode_request(q)) == q for q in catalog)

    for p in PROFILES:
        name = p.name
        print(f"{name}: generating exhaustive all-invariant-state vectors",flush=True)
        started = time.monotonic()
        states = tuple(valid_states(p))
        encoded = {encode_state(s) for s in states}
        assert len(states)==len(encoded)
        assert all(decode_state(encode_state(s)) == s for s in states)
        edges, commits = 0, 0
        vectors = build/(name+".vectors")
        adjacency = {}
        with vectors.open("w") as f:
            for s in states:
                sw = encode_state(s)
                successors = set()
                for q in catalog:
                    out, outcome = model.resolve(s,q,p)
                    model.check_edge(s,q,out,outcome,p)
                    ow = encode_state(out)
                    assert ow in encoded
                    successors.add(ow)
                    f.write(f"{sw:06x} {encode_request(q):04x} {ow:06x} {int(outcome=='commit')}\n")
                    edges += 1
                    commits += outcome == "commit"
                adjacency[sw] = successors
        seen, queue = {0}, deque([0])
        while queue:
            for out in adjacency[queue.popleft()]:
                if out not in seen:
                    seen.add(out)
                    queue.append(out)
        graph = next(g for g in json.loads((evidence/"reference-model.json").read_text())["authoritative_graphs"]
                     if g["profile"]==name)
        assert len(seen)==graph["states"]
        generation = time.monotonic()-started
        profile = {"name":name,"states":len(states),"reachable_states":len(seen),
                   "unreachable_valid_states":len(states)-len(seen),"vectors":edges,
                   "commit_vectors":commits,"deny_vectors":edges-commits,
                   "catalog_templates":148,"authenticity_variants":2,
                   "vector_sha256":digest(vectors),"vector_bytes":vectors.stat().st_size,
                   "generation_seconds":round(generation,6)}
        params = [f"-Pexhaustive_tb.COUPLED={int(p.coupled)}",f"-Pexhaustive_tb.EXCLUSIVE={int(p.exclusive)}"]
        sim = build/(name+".vvp")
        run(name+"-compile",compiler+params+["-s","exhaustive_tb","-o",sim,HERE/"kernel0.v",HERE/"exhaustive_tb.v"])
        simout = run(name+"-exhaustive",[args.vvp,sim,f"+vectors={vectors}"])
        assert f"PASS exhaustive vectors={edges}" in simout
        print(simout.strip(),flush=True)

        sequence = build/(name+"-sequence.vectors")
        witness_states, cycles, traces = sequence_vectors(p,sequence)
        dump(evidence/(name+"-traces.json"),traces)
        seqsim = build/(name+"-sequence.vvp")
        seqparams = [f"-Psequence_tb.COUPLED={int(p.coupled)}",f"-Psequence_tb.EXCLUSIVE={int(p.exclusive)}"]
        run(name+"-sequence-compile",compiler+seqparams+["-s","sequence_tb","-o",seqsim,HERE/"kernel0.v",HERE/"sequence_tb.v"])
        seqout = run(name+"-sequence",[args.vvp,seqsim,f"+vectors={sequence}"])
        assert f"PASS sequential cycles={cycles}" in seqout
        profile["sequential_cycles"] = cycles

        def yosys(label, script):
            scriptfile = build/(name+"-"+label+".ys")
            scriptfile.write_text(script+"\n")
            result = run(name+"-"+label,[args.yosys,"-Q","-T","-s",scriptfile])
            (evidence/(name+"-"+label+".log")).write_text(result)
            (evidence/(name+"-"+label+".ys")).write_text(script+"\n")
            return result

        def configure(top):
            return f"chparam -set COUPLED {int(p.coupled)} -set EXCLUSIVE {int(p.exclusive)} {top}; "

        # SAT compares the ABC-mapped law to the elaborated RTL for ALL raw bit
        # inputs, a larger domain than the semantic correspondence enumeration.
        eq = yosys("synthesis-equivalence",
            f"read_verilog {HERE/'kernel0.v'}; "+configure("kernel0_step")+
            "hierarchy -top kernel0_step; proc; flatten; memory; opt; design -save gold; "
            "synth -top kernel0_step -flatten -noabc; "
            f"abc -exe {args.abc} -g simple; clean; rename kernel0_step gate; design -stash gate; "
            "design -copy-from gold -as gold kernel0_step; design -copy-from gate -as gate gate; "
            "equiv_make gold gate equiv; hierarchy -top equiv; equiv_simple; equiv_status -assert")
        assert "Equivalence successfully proven!" in eq
        boundary = yosys("boundary",
            f"read_verilog {HERE/'kernel0.v'} {HERE/'boundary_formal.v'}; "+configure("boundary_formal")+
            "hierarchy -top boundary_formal; proc; flatten; memory; opt; "
            "sat -seq 2 -prove-skip 1 -set-def-inputs -set-init-def -prove ok 1 -verify")
        assert "SUCCESS" in boundary
        net = build/(name+"-machine.json")
        yosys("synthesis",f"read_verilog {HERE/'kernel0.v'}; "+configure("kernel0_machine")+
              "synth -top kernel0_machine -flatten -noabc; "+
              f"abc -exe {args.abc} -g simple; clean; check -assert; stat; ltp -noff; write_json {net}")
        module = json.loads(net.read_text())["modules"]["kernel0_machine"]
        cells = Counter(c["type"] for c in module["cells"].values())
        assert not any("latch" in c.lower() or "mem" in c.lower() for c in cells)
        profile["synthesis"] = {"cell_types":dict(sorted(cells.items())),
                                "cells":sum(cells.values()),"netlist_sha256":digest(net)}
        profile["synthesis_equivalence"] = "PASS; all raw state/proposal bit combinations"
        profile["boundary_proof"] = "PASS; one step from arbitrary defined register state"

        # Deliberate RTL faults must be detected by the exact same comparator.
        probes = build/(name+"-mutation.vectors")
        with probes.open("w") as f:
            for s in sorted(witness_states,key=encode_state):
                for q in catalog:
                    out, outcome = model.resolve(s,q,p)
                    f.write(f"{encode_state(s):06x} {encode_request(q):04x} {encode_state(out):06x} {int(outcome=='commit')}\n")
        mutations = {
            "always_deny": ("commit=admitted && valid_state(proposed);","commit=0;"),
            "forged_authority": ("wellformed && authentic && valid_state(state_in)","wellformed && valid_state(state_in)"),
            "reuse": ("current_rights==0 && !state_in[4+target]","current_rights==0"),
            "denied_partial": ("state_out=commit ? proposed : state_in;",
                "state_out=commit ? proposed : state_in; if (op==MIXED) state_out[1]=1;"),
        }
        if p.coupled:
            mutations["coupled_invariant"]=("COUPLED && s[1] && s[2]","1'b0")
        if p.exclusive:
            mutations["exclusive_invariant"]=("EXCLUSIVE && r3!=0","1'b0 && r3!=0")
        detected = {}
        source = (HERE/"kernel0.v").read_text()
        for label,(old,new) in mutations.items():
            assert source.count(old)==1
            mutant = build/(name+"-"+label+".v")
            mutant.write_text(source.replace(old,new))
            executable = build/(name+"-"+label+".vvp")
            run(name+"-"+label+"-compile",compiler+params+["-s","exhaustive_tb","-o",executable,mutant,HERE/"exhaustive_tb.v"])
            fault = run(name+"-"+label,[args.vvp,executable,f"+vectors={probes}"],expected_failure=True)
            assert "FATAL" in fault and "expected=" in fault
            detected[label] = fault.strip()
        profile["mutations_detected"] = detected
        profile["status"] = "PASS"
        metrics["profiles"].append(profile)
        dump(evidence/"results.json",metrics)
        dump(evidence/"commands.json",commands)
        print(f"{name}: PASS states={len(states)} vectors={edges} cells={sum(cells.values())}",flush=True)

    metrics["status"] = "PASS"
    metrics["total_vectors"] = sum(p["vectors"] for p in metrics["profiles"])
    metrics["artifact_sha256"] = {p.name:digest(p) for p in sorted(HERE.iterdir())
                                  if p.suffix in (".py",".v")}
    dump(evidence/"results.json",metrics)
    dump(evidence/"commands.json",commands)
    print(f"PASS total_vectors={metrics['total_vectors']}",flush=True)


if __name__ == "__main__":
    main()
