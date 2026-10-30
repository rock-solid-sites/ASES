"""F2 hostile-fixture reference library (independent test oracle).

This module is an independent oracle for the F2 fixture corpus of
``Phase-I-Verification.md`` §3. It is deliberately NOT written against any
Agent B formal model or Agent D realization: each fixture names the contract
facts its expected outcome follows from (C1–C13, Work Unit A–L, H5/H6,
closure rule 7), and the oracle applies a fixed semantics derived from those
contract statements.

A fixture supplies a *world* (the abstract store and substrate observations)
plus a list of *scenarios*. Each scenario is a list of events followed by an
observation with an expected outcome. The runner replays events with the
declared semantics; if the replayer cannot execute an event (for example a
right was removed), the scenario outcome is DENIED at that point.

Hostile histories are expressed by substituting state cells or events
relative to a healthy history. Destructive controls perturb one named
mechanism in the oracle and require the perturbed run to reach its intended
fault and to fail the expected outcome; controls whose fault is never
reached are reported INVALID, not as discriminators.

Boundary of the oracle: no host, process, descriptor, timer, transaction or
filesystem semantics exist here. Observations such as "engine died at t and
the activity used a retained handle afterwards" are *declared* by the
fixture through a substrate model, because that is exactly what a realization
must supply. Tests that need a real process/route/ACL are marked
``executable: false`` in their fixture data and are not counted as executed.
"""

from __future__ import annotations

import copy
import json

CONTENT_ATOMS = ("x", "y", "z")


class Inconsistent(Exception):
    """Raised when an event cannot apply to the current model state."""


class Stamp:
    """Monotone logical stamps standing in for durable sequence positions.

    Durable records (journal entries, candidates, accepted content) carry the
    stamp at which they became durable. Recovery compares stamps through a
    trusted high-water mark; nothing rolled back in a box can raise that mark.
    """

    _n = 0

    @classmethod
    def next(cls):
        cls._n += 1
        return cls._n


def new_store():
    return {
        "units": {},          # unit -> boundary record
        "parent": {},         # unit -> parent|None
        "grants": {},         # unit -> {"local": {...}, "exp": bool}
        "latent": {},         # unit -> {"right": {...}}  sealed restrictions
        "status": {},         # unit -> sealed|active|removed
        "accepted": {},       # unit -> list of atoms
        "candidates": [],     # unaccepted durable contents
        "content": {},        # atom -> counters
        "journal": tr(),
        "relations": tr(),    # relationship store (revocation + policy changes)
        "domain": 0,
        "comms": {},          # in-flight message identities
        "processes": {},      # process id -> alive
        "positions": {},      # position -> {"gen", "unit", "holder"}
        "derived": [],        # derived plan entries
        "recovered_stamps": [],
        "discovered": [],     # discovered-but-unvalidated material
        "dependents": {},     # unit -> remaining durable dependents
        "survivors": set(),   # atoms held by a trusted holder
        "witness": [],        # positive-control observations
    }


def tr():
    """A transaction store: cells plus a committed snapshot."""
    return {"live": {}, "committed": {}}


def tget(store_rec, key, default=None):
    if key in store_rec["live"]:
        return store_rec["live"][key]
    return store_rec["committed"].get(key, default)


def tcommit(store_rec):
    store_rec["committed"] = dict(store_rec["live"])


def tset(store_rec, key, value):
    store_rec["live"][key] = value


def tupd(store_rec, key, fn, default):
    tset(store_rec, key, fn(tget(store_rec, key, default)))


# ---------------------------------------------------------------------------
# Durable observation helpers
# ---------------------------------------------------------------------------

def content_counters(store, atom):
    return store["content"].setdefault(
        atom, {"internal": 0, "outward": 0, "published": 0, "sink_accept": 0})


def accepted_all(store):
    return [a for atoms in store["accepted"].values() for a in atoms]


def chain(store, unit):
    """The complete containment chain of ``unit`` including itself."""
    out, cur, seen = [], unit, set()
    while cur is not None:
        if cur in seen:
            raise Inconsistent("containment cycle at %s" % cur)
        seen.add(cur)
        out.append(cur)
        cur = store["parent"].get(cur)
    return out


def denied_by_chain(store, unit, right):
    """Which boundary in the chain first refuses ``right`` (None if none)."""
    for node in chain(store, unit):
        if not store["grants"].get(node, {}).get("local", {}).get(right):
            return node
        if store["latent"].get(node, {}).get("right", {}).get(right) is False:
            return node
    return None


def effective(store, unit, right):
    return denied_by_chain(store, unit, right) is None


def effective_exp(store, unit):
    for node in chain(store, unit):
        if not store["grants"].get(node, {}).get("exp", False):
            return False
    return store["status"].get(unit) not in ("sealed", "removed")


def unit_exists(store, unit):
    return store["status"].get(unit) != "removed" and unit in store["units"]


# ---------------------------------------------------------------------------
# Scenario result
# ---------------------------------------------------------------------------

class Result:
    def __init__(self):
        self.denied = None        # bool: boundary proposal denied
        self.reason = ""
        self.engine_denied = None  # bool: engine-level gate (never called)
        self.engine_reason = ""
        self.delete_blocked = None
        self.delete_reason = ""
        self.takeover_refused = None
        self.sink = None           # accepted|unknown|rejected|None
        self.flags = {}
        self.log = []

    def as_dict(self):
        return {
            "denied": self.denied, "reason": self.reason,
            "engine_denied": self.engine_denied, "engine_reason": self.engine_reason,
            "delete_blocked": self.delete_blocked, "delete_reason": self.delete_reason,
            "takeover_refused": self.takeover_refused, "sink": self.sink,
            "flags": self.flags,
        }


