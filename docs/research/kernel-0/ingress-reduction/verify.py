#!/usr/bin/env python3
"""Reproduce the one bounded ingress reduction; no writes to the baseline.

Requires the same Python/Icarus/Yosys/ABC tools as direct-rtl/verify.py.
The frozen baseline rerun is separate and retained in evidence/baseline-rerun.
"""
import argparse
from collections import Counter
from dataclasses import asdict
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from preflight import witnesses
from correspondence import (model, PROFILES, SOURCES, KINDS, valid_states,
                            encode_state, encode_request, decode_request)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = HERE.parent / "direct-rtl"
FROZEN = "c03bf1c470e54f51c299cb3347c547eeeae0e5ce"
spec = importlib.util.spec_from_file_location("baseline_verify", BASELINE / "verify.py")
baseline_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline_verify)
MASK55 = (1 << 55) - 1


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def lanes(word, noise=MASK55):
    """Remove actor/authenticity from a baseline word; actor selects a lane."""
    assert word & (1 << 14)
    actor = (word >> 4) & 7
    assert actor < 5
    payload = (word & 15) | (((word >> 7) & 127) << 4)
    packed = (noise & ~(2047 << (11 * actor))) | (payload << (11 * actor))
    return 1 << actor, packed


def abstract_word(lane, payload):
    return (1 << 14) | (payload & 15) | (lane << 4) | ((payload >> 4) << 7)


def sequence_vectors(p, build, evidence):
    # Reuse all baseline sequential histories except false-authenticity inputs:
    # those no longer exist at this interface. They remain in the baseline rerun.
    original = build / (p.name + "-original-sequence.vectors")
    _, _, traces = baseline_verify.sequence_vectors(p, original)
    path = build / (p.name + "-sequence.vectors")
    records = []
    count = 0
    with path.open("w") as out:
        for line in original.read_text().splitlines():
            reset, valid, word, state, resolved, commit = [int(x, 16) for x in line.split()]
            if not reset and valid and not word & (1 << 14):
                continue
            mask, payloads = lanes(word) if valid and not reset else (0, MASK55)
            # During reset drive all lanes valid: reset still has priority.
            if reset:
                mask = 31
            out.write(f"{reset:x} {mask:02x} {payloads:014x} {state:06x} {resolved:x} {commit:x}\n")
            records.append(dict(reset=reset, lanes=mask, payloads=payloads,
                                expected_state=state, resolved=resolved, committed=commit))
            count += 1
        s = model.State()

        def cycle(mask, payloads, q=None, reset=False, label=""):
            nonlocal s, count
            before = s
            if reset:
                s, resolved, commit = model.State(), 0, 0
            elif q is not None:
                s, outcome = model.resolve(s, q, p)
                model.check_edge(before, q, s, outcome, p)
                resolved, commit = 1, int(outcome == "commit")
            else:
                resolved, commit = 0, 0
            out.write(f"{int(reset):x} {mask:02x} {payloads:014x} {encode_state(s):06x} {resolved:x} {commit:x}\n")
            records.append(dict(label=label, reset=int(reset), lanes=mask, payloads=payloads,
                                before=asdict(before), after=asdict(s),
                                resolved=resolved, committed=commit))
            count += 1

        Q = model.Request
        cycle(31, MASK55, reset=True, label="reset wins over collision")
        for q in (Q("establish"), Q("grant",target=0,value=7),
                  Q("accept",0,value=1), Q("replace",target=0,other=1)):
            cycle(*lanes(encode_request(q)), q=q, label=q.label())
        # Withdrawing source valid is loss before submission. Neither this nor
        # collision can erase accepted content or silently submit work.
        for mask in range(32):
            if mask.bit_count() != 1:
                cycle(mask, MASK55 ^ (mask << 20), label="no unique submission")
        for q in (Q("set",0,0,1), Q("resume",1,value=1),
                  Q("flip",1,0), Q("flip",1,0)):
            cycle(*lanes(encode_request(q)), q=q, label=q.label())
    dump(evidence / (p.name + "-sequences.json"), {
        "cycles": records, "baseline_trace_names": [t["name"] for t in traces],
        "omitted": "false-authenticity baseline cycles; no such caller-controlled input exists"})
    return path, count


