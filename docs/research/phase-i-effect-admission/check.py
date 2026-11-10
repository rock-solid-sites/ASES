#!/usr/bin/env python3
"""Independent assertions over preserved native process, database and HTTP frames."""
import hashlib
import copy
import json
from pathlib import Path
import sys


class EvidenceError(ValueError):
    pass


def need(value, reason):
    if not value:
        raise EvidenceError(reason)


def unhex(entry):
    need(entry and entry.get("exists") is True, "missing captured bytes")
    raw = bytes.fromhex(entry["raw_hex"])
    need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "captured byte digest")
    need(len(raw) == entry["size"], "captured byte size")
    return raw


def tree_bytes(tree, path):
    entry = tree.get(path)
    need(entry is not None, "missing tree path " + path)
    raw = bytes.fromhex(entry["raw_hex"])
    need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "tree digest " + path)
    need(len(raw) == entry["size"], "tree size " + path)
    return raw


def source_generation(value):
    entry = value["files"]["store.sqlite"]
    raw = tree_bytes(value["files"], "store.sqlite")
    need(value["database_identity"] == [entry["dev"], entry["ino"]],
         "F1 source database identity does not match captured file")
    need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "F1 source generation bytes mismatch")
    need(value["state"]["integrity"] == "ok", "F1 source generation integrity check")


def journal(case):
    raw = unhex(case["local"])
    rows = [json.loads(line) for line in raw.splitlines()]
    need([row["event"] for row in rows[:3]] == ["managed_created", "managed_granted", "managed_activated"],
         "native F4 management prefix")
    effects = [row for row in rows if row.get("event") == "effect_accepted"]
    for row in effects:
        payload = json.loads(row["payload"])
        need(row["request_id"] == payload["request_id"], "request ID is not bound")
        need(hashlib.sha256(row["payload"].encode()).hexdigest() == row["payload_sha256"], "effect payload digest")
        need(row["accepted_under_version"] == row["presented_version"] == 1, "F4 flat authority version")
    return rows, effects


def source_rights(tree):
    current = tree_bytes(tree, "protected/CURRENT").decode().strip()
    record = json.loads(tree_bytes(tree, "protected/" + current))
    units = record["work_units"]
    current_unit, rights, enabled, seen = "D", {"read", "write"}, True, set()
    while current_unit is not None:
        need(current_unit in units and current_unit not in seen, "invalid L5 ancestry")
        seen.add(current_unit)
        unit = units[current_unit]
        enabled = enabled and unit["active"] and not unit["sealed"]
        rights &= set(unit["grants"])
        if "latent_ceiling" in unit:
            rights &= set(unit["latent_ceiling"])
        current_unit = unit["parent"]
    return bool(enabled and record["current_ingress"] == "W-L5" and "write" in rights), record