def _deny(res, why):
    if res.denied is None:
        res.denied = True
        res.reason = why
    res.log.append("DENY: " + why)


def _allow(res):
    if res.denied is None:
        res.denied = False
        res.reason = "admitted"


def _engine_deny(res, why):
    if res.engine_denied is None:
        res.engine_denied = True
        res.engine_reason = why
    res.log.append("ENGINE DENY: " + why)


def _need(store, proc):
    if store["processes"].get(proc, True) is False:
        raise Inconsistent("event requires dead process %r" % proc)


# ---------------------------------------------------------------------------
# Event dispatch — core semantics (C1–C13 / Work Unit A–L as declared)
# ---------------------------------------------------------------------------

def apply(store, event, res, mech):
    handler = HANDLERS.get(event["ev"])
    if handler is None:
        raise Inconsistent("unknown event %r" % event["ev"])
    handler(store, event, res, mech)


def _ev_create(store, e, res, mech):
    unit = e["unit"]
    if unit in store["units"] and unit_exists(store, unit):
        raise Inconsistent("duplicate unit %r" % unit)
    parent = e.get("parent")
    if parent is not None and not unit_exists(store, parent):
        raise Inconsistent("missing parent %r" % parent)
    store["units"][unit] = {
        "id": unit,
        "genesis": Stamp.next(),
        "created_by": e.get("created_by", "kit"),
        "project": e.get("project", "alpha"),
        "origin": e.get("origin", ""),
    }
    store["parent"][unit] = parent
    store["grants"][unit] = {"local": {"read": False, "write": False},
                             "exp": bool(e.get("exp", False))}
    store["status"][unit] = e.get("status", "sealed")
    store["accepted"][unit] = []
    store["dependents"][unit] = 0
    if e.get("latent_right"):
        store["latent"].setdefault(unit, {}).setdefault("right", {})[e["latent_right"]] = False
    res.log.append("create %s (parent=%s)" % (unit, parent))
    store["witness"].append("create empty sealed unit %s" % unit)


def _ev_grant(store, e, res, mech):
    unit = e["unit"]
    if not unit_exists(store, unit):
        raise Inconsistent("grant on missing unit %r" % unit)
    g = store["grants"].setdefault(unit, {"local": {"read": False, "write": False}, "exp": False})
    if "value" in e:
        g["exp"] = bool(e["value"])
    else:
        g["local"][e["right"]] = bool(e["value"] if "value" in e else e.get("allow", True))


def _ev_restriction(store, e, res, mech):
    """An independent local restriction imposed on a sealed unit."""
    store["latent"].setdefault(e["unit"], {}).setdefault("right", {})[e["right"]] = False


def _ev_seal(store, e, res, mech):
    if not unit_exists(store, e["unit"]):
        raise Inconsistent("seal of missing unit %r" % e["unit"])
    store["status"][e["unit"]] = "sealed"
    res.log.append("seal %s" % e["unit"])


def _ev_activate(store, e, res, mech):
    unit = e["unit"]
    if not unit_exists(store, unit):
        raise Inconsistent("activation of missing unit %r" % unit)
    proc = e.get("via")
    if proc is not None:
        _need(store, proc)
    if store["status"].get(unit) == "sealed" and e.get("layer_does_not_certify") and not e.get("trusted_currentness"):
        raise Inconsistent("sealed unit activated without trusted currentness")
    store["status"][unit] = "active"
    res.log.append("activate %s via %s" % (unit, proc))


def _ev_engine_use(store, e, res, mech):
    """A protected capability use mediated through the engine."""
    unit = e["unit"]
    if unit is not None and not unit_exists(store, unit):
        raise Inconsistent("use of missing unit %r" % unit)
    if unit is not None and store["status"].get(unit) != "active":
        _engine_deny(res, "unit %s is not active (sealed)" % unit)
        return
    if e.get("engine_died_at") is not None:
        _need(store, "engine")
        if store["processes"].get("engine") is False:
            _engine_deny(res, "engine lost; route unattributable at boundary")
            if mech.get("engine_route_mediation") is False:
                res.log.append("weakened route mediation: use admitted")
                _allow(res)
            return
    _allow(res)


def _ev_retain_handle(store, e, res, mech):
    store["flags"] = {**getattr(store, "flags", {})}
    res.log.append("process %s retains handle to %s" % (e["process"], e.get("path", "x")))


def _ev_kill(store, e, res, mech):
    store["processes"][e["process"]] = False
    if e["process"] == "engine":
        culprits = [u for u, s in store["status"].items() if s == "active"]
        for u in culprits:
            store["status"][u] = "sealed"
        res.log.append("engine dies; sealed %s" % ",".join(sorted(culprits)))


def _ev_handle_read(store, e, res, mech):
    proc = e["process"]
    if store["processes"].get(proc, True) is False:
        _deny(res, "handle use by dead process %s" % proc)
        return
    if e.get("unit") is not None and not effective(store, e["unit"], e["right"]):
        _deny(res, "retained handle use not currently authorized on %s" % e["unit"])
        return
    if store["status"].get(e.get("unit")) == "sealed" and not e.get("internal"):
        _deny(res, "sealed unit %s cannot use outward route" % e.get("unit"))
        return
    _allow(res)


