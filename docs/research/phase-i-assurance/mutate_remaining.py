"""Adversarial semantic mutation audit for four additional Phase I checkers.

Every mutation starts from a previously accepted raw case and must change its
checker verdict to VIOLATION or INCOMPLETE. This audits sensitivity only.
"""
import argparse, copy, importlib.util, json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--case",required=True,choices=("l5","l6","cut","receipt"))
p.add_argument("--source",type=Path,required=True)
a=p.parse_args()
root=a.source.resolve()
spec=importlib.util.spec_from_file_location("audited_checker",root/"check.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
raw=json.loads((root/"raw.json").read_text())
checks=[]

def audit(name,case,change,accepted="SUPPORTED"):
    base=raw["cases"][case]
    actual=module.check(base)["status"]
    assert actual==accepted,(name,"baseline",actual)
    mutated=copy.deepcopy(base)
    change(mutated)
    verdict=module.check(mutated)["status"]
    assert verdict in ("VIOLATION","INCOMPLETE"),(name,"mutant escaped",verdict)
    checks.append({"name":name,"baseline":actual,"mutant":verdict,"detected":True})

if a.case=="l5":
    cases=raw["cases"];assert "after_selector" in cases
    audit("missing-post-process-state","after_selector",lambda c:c.pop("after_process"))
    audit("cold-state-divergence","after_selector",lambda c:c["cold_ready"]["frame"]["snapshot"].update(selected="invalid-record"))
    audit("permission-escalation","after_selector",lambda c:c["after_process"]["permissions"].update(D=["read","write"]))
    audit("lost-accepted-content","after_selector",lambda c:c["after_process"]["contents"].clear())
    audit("wrong-postmove-parent","after_selector",lambda c:c["after_process"]["state"]["work_units"]["C"].update(parent="P"))
    audit("unauthorized-write-allowed","after_selector",lambda c:c["write"]["frame"]["result"]["reply"].update(allowed=True))
elif a.case=="l6":
    audit("missing-creator-attempt","guarded",lambda c:c.pop("creator_attempt"))
    audit("sqlite-busy-replaced","guarded",lambda c:c["creator_attempt"]["frame"]["reply"].update(sqlite_errorcode=0))
    audit("guard-not-held","guarded",lambda c:c["gate"]["frame"].update(in_transaction=False))
    audit("creator-accepted-under-guard","guarded",lambda c:c["creator_attempt"]["frame"]["reply"].update(result="COMMITTED"))
    audit("removed-unit-still-live","guarded",lambda c:c["final_before_exit"].update(live=True))
    audit("creator-first-removal-allowed","creator-first",lambda c:c["removal"]["frame"]["reply"].update(result="COMMITTED"))
elif a.case=="cut":
    audit("missing-success-receipt","positive",lambda c:next(s for s in c["original"]["steps"] if s["label"]=="cut-x").pop("response"))
    audit("missing-startup-refusal","rollback",lambda c:c.pop("startup_refusal"))
    audit("forged-published-hash","positive",lambda c:c["witness_after_ack"]["current"].update(journal_sha256="0"*64))
    audit("rollback-accepted-on-startup","rollback",lambda c:c["startup_refusal"]["frame"].update(ready=True))
    audit("witness-not-live","positive",lambda c:c.update(witness_alive=False))
    audit("unacknowledged-commit-hidden","rejected_publication",lambda c:next(s for s in c["original"]["steps"] if s["label"]=="local-unACKed-z")["response"]["body"].update(local_control_committed=False))
else:
    audit("missing-witness","lost",lambda c:c.pop("witness_after_z"))
    audit("witness-revision-not-advanced","lost",lambda c:c["witness_after_z"].update(revision=c["witness_before"]["revision"]))
    audit("missing-transport-error","lost",lambda c:next(s for s in c["original"]["steps"] if s["label"]=="receipt-z")["observed"]["cut_protocol_log"][-1].pop("error"))
    audit("lost-receipt-falsely-acknowledged","lost",lambda c:next(s for s in c["original"]["steps"] if s["label"]=="receipt-z")["response"].update(status=201))
    audit("remote-update-missing","lost",lambda c:c["witness_after_z"].update(current=c["witness_before"]["current"]))
    audit("lost-local-commit","lost",lambda c:c["after_z"].update(raw_hex=""))
print(json.dumps({"case":a.case,"count":len(checks),"checks":checks,"independent_oracle":False},indent=2))