def main():
    if not __debug__:
        raise SystemExit("Do not disable verification assertions with -O")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--build", type=Path, default=HERE / "build")
    ap.add_argument("--evidence", type=Path, default=HERE / "evidence")
    for tool in ("iverilog", "vvp", "yosys", "abc"):
        ap.add_argument("--" + tool, default="berkeley-abc" if tool == "abc" else tool)
    ap.add_argument("--ivl-base")
    args = ap.parse_args()
    build, evidence = args.build.resolve(), args.evidence.resolve()
    build.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    metrics = {"status": "INCOMPLETE", "baseline": FROZEN, "profiles": [],
               "python": platform.python_version(), "tools": {}, "commands": [],
               "scope": "fixed protected lanes; synchronous digital timing retained"}
    inputs = {p.name:digest(p) for p in sorted(HERE.iterdir()) if p.suffix in (".py", ".v")}
    dump(evidence / "results.json", metrics)

    def run(name, argv, proof_failure=False):
        start = time.monotonic()
        log = evidence / (name + ".log")
        with log.open("w") as f:
            proc = subprocess.Popen(list(map(str, argv)), stdout=f, stderr=subprocess.STDOUT)
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
        metrics["commands"].append(dict(name=name, argv=list(map(str, argv)),
            exit_code=proc.returncode, wall_seconds=round(time.monotonic()-start, 6),
            max_rss_kib=usage.ru_maxrss, expected_proof_failure=proof_failure))
        dump(evidence / "results.json", metrics)
        output = log.read_text()
        if proof_failure:
            assert proc.returncode != 0 and "proof did fail" in output, output[-3000:]
        else:
            assert proc.returncode == 0, output[-3000:]
        return output

    def yosys(name, script, proof_failure=False):
        path = evidence / (name + ".ys")
        path.write_text(script + "\n")
        return run(name, [args.yosys, "-Q", "-T", "-s", path], proof_failure)

    # Check all tracked files in the original artifact, including its evidence,
    # and governing inputs against Git; do not merely trust a branch name.
    names = ["docs/research/kernel-0/" + n for n in SOURCES]
    names += ["docs/research/kernel-0/Kernel-0-Direct-RTL-Result.md"]
    names += subprocess.check_output(["git", "ls-tree", "-r", "--name-only", FROZEN,
        "docs/research/kernel-0/direct-rtl"], cwd=ROOT, text=True).splitlines()
    manifest = {}
    for name in sorted(set(names)):
        frozen = subprocess.check_output(["git", "show", FROZEN + ":" + name], cwd=ROOT)
        assert (ROOT / name).read_bytes() == frozen, "baseline changed: " + name
        manifest[name] = digest(ROOT / name)
    dump(evidence / "source-manifest.json", dict(baseline=FROZEN, sha256=manifest))
    dump(evidence / "preflight.json", witnesses())
    print("PASS frozen artifact integrity and discriminating preflight", flush=True)

    compiler = [args.iverilog]
    if args.ivl_base:
        compiler += ["-B", args.ivl_base]
    metrics["tools"]["iverilog"] = run("iverilog-version", compiler + ["-V"]).splitlines()[0]
    metrics["tools"]["yosys"] = run("yosys-version", [args.yosys, "-V"]).strip()
    metrics["tools"]["abc"] = run("abc-version", [args.abc, "-c", "version"]).strip()
    compiler += ["-g2012"]
    fixed, formal = HERE / "fixed_ingress.v", HERE / "refinement_formal.v"
    baseline = BASELINE / "kernel0.v"
    proof_tail = ("hierarchy -top ingress_formal; proc; flatten; opt; "
                  "sat -set-def-inputs -prove ok 1 -show-inputs -show-outputs -verify")
    result = yosys("ingress-refinement", f"read_verilog {fixed} {formal}; " + proof_tail)
    assert "SUCCESS" in result
    metrics["ingress_refinement"] = "PASS all 2^60 defined raw input combinations"
    # Every mutation must fail the same universal ingress mapping, with a SAT
    # failure signature rather than a compiler/tool error.
    source = fixed.read_text()
    mutations = {
        "worker_becomes_manager": ("payload=payloads[10:0];  actor=0;", "payload=payloads[10:0];  actor=4;"),
        "old_becomes_current": ("payload=payloads[10:0];  actor=0;", "payload=payloads[10:0];  actor=1;"),
        "wrong_lane_payload": ("payload=payloads[21:11]; actor=1;", "payload=payloads[10:0]; actor=1;"),
        "collision_submits": ("default: valid=0;", "default: valid=|lane_valid;"),
        "always_idle": ("valid=1;", "valid=0;"),
    }
    for label, (old, new) in mutations.items():
        assert source.count(old) == 1
        mutant = build / (label + ".v")
        mutant.write_text(source.replace(old, new))
        yosys("mutant-" + label, f"read_verilog {mutant} {formal}; " + proof_tail, True)
        # -verify stops this Yosys version before printing the model. Run the
        # same failed proof without that exit switch to retain its assignment.
        counterexample = yosys("counterexample-" + label,
            f"read_verilog {mutant} {formal}; " + proof_tail.removesuffix(" -verify"))
        assert "model found: FAIL" in counterexample
    metrics["ingress_mutations_detected"] = list(mutations)
    print("PASS universal ingress mapping and five detected mutants", flush=True)

    catalog = tuple(model.catalog())
    encoded_catalog = {encode_request(q): q for q in catalog}
    assert len(encoded_catalog) == 148
    assert len({lanes(w) for w in encoded_catalog}) == 148
    for word in encoded_catalog:
        mask, payloads = lanes(word)
        lane = mask.bit_length() - 1
        assert abstract_word(lane, (payloads >> (11*lane)) & 2047) == word

    for p in PROFILES:
        name = p.name
        profile = dict(name=name)
        states = tuple(valid_states(p))
        words = {encode_state(s) for s in states}
        count = commits = 0
        vectors = build / (name + ".vectors")
        print(name + ": enumerating all invariant states and catalog inputs", flush=True)
        with vectors.open("w") as f:
            for s in states:
                for q in catalog:
                    successor, outcome = model.resolve(s, q, p)
                    model.check_edge(s, q, successor, outcome, p)
                    assert encode_state(successor) in words
                    mask, payloads = lanes(encode_request(q), MASK55 ^ encode_state(s))
                    f.write(f"{encode_state(s):06x} {mask:02x} {payloads:014x} {encode_state(successor):06x} {int(outcome=='commit')}\n")
                    count += 1
                    commits += outcome == "commit"
        profile.update(states=len(states), semantic_vectors=count, commit_vectors=commits,
                       vector_sha256=digest(vectors))

        def simulate(label, tb, path, top, cycles):
            exe = build / (name + "-" + label + ".vvp")
            run(name + "-" + label + "-compile", compiler +
                [f"-P{top}.COUPLED={int(p.coupled)}", f"-P{top}.EXCLUSIVE={int(p.exclusive)}",
                 "-s", top, "-o", exe, baseline, fixed, HERE / tb])
            output = run(name + "-" + label, [args.vvp, exe, "+vectors=" + str(path)])
            assert (f"cycles={cycles}" if "sequence" in label else f"vectors={cycles}") in output

        simulate("exhaustive", "exhaustive_tb.v", vectors, "ingress_exhaustive_tb", count)
        # Extra raw-data attack checks are deliberately separate from semantic
        # equivalence counts. Out-of-catalog words have baseline denial semantics.
        attack = build / (name + "-attack.vectors")
        s = model.State()
        for q in (model.Request("establish"), model.Request("grant",target=0,value=7),
                  model.Request("replace",target=0,other=1)):
            s, outcome = model.resolve(s, q, p)
            assert outcome == "commit"
        stale_commits = 0
        with attack.open("w") as f:
            for lane in range(5):
                for payload in range(2048):
                    word = abstract_word(lane, payload)
                    q = encoded_catalog.get(word)
                    successor, outcome = model.resolve(s, q, p) if q else (s, "deny")
                    if lane == 0:
                        stale_commits += outcome == "commit"
                    mask, payloads = lanes(word)
                    f.write(f"{encode_state(s):06x} {mask:02x} {payloads:014x} {encode_state(successor):06x} {int(outcome=='commit')}\n")
        assert stale_commits == 0
        simulate("attack", "exhaustive_tb.v", attack, "ingress_exhaustive_tb", 10240)
        profile["raw_lane_attack_vectors"] = 10240
        profile["stale_lane_commits_over_all_2048_payloads"] = stale_commits
        seq, cycles = sequence_vectors(p, build, evidence)
        simulate("sequence", "sequence_tb.v", seq, "ingress_sequence_tb", cycles)
        profile["sequential_cycles"] = cycles

        def configure(top):
            return f"chparam -set COUPLED {int(p.coupled)} -set EXCLUSIVE {int(p.exclusive)} {top}; "

        result = yosys(name + "-boundary", f"read_verilog {baseline} {fixed} {formal}; " +
            configure("ingress_boundary_formal") +
            "hierarchy -top ingress_boundary_formal; proc; flatten; memory; opt; "
            "sat -seq 2 -prove-skip 1 -set-def-inputs -set-init-def -prove ok 1 -verify")
        assert "SUCCESS" in result
        profile["boundary_proof"] = "PASS arbitrary defined state and all raw port inputs"
        top = "fixed_ingress_machine"
        result = yosys(name + "-synthesis-equivalence", f"read_verilog {baseline} {fixed}; " +
            configure(top) + f"hierarchy -top {top}; proc; flatten; memory; opt; design -save gold; " +
            f"synth -top {top} -flatten -noabc; abc -exe {args.abc} -g simple; clean; " +
            f"rename {top} gate; design -stash gate; design -copy-from gold -as gold {top}; " +
            "design -copy-from gate -as gate gate; equiv_make gold gate equiv; " +
            "hierarchy -top equiv; equiv_simple; equiv_induct -seq 2; equiv_status -assert")
        assert "Equivalence successfully proven!" in result
        profile["synthesis_equivalence"] = "PASS whole machine mapped-versus-RTL"
        net = build / (name + "-machine.json")
        yosys(name + "-synthesis", f"read_verilog {baseline} {fixed}; " + configure(top) +
            f"synth -top {top} -flatten -noabc; abc -exe {args.abc} -g simple; " +
            f"clean; check -assert; stat; ltp -noff; write_json {net}")
        mod = json.loads(net.read_text())["modules"][top]
        cells = Counter(c["type"] for c in mod["cells"].values())
        assert not any("latch" in c.lower() or "mem" in c.lower() for c in cells)
        assert sum(v for k,v in cells.items() if "DFF" in k) == 24
        profile["synthesis"] = dict(cell_types=dict(sorted(cells.items())),
                                    cells=sum(cells.values()), netlist_sha256=digest(net))
        profile["status"] = "PASS"
        metrics["profiles"].append(profile)
        dump(evidence / "results.json", metrics)
        print(f"PASS {name}: {count} oracle comparisons; {sum(cells.values())} cells", flush=True)

    metrics["artifact_sha256"] = {p.name:digest(p) for p in sorted(HERE.iterdir())
                                  if p.suffix in (".py", ".v")}
    assert metrics["artifact_sha256"] == inputs, "implementation/checker changed during run"
    metrics["semantic_vectors"] = sum(p["semantic_vectors"] for p in metrics["profiles"])
    metrics["status"] = "PASS"
    dump(evidence / "results.json", metrics)
    print(f"PASS ingress reduction: {metrics['semantic_vectors']} semantic comparisons", flush=True)


if __name__ == "__main__":
    main()