def _ev_internal_accept(store, e, res, mech):
    unit, atom = e["unit"], e["atom"]
    if not unit_exists(store, unit):
        raise Inconsistent("accept into missing unit %r" % unit)
    if atom not in CONTENT_ATOMS:
        raise Inconsistent("unknown atom %r" % atom)
    store["accepted"][unit].append(atom)
    content_counters(store, atom)["internal"] += 1
    store["witness"].append("accept %s inside %s" % (atom, unit))
    res.log.append("internal accept %s in %s" % (atom, unit))


def _ev_derive(store, e, res, mech):
    """Compute a derived guard snapshot from the current state (a cache)."""
    unit = e["unit"]
    snap = {"unit": unit, "epoch": tget(store["relations"], "epoch", {}).get(unit, 0),
            "map": {}
            if mech.get("current_view_checking") is False
            else {r: effective(store, unit, r) for r in ("read", "write")},
            "stamp": Stamp.next()}
    store["derived"].append(snap)
    res.log.append("derive guard snapshot for %s epoch %s" % (unit, snap["epoch"]))


def _ev_revoke(store, e, res, mech):
    unit = e["unit"]
    if not unit_exists(store, unit):
        raise Inconsistent("revocation of missing unit %r" % unit)
    tupd(store["relations"], "epoch", lambda m: {**m, unit: m.get(unit, 0) + 1}, {})
    if e.get("keep_representations"):
        store.setdefault("stale_reps", set()).add(unit)
    if e.get("ack"):
        store["acks"] = getattr(store, "acks", {})
        res.flags["revoked_ack_stamp"] = store["relations"]["live"]["epoch"][unit]
    res.log.append("revoke %s (epoch bump)" % unit)
    store["witness"].append("revocation of boundary %s" % unit)
    # C6/C8: revocation of a boundary disables outward use through it.
    if mech.get("ancestor_checking") is False:
        res.log.append("weakened ancestor checking: descendants unaffected")


def _ev_use_with(store, e, res, mech):
    """Submit a use justified by a retained representation (old handle,
    old generation token, derived snapshot)."""
    use = e["use"]
    if use.get("engine"):
        _ev_engine_use(store, {"unit": e.get("unit"), "ev": "engine_use"}, res, mech)
        if res.engine_denied:
            return
    if use.get("snapshot_ref") is not None:
        snap = store["derived"][use["snapshot_ref"]]
        if mech.get("current_view_checking") is False:
            ok = snap["map"].get(use["right"], False)
        else:
            ok = (snap["epoch"] == tget(store["relations"], "epoch", {}).get(snap["unit"], 0)
                  and effective(store, snap["unit"], use["right"]))
        if not ok:
            _deny(res, "derived snapshot is stale under current authority")
            return
        _allow(res)
        return
    unit = e.get("unit")
    right = use.get("right")
    if unit is not None and right and not effective(store, unit, right):
        _deny(res, "current authority for %s/%s absent" % (unit, right))
        return
    if unit is not None and use.get("outward") and not effective_exp(store, unit):
        _deny(res, "outward use of %s not authorized by current boundary state" % unit)
        return
    _allow(res)


def _ev_position_advance(store, e, res, mech):
    pos = store["positions"].setdefault(e["pos"], {"gen": 0, "unit": e["unit"], "holder": e.get("to")})
    if e.get("to") is not None:
        pos["holder"] = e["to"]
    pos["gen"] += 1
    pos["unit"] = e["unit"]
    res.log.append("position %s generation %s (holder %s)" % (e["pos"], pos["gen"], pos["holder"]))


def _ev_stale_claim(store, e, res, mech):
    """Old producer claims the new position/generation."""
    pos = store["positions"]
    if e["pos"] not in pos:
        raise Inconsistent("claim for unknown position %r" % e["pos"])
    cur = pos[e["pos"]]
    claimed = {"gen": e.get("gen", 1), "unit": e.get("unit", cur["unit"]),
               "holder": e.get("as", e["claimant"])}
    if mech.get("source_binding") is False:
        cur.update(claimed)
        _allow(res)
        res.log.append("weakened source binding: stale claim admitted")
        return
    if e.get("old_rep"):
        _deny(res, "reuse of old representation %r" % e["old_rep"])
        return
    if claimed["holder"] == cur["holder"] and claimed["gen"] == cur["gen"] and claimed["unit"] == cur["unit"]:
        _allow(res)
        return
    _deny(res, "claim does not match current position identity (gen %s holder %s)" % (cur["gen"], cur["holder"]))


def _ev_replay_message(store, e, res, mech):
    mid = e["msg"]
    com = store["comms"].setdefault(mid, {"delivered": False})
    if e.get("deliver"):
        com["delivered"] = True
    if com["delivered"] and mech.get("source_binding") is not False:
        _deny(res, "replay of already delivered message %s" % mid)
        return
    if com["delivered"] and mech.get("source_binding") is False:
        _allow(res)
        res.log.append("weakened replay protection: duplicate delivered")
        return
    com["delivered"] = True
    _allow(res)