def check(raw):
    cases = raw["cases"]
    need(raw["execution"] == "PASS", "probe did not complete")
    result = {}

    allowed = cases["allowed"]
    rows, effects = journal(allowed)
    need(allowed["response"]["status"] == 201 and len(effects) == 1, "authorized effect did not publish")
    source_allowed, _ = source_rights(allowed["before"]["l5"])
    need(source_allowed, "authorized L5 fixture was not currently writable")
    need(allowed["witness"]["body"]["current"]["journal_sha256"] == allowed["local"]["sha256"],
         "authorized journal not published")
    result["allowed"] = dict(http=201, effects=len(effects), published=True)

    denied = cases["moved-attenuated"]
    _, effects = journal(denied)
    source_allowed, denied_l5 = source_rights(denied["before"]["l5"])
    need(not source_allowed and denied["response"]["status"] == 409 and not effects, "denied descendant was admitted")
    need(denied["before"] and denied["response"]["status"] == 409, "denial frame missing")
    pre = denied["before"]["l5"]
    selected = tree_bytes(pre, "protected/CURRENT").decode().strip()
    state = json.loads(tree_bytes(pre, "protected/" + selected))
    need(state["work_units"]["C"]["parent"] == "Q", "L5 move was not selected")
    need(denied["local"]["raw_hex"] == denied["journal_before"]["raw_hex"],
         "denied journal did not remain unchanged")
    result["moved-attenuated"] = dict(http=409, descendant_write=False, effects=0)

    for label in ("wrong-pair-world", "wrong-pair-subject", "wrong-epoch", "wrong-subject",
                  "l6-disposed-removed", "l6-unknown-material", "root-retarget", "l6-remove-interleaved"):
        case = cases[label]
        rows, effects = journal(case)
        need(case["response"]["status"] == 409 and not effects, label + " did not fail closed")
        need(case["local"]["raw_hex"] == case["journal_before"]["raw_hex"], label + " altered F4 bytes")
        result[label] = dict(http=409, effects=0)
    alternate = cases["wrong-pair-world"]
    need(alternate["envelope"]["pair"]["accepted_content"] == cases["allowed"]["envelope"]["pair"]["accepted_content"],
         "alternate opaque-world control changed accepted bytes")
    need(alternate["envelope"]["pair"] != cases["allowed"]["envelope"]["pair"],
         "alternate opaque-world control not distinct")
    removed = cases["l6-disposed-removed"]["l6_change"]
    need(removed["dispose"]["reply"]["result"] == removed["remove"]["reply"]["result"] == "COMMITTED"
         and removed["remove"]["snapshot"]["live"] is False
         and removed["remove"]["snapshot"]["objects_directory_exists"] is False,
         "pre-request L6 disposal/removal did not complete")
    removed_during = cases["l6-remove-interleaved"]["interleaved_l6"]
    need(removed_during["dispose"]["reply"]["result"] == removed_during["remove"]["reply"]["result"] == "COMMITTED"
         and removed_during["remove"]["snapshot"]["live"] is False,
         "interleaved native L6 removal did not complete")

    stale = cases["stale-generation"]
    _, effects = journal(stale)
    need(stale["response"]["status"] == 409 and not effects, "stale L5 generation accepted")
    old_allowed, old_state = source_rights(stale["before"]["l5"])
    new_allowed, new_state = source_rights(stale["after"]["l5"])
    need(not old_allowed and new_allowed and old_state["current_ingress"] is None
         and new_state["work_units"]["C"]["parent"] == "Q", "stale case lacks sealed-to-active generation transition")
    need(stale["interleaved_l5"]["move"]["result"]["reply"]["result"] == "COMMITTED"
         and stale["interleaved_l5"]["activation"]["result"]["reply"]["result"] == "COMMITTED",
         "native L5 interleaving did not complete")
    result["stale-generation"] = dict(http=409, old_selector_was_sealed=True,
                                      current_authority_after_transition=True, effects=0,
                                      limitation="does not demonstrate revocation of formerly enabled authority")

    opaque = cases["f1-opaque-reaccept"]
    _, effects = journal(opaque)
    transition = opaque["native_f1_transition"]
    old_generation, new_generation = transition["before"], transition["after"]
    source_generation(old_generation)
    source_generation(new_generation)
    op = transition["operation"]["response"]["response"]
    need(op.get("outcome") == "commit", "native F1 same-byte opaque reaccept did not commit")
    need(old_generation["state"]["pair"]["accepted_content"] ==
         new_generation["state"]["pair"]["accepted_content"], "opaque reaccept changed accepted bytes")
    need(old_generation["state"]["pair"] != new_generation["state"]["pair"],
         "opaque reaccept did not change evidence world")
    need(new_generation["state"]["pair"] != opaque["envelope"]["pair"]
         and new_generation["files"]["store.sqlite"]["sha256"] !=
         old_generation["files"]["store.sqlite"]["sha256"],
         "native source generation did not advance to the new evidence world")
    need(opaque["response"]["status"] == 409 and not effects
         and opaque["local"]["raw_hex"] == opaque["journal_before"]["raw_hex"],
         "stale opaque-world request was not denied without append")
    result["f1-opaque-reaccept"] = dict(native_accept=True, same_bytes=True, opaque_world_changed=True,
                                        old_request_http=409, effects=0, source_generation_advanced=True)

    neighbor = cases["missing-bundle-neighbor"]
    _, effects = journal(neighbor)
    transition = neighbor["native_f1_transition"]
    old_generation, new_generation = transition["before"], transition["after"]
    source_generation(old_generation)
    source_generation(new_generation)
    op = transition["operation"]["response"]["response"]
    need(op.get("outcome") == "deny", "changed-content F1 accept without bundle was not denied")
    need(old_generation["state"]["pair"] == new_generation["state"]["pair"]
         and old_generation["files"]["store.sqlite"]["sha256"] ==
         new_generation["files"]["store.sqlite"]["sha256"],
         "missing-bundle denial changed the F1 accepted generation")
    need(neighbor["response"]["status"] == 201 and len(effects) == 1,
         "still-current paired F1 state did not admit authorized F4 neighbor")
    need(neighbor["envelope"]["pair"] == new_generation["state"]["pair"],
         "authorized neighbor was not bound to the preserved accepted pair")
    result["missing-bundle-neighbor"] = dict(changed_content_accept=False, old_pair_preserved=True,
                                             authorized_neighbor_http=201, effects=1)

    gated = cases["guarded-writers"]
    rows, effects = journal(gated)
    attempts = gated["writer_attempts"]
    need("locked" in attempts["f1"].lower() and "locked" in attempts["l6"].lower(), "SQLite writers were not excluded")
    need(gated["l5_contender"]["returncode"] == 75 and "REFUSED" in gated["l5_contender"]["stdout"],
         "cooperative L5 contender was not refused")
    need(gated["response"]["status"] == 201 and len(effects) == 1, "guarded work did not resume")
    result["guarded-writers"] = dict(f1="locked", l6="locked", l5="refused", resumed_http=201)

    before_kill = cases["kill-before-append"]
    rows, effects = journal(before_kill)
    need(before_kill["response"] is None and len(effects) == 0 and len(rows) == 3,
         "pre-append kill left an effect")
    need(before_kill["sink_process"]["exit"] == -9, "pre-append process was not SIGKILLed")
    need(before_kill["cold"].get("startup_error") is None, "pre-append cold recovery failed")
    result["kill-before-append"] = dict(effects=0, cold_started=True)

    after_kill = cases["kill-after-append"]
    rows, effects = journal(after_kill)
    need(after_kill["response"] is None and len(effects) == 1, "post-append kill did not preserve local effect")
    need(after_kill["sink_process"]["exit"] == -9, "post-append process was not SIGKILLed")
    need(after_kill["witness"]["body"]["current"]["journal_sha256"] != after_kill["local"]["sha256"],
         "post-append witness unexpectedly advanced")
    cold = after_kill["cold"]
    need(cold.get("startup_error") is not None or cold.get("ready", {}).get("ready") is False,
         "cold F4 did not refuse unpublished local effect")
    result["kill-after-append"] = dict(effects=1, reply=None, witness_published=False, cold_refused=True)

    after_append_eof = cases["after-append-eof"]
    rows, effects = journal(after_append_eof)
    response = after_append_eof["response"]
    need(len(effects) == 1 and response["status"] == 503,
         "after-append EOF did not report an uncertain 503 with local effect")
    need(response["body"].get("local_control_committed") is not False
         and "recovery" in response["body"].get("error", "").lower(),
         "after-append EOF was mislabeled as a no-effect denial")
    result["after-append-eof"] = dict(http=503, effects=1, uncertain=True,
                                      local_control_committed=response["body"].get("local_control_committed"))

    lost = cases["lost-receipt"]
    rows, effects = journal(lost)
    need(lost["response"]["status"] == 503 and len(effects) == 1, "lost receipt not distinguished from no effect")
    need(lost["witness"]["body"]["current"]["journal_sha256"] == lost["local"]["sha256"],
         "lost-receipt publication not observed")
    need(lost["cold_after_receipt_loss"]["ready"].get("ready") is True,
         "cold recovery did not accept the already-published cut")
    result["lost-receipt"] = dict(http=503, local_effects=1, remotely_published=True, cold_recovered=True,
                                  deduplication="not tested")

    audit = cases["audit-route"]
    _, effects = journal(audit)
    need(audit["response"]["status"] == 409 and not effects, "separate obligation route was accepted")
    result["audit-route"] = dict(http=409, effects=0)
    return dict(cases=result, conclusion="BOUNDED_NATIVE_COMMIT_POINT_OBSERVATIONS", scope=
                "test-only import binding; cooperative native writers; selected histories only")


def qualify(raw):
    controls = []
    mutations = (
        ("denied-case-forged-success", lambda r: r["cases"]["moved-attenuated"]["response"].update(status=201)),
        ("lost-receipt-witness-cut-mismatch", lambda r: r["cases"]["lost-receipt"]["witness"]["body"]["current"].update(journal_sha256="0" * 64)),
        ("same-byte-opaque-world-made-identical", lambda r: r["cases"]["wrong-pair-world"]["envelope"].update(
            pair=copy.deepcopy(r["cases"]["allowed"]["envelope"]["pair"]))),
    )
    for name, mutate in mutations:
        altered = copy.deepcopy(raw)
        mutate(altered)
        try:
            check(altered)
        except EvidenceError:
            controls.append(dict(name=name, rejected=True))
        else:
            raise EvidenceError("checker accepted altered raw control: " + name)
    return controls


def main():
    raw = json.loads(Path(sys.argv[1]).read_text())
    result = check(raw)
    result["checker_controls"] = qualify(raw)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
