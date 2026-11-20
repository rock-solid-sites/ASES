#!/usr/bin/env python3
"""Synthetic 2x3 task-context packet comparison; no model or external calls."""
from pathlib import Path
import copy
import json

HERE = Path(__file__).resolve().parent
METHODS = ("manual", "structured", "graph")
TASK_NAMES = (("docs", "task:docs"), ("review", "task:review"))
AUTHORITIES = {"canonical-fixture", "project-fixture", "observation-fixture", "experimental-fixture"}


class InvalidGraph(ValueError):
    pass


def fixture():
    return json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def unique_map(records, kind):
    items = {}
    for record in records:
        key = record.get("id")
        if not isinstance(key, str) or not key or key in items:
            raise InvalidGraph("invalid or duplicate " + kind + " identity")
        items[key] = record
    return items


def resolve(graph, task_id):
    """Test-only resolution of applicable rules, decisions and evidence."""
    sources = unique_map(graph["sources"], "source")
    tasks = unique_map(graph["tasks"], "task")
    rules = unique_map(graph["rules"], "rule")
    decisions = unique_map(graph["decisions"], "decision")
    evidence = unique_map(graph["evidence"], "evidence")
    if task_id not in tasks:
        raise InvalidGraph("unknown task")
    task = tasks[task_id]
    if task["model_launch"] != "none" or task["fallback"] != "none":
        raise InvalidGraph("unauthorized route for non-model fixture")
    if not task.get("output") or not task.get("destination"):
        raise InvalidGraph("missing output/destination")
    for source in sources.values():
        if not source.get("revision") or source.get("authority") not in AUTHORITIES:
            raise InvalidGraph("invalid source revision or authority")

    def source_ref(source_id):
        if source_id not in sources:
            raise InvalidGraph("dangling source reference")
        source = sources[source_id]
        return source_id + "@" + source["revision"]

    # Validate all graph relationships, even those not selected for this task.
    for rule in rules.values():
        source_ref(rule["source"])
        if any(t not in tasks for t in rule["applies_to"]):
            raise InvalidGraph("dangling rule scope")
    for ev in evidence.values():
        source_ref(ev["source"])
        if any(t not in tasks for t in ev["applies_to"]):
            raise InvalidGraph("dangling evidence scope")
    for decision in decisions.values():
        source_ref(decision["source"])
        if decision["target_rule"] not in rules or decision["scope_task"] not in tasks:
            raise InvalidGraph("dangling decision")
        if decision.get("status") != "approved-fixture" or not decision.get("authorized_by"):
            raise InvalidGraph("unapproved decision")
        if decision.get("type") != "override" or not decision.get("replacement_text"):
            raise InvalidGraph("invalid override decision")
        if sources[decision["source"]]["authority"] != "project-fixture":
            raise InvalidGraph("override lacks project ownership")

    selected = sorted((r for r in rules.values() if task_id in r["applies_to"]), key=lambda r: r["id"])
    overrides = {}
    for decision in decisions.values():
        if decision["scope_task"] != task_id:
            continue
        target = decision["target_rule"]
        if target in overrides:
            raise InvalidGraph("conflicting overrides")
        overrides[target] = decision
    if any(target not in {r["id"] for r in selected} for target in overrides):
        raise InvalidGraph("override not applicable to selected task")

    effective_rules, refs = [], set()
    for rule in selected:
        ref = source_ref(rule["source"])
        refs.add(ref)
        authority = sources[rule["source"]]["authority"]
        if authority not in ("canonical-fixture", "project-fixture"):
            raise InvalidGraph("experimental/observational material promoted to rule")
        override = overrides.get(rule["id"])
        if override:
            refs.add(source_ref(override["source"]))
        effective_rules.append({
            "id": rule["id"], "source": ref,
            "text": override["replacement_text"] if override else rule["text"],
            "overridden_by": override["id"] if override else None,
            "replacement_source": source_ref(override["source"]) if override else None,
            "authorized_by": override["authorized_by"] if override else None,
        })

    selected_evidence = []
    for ev in sorted(evidence.values(), key=lambda e: e["id"]):
        if task_id not in ev["applies_to"]:
            continue
        ref = source_ref(ev["source"])
        refs.add(ref)
        if not ev.get("certainty") or not ev.get("what_not_tested"):
            raise InvalidGraph("missing uncertainty disclosure")
        selected_evidence.append({
            "id": ev["id"], "source": ref,
            "claim": ev["claim"], "certainty": ev["certainty"],
            "what_not_tested": ev["what_not_tested"],
        })
    return {"task": task, "rules": effective_rules, "evidence": selected_evidence,
            "decision_ids": sorted(d["id"] for d in overrides.values()),
            "source_refs": sorted(refs)}