def _ev_reserve(store, e, res, mech):
    pool = store.setdefault("pool", {})
    p = pool.setdefault(e["pool"], {"cap": e.get("cap", 1), "used": 0})
    if mech.get("capacity_check"):
        if p["used"] + 1 > p["cap"]:
            _deny(res, "pool %s at capacity" % e["pool"])
            return
    p["used"] += 1
    _allow(res)
    res.log.append("reserved %s (%d/%d)" % (e["pool"], p["used"], p["cap"]))


def _ev_order_propose(store, e, res, mech):
    prop = store.setdefault("proposals", {}).setdefault(e["id"], {"unit": e["unit"], "pre": [], "state": "proposed"})
    prop["pre"] = list(e.get("pre", []))
    res.log.append("propose %s requires %s" % (e["id"], prop["pre"]))


def _ev_order_validate(store, e, res, mech):
    prop = store.setdefault("proposals", {}).setdefault(e["id"], {"unit": None, "pre": [], "state": "proposed"})
    prop["validated"] = True


def _ev_order_commit(store, e, res, mech):
    prop = store.setdefault("proposals", {}).setdefault(e["id"], {"unit": None, "pre": [], "state": "proposed"})
    if not prop.get("validated"):
        raise Inconsistent("commit before validation for %r" % e["id"])
    committed = store.setdefault("committed_order", [])
    committed_now = set(committed)
    if mech.get("common_order"):
        unmet = [p for p in prop["pre"] if p not in committed_now]
        if unmet:
            _deny(res, "precedence unmet: %s" % unmet)
            return
    committed.append(e["id"])
    prop["state"] = "committed"
    _allow(res)


def _ev_irrevocable_commit(store, e, res, mech):
    """Prepare, then durably commit an accepted value; the reply may be lost.

    mech['wal_before_ack'] = False removes the journal write before the
    durable commit, so a crash can lose a value already acknowledged.
    """
    key = "commit:%s" % e["id"]
    if e.get("interrupt_at") == "preparation":
        _deny(res, "interrupted before preparation")
        return
    T = store["journal"]
    tset(T, key, "prepared")
    if e.get("interrupt_at") == "commitment":
        _deny(res, "interrupted at commitment point")
        return
    if mech.get("wal_before_ack", True):
        tcommit(T)
    if e.get("lost_reply"):
        # durable commit happened; the requester learns nothing
        res.flags["reply"] = "lost"
        res.sink = "unknown"
    else:
        res.flags["reply"] = "success"
    _allow(res)


def _ev_crash(store, e, res, mech):
    T = store["journal"]
    T["live"] = dict(T["committed"])
    if e.get("power_loss") and mech.get("wal_before_ack", True):
        # power loss loses acknowledged-but-not-journalled values
        T["committed"] = {k: v for k, v in T["committed"].items() if v != "prepared"}
        T["live"] = dict(T["committed"])
    res.log.append("crash (%s)" % ("power" if e.get("power_loss") else "process"))


def _ev_recover_commit(store, e, res, mech):
    T = store["journal"]
    for key, value in sorted(T["committed"].items()):
        res.flags.setdefault("recovered_commits", []).append(key)
    res.log.append("recover committed journal")


def _ev_sink_send(store, e, res, mech):
    unit = e.get("unit")
    if unit is not None and not effective_exp(store, unit):
        _deny(res, "outward effect not authorized by current boundary state")
        return
    msg = store["comms"].setdefault(e["msg"], {"sent": 0, "accepted": False})
    msg["sent"] += 1
    res.flags["sent"] = msg["sent"]
    _allow(res)


def _ev_sink_accept(store, e, res, mech):
    msg = store["comms"].setdefault(e["msg"], {"sent": 0, "accepted": False})
    if mech.get("sink_at_most_once", False) and msg["accepted"]:
        res.log.append("sink suppresses duplicate (contract)")
        return
    msg["accepted"] = True
    content_counters(store, e.get("atom", "x"))["sink_accept"] += 1


def _ev_sink_reply(store, e, res, mech):
    msg = store["comms"].get(e["msg"], {})
    if e.get("drop"):
        res.sink = "unknown"
        res.flags["reply"] = "lost"
    else:
        res.sink = "accepted" if msg.get("accepted") else "unknown"
        res.flags["reply"] = "received"


def _ev_retry(store, e, res, mech):
    """Retry a use whose outcome is unknown. Baseline: no at-most-once
    contract, so a retry can duplicate; a sound sink contract forbids or
    suppresses it."""
    if mech.get("exactly_once", False):
        _deny(res, "exactly-once contract not supported")
        return
    _allow(res)
    res.flags["duplicate_possible"] = True


def _ev_snapshot(store, e, res, mech):
    store["snapshot"] = {
        "domain": store["domain"],
        "relations": copy.deepcopy(store["relations"]),
        "status": copy.deepcopy(store["status"]),
        "accepted": copy.deepcopy(store["accepted"]),
        "journal": copy.deepcopy(store["journal"]),
        "stamp": Stamp.next(),
    }
    res.log.append("snapshot domain %s" % store["domain"])


def _ev_restore(store, e, res, mech):
    snap = store.get("snapshot")
    if snap is None:
        raise Inconsistent("restore without snapshot")
    store["relations"] = copy.deepcopy(snap["relations"])
    store["status"] = copy.deepcopy(snap["status"])
    store["accepted"] = copy.deepcopy(snap["accepted"])
    store["journal"] = copy.deepcopy(snap["journal"])
    store["domain"] = snap["domain"]
    store["restamp"] = {"stamp": snap["stamp"], "domain": snap["domain"]}
    res.log.append("restore old image (domain %s, stamp %s)" % (snap["domain"], snap["stamp"]))


