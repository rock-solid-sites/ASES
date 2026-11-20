"""Run a tiny mutation qualification campaign against specific high-risk guards.

Original suite must pass separately. Mutation is a targeted test-sensitivity
probe, not a general mutation score or proof of production correctness.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT=Path(__file__).parent
MUTANTS=[
    ("ignore_reserved_capacity",
     'return b["allowance"] - spent - b["reserved"]',
     'return b["allowance"] - spent',
     "test_control.ResourceTests.test_two_simultaneous_jobs_cannot_reserve_more_than_allowance"),
    ("ignore_free_only_launch_guard",
     'if not claims:\n            raise Rejected("NO_RESOURCE_CLAIMS")',
     'if False:\n            raise Rejected("NO_RESOURCE_CLAIMS")',
     "test_control.ResourceTests.test_empty_claims_fail_prevent_unbounded_agent_launch"),
    ("disable_overrun_freeze",
     'if used>reserved:',
     'if False and used>reserved:',
     "test_control.ResourceTests.test_longer_execution_records_real_overrun_and_freezes"),
    ("disable_quote_binding",
     'if original is None or original["account"]!=account or original["payload"]!=canonical(quote):',
     'if False:',
     "test_control.ResourceTests.test_quote_claim_tampering_rejected"),
]


def main():
    source=(ROOT/"control.py").read_text()
    evidence=[]
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp)
        shutil.copy2(ROOT/"test_control.py",folder/"test_control.py")
        for label,needle,replacement,case in MUTANTS:
            if source.count(needle)!=1:
                raise RuntimeError("mutation anchor not unique: "+label)
            (folder/"control.py").write_text(source.replace(needle,replacement))
            run=subprocess.run([sys.executable,"-m","unittest",case,"-v"],
                               cwd=folder,capture_output=True,text=True,timeout=40)
            output=run.stdout+run.stderr
            killed=run.returncode!=0 and ("FAIL:" in output or "ERROR:" in output)
            evidence.append({"id":label,"test":case,"killed":killed,
                             "returncode":run.returncode,"failure_excerpt":output[-1400:]})
        payload={"status":"PASS" if all(e["killed"] for e in evidence) else "FAIL",
                 "mutants":evidence}
        print(json.dumps(payload,indent=2))
        if payload["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":
    main()