def render_graph(view):
    t = view["task"]
    lines = ["Task " + t["id"] + ": " + t["goal"], "",
             "Output: " + t["output"], "Durable result: " + t["destination"], "",
             "Applicable rules:"]
    for r in view["rules"]:
        lines.append("- " + r["id"] + " | " + r["source"])
        if r["overridden_by"]:
            lines.append("  Replaced by " + r["overridden_by"] + " | "
                         + r["replacement_source"] + " | authorized_by=" + r["authorized_by"])
        lines.append("  " + r["text"])
    lines.append("")
    lines.append("Evidence:")
    for ev in view["evidence"]:
        lines.append("- " + ev["id"] + " | " + ev["source"] + " | certainty=" + ev["certainty"])
        lines.append("  " + ev["claim"])
        lines.append("  WHAT-NOT-TESTED: " + ev["what_not_tested"])
    lines.extend(["", "Resolution receipt: " + ", ".join(view["source_refs"]),
                  "MODEL_LAUNCH=" + t["model_launch"],
                  "FALLBACK=" + t["fallback"], ""])
    return "\n".join(lines)


def packet(method, name, graph):
    if method == "graph":
        return render_graph(resolve(graph, "task:" + name))
    return (HERE / "packets" / (method + "-" + name + ".md")).read_text(encoding="utf-8")


def evaluate(body, task_id, graph):
    """Observable exact-string checks only; NOT semantic correctness or model behavior."""
    view = resolve(graph, task_id)
    expected = graph["expected"][task_id]
    rules = [r["id"] for r in view["rules"]]
    evs = [e["id"] for e in view["evidence"]]
    if (rules != expected["rule_ids"] or evs != expected["evidence_ids"]
            or view["decision_ids"] != expected["decision_ids"]
            or view["source_refs"] != expected["source_refs"]):
        raise InvalidGraph("fixture ground truth disagrees with resolution")

    needed = [task_id, view["task"]["output"], view["task"]["destination"],
              "MODEL_LAUNCH=none", "FALLBACK=none"]
    for r in view["rules"]:
        needed.extend((r["id"], r["source"], r["text"]))
        if r["overridden_by"]:
            needed.extend((r["overridden_by"], r["replacement_source"], r["authorized_by"]))
    for ev in view["evidence"]:
        needed.extend((ev["id"], ev["source"], ev["claim"],
                       ev["certainty"], ev["what_not_tested"]))
    missing = sorted({m for m in needed if m not in body})
    all_source_refs = {s["id"] + "@" + s["revision"] for s in graph["sources"]}
    unexpected_refs = sorted(ref for ref in all_source_refs - set(view["source_refs"])
                             if ref in body)
    selected_rule_ids = set(rules)
    allowed_texts = {r["text"] for r in view["rules"]}
    forbidden = sorted({r["text"] for r in graph["rules"]
                        if r["id"] not in selected_rule_ids or r["text"] not in allowed_texts
                        if r["text"] in body})
    forbidden += sorted({e["claim"] for e in graph["evidence"]
                         if e["id"] not in evs and e["claim"] in body})
    return {
        "ok": not missing and not forbidden and not unexpected_refs,
        "required_present": len(set(needed)) - len(missing),
        "required_total": len(set(needed)),
        "missing": missing,
        "forbidden": forbidden,
        "unrelated_source_refs": unexpected_refs,
        "bytes": len(body.encode("utf-8")),
        "lines": len(body.splitlines()),
        "source_refs": view["source_refs"],
    }


def run():
    graph = fixture()
    rows = []
    for name, task in TASK_NAMES:
        for method in METHODS:
            body = packet(method, name, graph)
            result = evaluate(body, task, graph)
            rows.append({"task": task, "format": method, **result})
    return rows


if __name__ == "__main__":
    rows = run()
    print(json.dumps({"notice": "Synthetic exact-string checks, not model performance.",
                      "rows": rows}, indent=2))
    if not all(r["ok"] for r in rows):
        raise SystemExit(1)