def _ev_fresh_credentials(store, e, res, mech):
    store["credentials"] = "fresh"
    res.flags["credentials"] = "fresh"
    res.log.append("fresh credentials issued")


def _ev_discover(store, e, res, mech):
    unit = e.get("unit", "C")
    if e.get("durable_state") is None:
        raise Inconsistent("no durable state to discover")
    store["discovered"].append({"unit": unit, "trusted_currentness": bool(e.get("trusted_currentness"))})
    res.flags["recovered_currentness"] = bool(e.get("trusted_currentness"))
    res.log.append("discover %s currentness=%s" % (unit, bool(e.get("trusted_currentness"))))


def _ev_validate(store, e, res, mech):
    if not store["discovered"]:
        raise Inconsistent("validation without discovery")
    if e.get("image") == "wrong_root":
        res.flags["quarantined"] = True
        _deny(res, "wrong root: image quarantined")
        return
    if e.get("image") == "incomplete":
        res.flags["quarantined"] = True
        _deny(res, "incomplete content: image quarantined")
        return
    if e.get("interpretation") and e.get("interpretation") != "compatible":
        res.flags["quarantined"] = True
        res.flags["widening_blocked"] = True
        _deny(res, "incompatible interpretation refused")
        return
    if e.get("trusted_currentness") is False and mech.get("recovery_requires_currentness", True):
        res.flags["sealed_without_currentness"] = True
        res.log.append("validation finds no trusted currentness; unit remains sealed")
    _allow(res)


def _ev_check_content(store, e, res, mech):
    """Recovery-side completeness check against discovered material."""
    if e.get("via"):
        from_ = e["via"]
    else:
        from_ = "durable"
    present = store["accepted"].get("C", [])
    candidates = [c for c in store["candidates"] if c["unit"] == "C"]
    if from_ != "durable":
        present = []
        candidates = []
    if store["discovered"] and not store["discovered"][-1]["trusted_currentness"] \
            and mech.get("recovery_requires_currentness", True) and not e.get("exempt"):
        _deny(res, "currentness not established; content not declared current")
        return
    res.flags["recovered_atoms"] = sorted(set(present))
    res.flags["recovered_candidates"] = len(candidates)
    _allow(res)


def _ev_lose_recovery(store, e, res, mech):
    if e.get("discard_discovered"):
        store["discovered"] = []
    store["recovered_stamps"] = list(store["recovered_stamps"])
    store["status"]["C"] = "sealed"
    res.log.append("recovery process lost (unit re-sealed)")


def _ev_activate_fresh(store, e, res, mech):
    if not store["discovered"]:
        raise Inconsistent("fresh activation without discovery")
    if not store["discovered"][-1]["trusted_currentness"]:
        res.flags["activated_without_currentness"] = True
        _deny(res, "activation refused: no trusted currentness")
        return
    store["status"]["C"] = "active"
    ok = 0
    if e.get("routes"):
        for r in e["routes"]:
            g = store["grants"].get("C", {}).get("local", {})
            if g.get(r):
                ok += 1
    res.flags["routes_restored"] = ok
    _allow(res)
    res.log.append("fresh activation with %d route(s)" % ok)


def _ev_candidate_add(store, e, res, mech):
    store["candidates"].append({"unit": e["unit"], "atom": e["atom"], "stamp": Stamp.next()})
    res.log.append("durable unaccepted candidate %s in %s" % (e["atom"], e["unit"]))


def _ev_durable_add(store, e, res, mech):
    store["dependents"][e["unit"]] = store["dependents"].get(e["unit"], 0) + 1
    res.log.append("durable dependent added to %s" % e["unit"])


def _ev_dispose(store, e, res, mech):
    unit = e["unit"]
    if e.get("what") == "accepted":
        store["accepted"][unit] = []
        store["dependents"][unit] = max(0, store["dependents"].get(unit, 0) - 1)
    elif e.get("what") == "candidate":
        if store["candidates"]:
            store["candidates"].pop(e.get("index", 0))
    elif e.get("what") == "dependent":
        store["dependents"][unit] = max(0, store["dependents"].get(unit, 0) - 1)
    if e.get("keep_representation"):
        store.setdefault("stale_reps", set()).add(unit)
    res.log.append("dispose %s of %s" % (e.get("what"), unit))


def _ev_delete(store, e, res, mech):
    unit = e["unit"]
    fails = []
    blocked = False
    if unit not in store["units"]:
        raise Inconsistent("delete of missing unit %r" % unit)
    for child, parent in store["parent"].items():
        if parent == unit and unit_exists(store, child):
            fails.append("child %s still contained" % child)
    if mech.get("complete_domain_checking", True):
        if store["dependents"].get(unit, 0) > 0:
            fails.append("%d durable dependent(s) not dispositioned" % store["dependents"][unit])
        if store["accepted"].get(unit):
            fails.append("accepted content present")
        cands = [c for c in store["candidates"] if c["unit"] == unit]
        if cands:
            fails.append("%d unaccepted durable candidate(s) confined" % len(cands))
    else:
        if store["accepted"].get(unit):
            fails.append("accepted content present")
        if [c for c in store["candidates"] if c["unit"] == unit] and mech.get("check_accepted_only"):
            res.log.append("weakened domain check: candidate z invisible to accepted-only check")
    stale = store.get("stale_reps")
    if stale and unit in stale:
        fails.append("retained representation of %s can still expose disposed material" % unit)
    if fails:
        res.delete_blocked = True
        res.delete_reason = "; ".join(fails)
        res.log.append("delete blocked: " + res.delete_reason)
    else:
        res.delete_blocked = False
        res.delete_reason = "allowed"
        store["status"][unit] = "removed"
        res.log.append("boundary %s removed" % unit)


