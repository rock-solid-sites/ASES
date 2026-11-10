#!/usr/bin/env python3
"""Native unsupported-interpretation controls around actual append admission."""
import argparse
import json
from pathlib import Path
import sys
import time
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "phase-i-effect-admission"))
import probe as admission_probe

n = admission_probe.n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    out = p.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    result = dict(start_ns=time.monotonic_ns(), cases={},
                  source_hash=n.sha((HERE.parent / "phase-i-effect-admission/admission.py").read_bytes()))
    try:
        for label, schema in (("valid", 1), ("future", 2), ("string", "1"), ("boolean", True), ("missing", None)):
            case = admission_probe.setup_case(out / "state" / label, label)
            root = Path(case["root"])
            selector, state = admission_probe.n.module("profile_l5", admission_probe.L5DIR / "l5_integrated.py").load_current(root / "l5")
            if schema is None:
                state.pop("schema")
            else:
                state["schema"] = schema
            record = root / "l5/protected" / selector
            record.write_text(n.canonical(state) + "\n")
            case["envelope"]["l5"] = dict(selector=selector, sha256=n.sha(record.read_bytes()))
            observation = admission_probe.run_effect(case, out, label)
            observation["injected_selected_record"] = n.blob(record)
            result["cases"][label] = observation
        result["execution"] = "PASS"
    except BaseException:
        result["execution"] = "ERROR"
        result["error"] = traceback.format_exc()
    finally:
        for child in n.CHILDREN:
            child.close(True)
        result.update(processes=n.PROCESSES, events=n.EVENTS)
        (out / "raw.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(n.canonical(dict(execution=result["execution"], error=result.get("error"),
                           outcomes={k:v["response"]["status"] for k,v in result["cases"].items()})))
    return 0 if result["execution"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