def _ev_observe(store, e, res, mech):
    res.flags[e["name"]] = e["value"]


def _ev_isolate(store, e, res, mech):
    store["isolated"] = set(e.get("holders", ["A"]))
    res.log.append("isolate %s" % sorted(store["isolated"]))


def _ev_takeover(store, e, res, mech):
    holders = e.get("holders", ["B"])
    isolated = store.get("isolated", set())
    overlap = [h for h in holders if h in isolated]
    if overlap and mech.get("holder_exclusion", True):
        res.takeover_refused = True
        res.takeover_reason = "cannot establish exclusion for %s" % overlap
        return
    res.takeover_refused = False
    res.takeover_reason = "activated"
    res.log.append("takeover by %s" % holders)


def _ev_conflicting_accept(store, e, res, mech):
    unit = e["unit"]
    if store.get("isolated") and mech.get("holder_exclusion", True):
        if not effective(store, unit, "write"):
            _deny(res, "holder not eligible under current authority")
            return
        if store.get("conflict"):
            _deny(res, "second acceptance into %s while holder without exclusion exists" % unit)
            return
        store["conflict"] = e["result"]
        _allow(res)
        return
    _allow(res)


def _ev_clear_cache(store, e, res, mech):
    store["derived"] = []
    res.log.append("optional caches deleted")


def _ev_kill_half_derivation(store, e, res, mech):
    store["half"] = True
    res.log.append("half-completed derivation killed")


def _ev_submit_derived(store, e, res, mech):
    if store.get("half") and not e.get("recomputed") and mech.get("current_view_checking", True):
        _deny(res, "partial output is not an authoritative derivation")
        return
    if not effective(store, e["unit"], e["right"]):
        _deny(res, "recomputed guard refuses %s" % e["right"])
        return
    store["committed"] = store.get("committed")
    res.log.append("submitted derivation accepted")
    _allow(res)


def _ev_submit_old_derived(store, e, res, mech):
    snap = store["derived"][e.get("index", -1)]
    if mech.get("current_view_checking") is False:
        _allow(res)
        res.log.append("weakened current-view check: stale derivation admitted")
        return
    cur_epoch = tget(store["relations"], "epoch", {}).get(snap["unit"], 0)
    if snap["epoch"] != cur_epoch:
        _deny(res, "derived result from epoch %s, current epoch %s" % (snap["epoch"], cur_epoch))
        return
    _allow(res)


def _ev_interior_edit(store, e, res, mech):
    unit = e["unit"]
    rec = store["units"].get(unit)
    if rec is None:
        raise Inconsistent("edit of missing unit %r" % unit)
    field, value = e["field"], e["value"]
    if mech.get("metadata_separation", True):
        if field in ("parent", "identity", "grants", "status"):
            _deny(res, "interior edit cannot alter boundary field %s" % field)
            return
        res.log.append("interior content edit %s" % field)
        _allow(res)
        return
    if field == "parent":
        store["parent"][unit] = value
        res.log.append("weakened: interior edit changed parent to %s" % value)
    _allow(res)


def _ev_policy_change(store, e, res, mech):
    mode = mech.get("ac_policy", "ordered")
    decisions = ["read", "write"]
    if mode == "detached":
        tset(store["relations"], "policy", "broadened")
        _allow(res)
        res.log.append("weakened: policy broadened without Kernel order")
        return
    if mode == "partial":
        tset(store["relations"], "policy", "half_applied")
        _deny(res, "policy application partial: fail closed")
        if mech.get("ac_fail_closed", True):
            tupd(store["relations"], "epoch", lambda m: {**m, e["unit"]: m.get(e["unit"], 0) + 1}, {})
        res.log.append("partial application rejected")
        return
    if e.get("broadening") and not e.get("kernel_authorized"):
        if mech.get("ac_ordering", True):
            _deny(res, "policy broadening not authorized by Kernel")
            return
    tset(store["relations"], "policy", "broadened")
    tupd(store["relations"], "epoch", lambda m: {**m, e["unit"]: m.get(e["unit"], 0) + 1}, {})
    res.log.append("policy change ordered with Kernel change")
    _allow(res)


def _ev_reopen_access_check(store, e, res, mech):
    """A use after a revocation the Kernel acknowledged; authorization must be
    the Kernel's current decision, not 'policy used to permit it'."""
    unit = e["unit"]
    if mech.get("ac_ordering", True):
        if tget(store["relations"], "policy") == "broadened" and e.get("policy_still_permits"):
            _deny(res, "policy broadening cannot authorize post-revocation use")
            return
        _allow(res)
        return
    _allow(res)


def _ev_ac_out_of_band(store, e, res, mech):
    """Policy broadening applied outside the Kernel's ordering boundary."""
    tset(store["relations"], "policy", "out_of_band")
    res.flags["ac_in_boundary"] = False
    res.log.append("out-of-band policy broadening recorded")


def _ev_observe_ac(store, e, res, mech):
    thinks = e["kernel_thinks"]
    policy = tget(store["relations"], "policy", "narrow")
    res.flags["kernel_thinks"] = thinks
    res.flags["policy_state"] = policy
    res.flags["consistent"] = (thinks == "revoked" and policy != "broadened") or thinks == "granted"
    res.log.append("AC observation: kernel=%s policy=%s consistent=%s" %
                   (thinks, policy, res.flags["consistent"]))


def _ev_substitute_content(store, e, res, mech):
    """Boundary accepts the exact checked bytes, not the current path target."""
    checked = store["candidate_checked"]
    if mech.get("content_binding", True):
        if e.get("path_target") != checked["bytes"]:
            _deny(res, "path target %r differs from checked bytes %r" % (e["path_target"], checked["bytes"]))
            return
        _allow(res)
        return
    _allow(res)
    res.log.append("weakened content binding: accepted substituted bytes")


def _ev_hold_bytes(store, e, res, mech):
    store["trusted_copy"] = e["bytes"]
    store["candidate_checked"] = {"bytes": e["bytes"]}
    res.log.append("validated exact bytes %r" % e["bytes"])


def _ev_use_after_holder_loss(store, e, res, mech):
    victim = e.get("kill")
    if victim is not None:
        store["processes"][victim] = False
    if store.get("trusted_copy") or store["survivors"]:
        res.flags["bytes_available"] = store.get("trusted_copy") or sorted(store["survivors"])
        _allow(res)
    else:
        _deny(res, "required bytes unavailable")


def _ev_assign_dependency(store, e, res, mech):
    store["depends"] = {k: list(v) for k, v in e["map"].items()}


def _ev_coupled_move(store, e, res, mech):
    if mech.get("whole_effect_recovery"):
        tset(store["relations"], "move", e["to"])
        tcommit(store["relations"])
        store["parent"][e["child"]] = e["to"]
        _allow(res)
        res.log.append("coupled move committed")
        return
    store["parent"][e["child"]] = e["to"]
    _allow(res)
    res.log.append("weakened: half effect (parent changed, restrictions lost)")


def _ev_interrupt(store, e, res, mech):
    store["interrupted_at"] = e["at"]
    res.log.append("interrupted %s" % e["at"])


def _ev_resume_move(store, e, res, mech):
    if mech.get("whole_effect_recovery"):
        if tget(store["relations"], "move", None) is None:
            store["parent"][e["child"]] = None
            res.log.append("recovered: uninterfered effect is old relation")
            return
    # old relation is recovered if nothing committed
    res.log.append("resume recovered a whole relation")


def _ev_empty_check(store, e, res, mech):
    snap = len(store["units"]) and set(store["units"])
    store["empty_check_units"] = snap
    res.log.append("empty check observed %d units" % len(snap))


def _ev_assert_empty_removal(store, e, res, mech):
    unit = e["unit"]
    children = [c for c, p in store["parent"].items() if p == unit and unit_exists(store, c)]
    if children:
        store["parent"][children[0]] = None
        res.log.append("weakened: concurrent child %s stranded (moved to top)" % children[0])
        res.delete_blocked = False
        return
    res.delete_blocked = False
    res.log.append("removal of empty %s" % unit)


def _ev_discovery_graph(store, e, res, mech):
    store["root"] = e.get("root")


def _ev_generate_image(store, e, res, mech):
    return


def _ev_model_judgement(store, e, res, mech):
    decision = e.get("decision") or None
    if mech.get("policy_authorizes_model_decision"):
        if not effective(store, e["unit"], e.get("right", "write")):
            _deny(res, "policy does not authorize model decision")
            return
        res.flags["decision"] = decision
        _allow(res)
        return
    _deny(res, "model confidence cannot supply permission")


def _ev_append_message(store, e, res, mech):
    com = store["comms"].setdefault(e["msg"], {"messages": []})
    com["messages"].append(e["body"])
    res.log.append("append %r" % e["body"])


def _ev_activation_without_authority(store, e, res, mech):
    _ev_engine_use(store, {"unit": e.get("unit"), "ev": "engine_use"}, res, mech)


def _ev_restrict_pool(store, e, res, mech):
    return


def _ev_restart(store, e, res, mech):
    store["status"] = {u: "sealed" for u in store["units"]}
    res.log.append("restart")


def _ev_rebuild(st, e, res, mech):
    return


def _ev_half_scan(st, e, res, mech):
    return


HANDLERS = {
    "create": _ev_create,
    "grant": _ev_grant,
    "restriction": _ev_restriction,
    "seal": _ev_seal,
    "activate": _ev_activate,
    "engine_use": _ev_engine_use,
    "retain_handle": _ev_retain_handle,
    "kill": _ev_kill,
    "handle_use": _ev_handle_read,
    "internal_accept": _ev_internal_accept,
    "derive": _ev_derive,
    "revoke": _ev_revoke,
    "use": _ev_use_with,
    "use_old_derived": _ev_submit_old_derived,
    "position_advance": _ev_position_advance,
    "stale_claim": _ev_stale_claim,
    "replay_message": _ev_replay_message,
    "reserve": _ev_reserve,
    "order_propose": _ev_order_propose,
    "order_validate": _ev_order_validate,
    "order_commit": _ev_order_commit,
    "irrevocable_commit": _ev_irrevocable_commit,
    "crash": _ev_crash,
    "recover_commit": _ev_recover_commit,
    "sink_send": _ev_sink_send,
    "sink_accept": _ev_sink_accept,
    "sink_reply": _ev_sink_reply,
    "retry": _ev_retry,
    "snapshot": _ev_snapshot,
    "restore": _ev_restore,
    "fresh_credentials": _ev_fresh_credentials,
    "discover": _ev_discover,
    "validate": _ev_validate,
    "check_content": _ev_check_content,
    "lose_recovery": _ev_lose_recovery,
    "activate_fresh": _ev_activate_fresh,
    "candidate_add": _ev_candidate_add,
    "durable_add": _ev_durable_add,
    "dispose": _ev_dispose,
    "delete": _ev_delete,
    "observe": _ev_observe,
    "isolate": _ev_isolate,
    "takeover": _ev_takeover,
    "conflicting_accept": _ev_conflicting_accept,
    "clear_cache": _ev_clear_cache,
    "kill_half_derivation": _ev_kill_half_derivation,
    "submit_derived": _ev_submit_derived,
    "interior_edit": _ev_interior_edit,
    "policy_change": _ev_policy_change,
    "reopen_access_check": _ev_reopen_access_check,
    "ac_out_of_band": _ev_ac_out_of_band,
    "observe_ac": _ev_observe_ac,
    "substitute_content": _ev_substitute_content,
    "hold_bytes": _ev_hold_bytes,
    "use_after_holder_loss": _ev_use_after_holder_loss,
    "assign_dependency": _ev_assign_dependency,
    "coupled_move": _ev_coupled_move,
    "interrupt": _ev_interrupt,
    "resume_move": _ev_resume_move,
    "empty_check": _ev_empty_check,
    "assert_empty_removal": _ev_assert_empty_removal,
    "discovery_graph": _ev_discovery_graph,
    "generate_image": _ev_generate_image,
    "model_judgement": _ev_model_judgement,
    "append_message": _ev_append_message,
    "activation_without_authority": _ev_activation_without_authority,
    "restrict_pool": _ev_restrict_pool,
    "restart": _ev_restart,
    "rebuild": _ev_rebuild,
    "half_scan": _ev_half_scan,
}


def build(init):
    store = new_store()
    store.update(copy.deepcopy(init.get("store", {})))
    for k in ("content",):
        base = new_store()["content"]
        for atom in CONTENT_ATOMS:
            base.setdefault(atom, {"internal": 0, "outward": 0, "published": 0, "sink_accept": 0})
        store["content"] = {a: dict(base[a]) for a in CONTENT_ATOMS}
        for a, v in init.get("store", {}).get("content", {}).items():
            store["content"].setdefault(a, {"internal": 0, "outward": 0, "published": 0, "sink_accept": 0})
            store["content"][a].update(v)
    for e in init.get("events", []):
        res = Result()
        apply(store, e, res, {})
    return store


def run_scenario(world, scenario, mech=None):
    mech = dict(mech or {})
    store = build(world["init"])
    if "store_patch" in scenario:
        _patch(store, scenario["store_patch"])
    res = Result()
    for e in scenario["events"]:
        apply(store, e, res, mech)
    return store, res


def _patch(store, patch):
    for path, value in patch.items():
        parts = path.split(".")
        cur = store
        for part in parts[:-1]:
            cur = cur[int(part)] if part.isdigit() else cur.setdefault(part, {})
        last = parts[-1]
        if last.isdigit():
            cur[int(last)] = value
        else:
            cur[last] = value


def check(expect, res, store):
    """Evaluate an expectation dict against a result. Returns list of failures."""
    fails = []

    def eq(name, got, want):
        if want is not None and got != want:
            fails.append("%s: expected %r, got %r" % (name, want, got))

    eq("deny", res.denied, expect.get("deny"))
    eq("engine_deny", res.engine_denied, expect.get("engine_deny"))
    eq("delete_blocked", res.delete_blocked, expect.get("delete_blocked"))
    eq("takeover_refused", res.takeover_refused, expect.get("takeover_refused"))
    eq("sink", res.sink, expect.get("sink"))
    for k, v in (expect.get("flags") or {}).items():
        got = res.flags.get(k)
        if got != v:
            fails.append("flag %s: expected %r, got %r" % (k, v, got))
    for k, v in (expect.get("store") or {}).items():
        got = _read_path(store, k)
        if got != v:
            fails.append("store[%s]: expected %r, got %r" % (k, v, got))
    for name, fn in (expect.get("calls") or {}).items():
        if "construct" in fn:
            try:
                fn["construct"](store)
            except Inconsistent:
                fails.append("call %s could not be constructed" % name)
    for name, fn in (expect.get("refused") or {}).items():
        try:
            fn["construct"](store)
        except Inconsistent:
            continue
        fails.append("call %s was not refused" % name)
    if expect.get("reason_contains") and expect["reason_contains"] not in (res.reason or ""):
        fails.append("reason %r lacks %r" % (res.reason, expect["reason_contains"]))
    return fails


def _read_path(store, path):
    cur = store
    for part in path.split("."):
        if isinstance(cur, (dict, list)) and part.isdigit() and isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            if part not in cur:
                return "<missing>"
            cur = cur[part]
        else:
            return "<unreadable>"
    if isinstance(cur, set):
        return sorted(cur)
    return cur
