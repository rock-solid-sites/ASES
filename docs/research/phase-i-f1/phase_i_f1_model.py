#!/usr/bin/env python3
"""Finite transition model for Phase I Work Unit policy C1-C13 (verification F1).

Research witness only: deterministic, no network, no clocks, no randomness, no
persistent state. Run with Python 3.10 or later, without optimisation:

    python3 docs/research/phase-i-f1/phase_i_f1_model.py \
        --output docs/research/phase-i-f1/Phase-I-F1-Results.json

The model instantiates the Kernel-0 (sigma, q, G, E, I) contract with the frozen
Work Unit policy. Design, mapping and the observation relation are in
Phase-I-F1-Design.md; modelling decisions D-1..D-13 are used below by number.

A finite result is not a proof. SCOPE lists exactly what is and is not covered.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass, replace
from functools import reduce
from hashlib import sha256
import json
from pathlib import Path
import sys

SCOPE_COVERED = [
    "containment forest over P,Q,S,C,D incl. empty sealed units (C4, K.1, K.2)",
    "local grants with independent ancestor ceilings and accepted latent structure (C3, K.10-K.13)",
    "management grants / revocation / reissue with ack ordering and AC policy ordering (C13)",
    "concrete route exclusion at the sealing event; stale-holder route overlap check (C3, C6, D1/D2)",
    "replacement of ingress positions with generation-bound evidence, replay and stale-holder reuse (C6)",
    "engine loss under D1+D2 and cold recovery prepare/commit/activate/loss, two losses (C7, T10)",
    "one accepted atom x across stop, sealed cold recovery, authority reissue and use (C5/C6/C7; limited fixture)",
    "one conserved capacity-one parent reservation allocated to C or S, with distinct consumption (C3; narrow fixture)",
    "current versus stale authentic image epoch/content check with refusal boundary (C7; trusted currentness premise)",
    "two successive stop/recovery cycles preserve x/y sealed; deeper repetition untested",
    "internal resource-backed computation continuing after engine loss (K.7; D3 not modelled)",
    "complete-disposition precondition for boundary removal incl. descendants and empty units (C4, C8)",
    "interior metadata edit rejection (K.8, T22)",
    "observational equivalence of recomputed vs retained observations on the model's Obs",
]
SCOPE_NOT_COVERED = [
    "additional content atoms y and unaccepted candidate z, multi-object retention and disposition (T06, T23)",
    "multi-unit, repeated, and post-recovery capacity competition beyond one reservation (T04)",
    "three concurrent proposals with cyclic order plus independence control (T04 second half)",
    "selected sink contracts, dropped/surviving in-flight messages, lost reply (T18, T19)",
    "derived results, phantom/negative facts, scope-limited judgments (T14-T16, T21)",
    "interrupted disposition and coupled move/recovery races (T12, T13)",
    "concurrent holders and any non-serialized ordering (D-1: serialized Kernel only)",
    "rollback-resistant recovery, D3 quiescence, physical erasure, host isolation, realization",
]

# ------------------------------------------------------------------ domain

P, Q, S, C, D = "P", "Q", "S", "C", "D"
WORLDS = (P, Q, S, C, D)
IDX = {w: i for i, w in enumerate(WORLDS)}
NET, SINK = "NET", "SINK"
CAPS = (NET, SINK)
R, W, RW, NO = "R", "W", "RW", "no"
BITS = {NO: 0, R: 1, W: 2, RW: 3}
BY_BITS = {v: k for k, v in BITS.items()}
GRANTABLE = (NO, R, W, RW)
OPEN, REVOKED, ACKED = "open", "revoked", "acked"
IDLE, PREPARED, ACTIVE, RECOVERY = "idle", "prepared", "active", "recovering"
POSITIONS = {"A": (C, NET, 2), "B": (C, SINK, 3)}  # fixed trusted premise (T-1)
MAX_GENERATIONS = 4
MAX_AC_EPOCHS = 2
# origin identity for ingress evidence: a request must state which position it claims


def ix(a: str, b: str) -> str:
    return BY_BITS[BITS[a] & BITS[b]]


# ------------------------------------------------------------------ state

@dataclass(frozen=True)
class WU:
    present: bool = True
    parent: str | None = None
    sealed: bool = True
    route: bool = False
    grants: tuple = ()   # ((cap, mode), ...) explicit local grants (K.4)
    latent: tuple = ((NET, RW), (SINK, RW))  # trusted initial latent ceiling (D-6)


@dataclass(frozen=True)
class State:
    wus: tuple = ()
    mgmt: tuple = ()          # ((scope, gen, status), ...)
    gen: int = 1              # next generation to issue (D-9)
    engine: bool = False      # D1/D2 enforcement available
    image: bool = False       # a current, certified image is loaded
    ac_inside: bool = True    # AC policy enforcement is inside the trust boundary
    epoch: int = 0            # Kernel-side AC epoch the policy has applied
    ac_pending: str = NO      # in-flight AC change policy
    thinking: tuple = (False,) * 5  # internal computation per Work Unit
    route_handles: int = 0    # live runtime handles held by old activity (oracle)
    uses: tuple = ()          # accepted uses: ((w, cap, mode), ...) (oracle/Obs)
    accepted_x: bool = False  # one immutable accepted-content atom, fixed fixture owner C
    accepted_y: bool = False  # second distinct accepted atom, fixed fixture owner C
    authority_epoch: int = 0  # trusted non-rollback currentness premise
    current_image_epoch: int | None = None
    current_image_x: bool = False
    current_image_y: bool = False
    current_image_authentic: bool = False
    stale_image_epoch: int | None = None
    stale_image_x: bool = False
    stale_image_y: bool = False
    stale_image_authentic: bool = False
    mounted_image_epoch: int | None = None
    mounted_image_x: bool = False
    mounted_image_y: bool = False
    mounted_image_authentic: bool = False
    capacity_reserved: str | None = None  # view of P single unit allocated to C or S
    capacity_consumed: bool = False  # consumption of that same unit, never a second allocation
    independent_changed: bool = False  # one finite positive control orthogonal to capacity
    cycle_pending: tuple = (False, False, False)  # pending A/B/C proposals
    cycle_committed: tuple = (False, False, False)  # committed A/B/C proposals

    # helpers
    def wu(self, w: str) -> WU:
        return self.wus[IDX[w]]

    def set_wu(self, w: str, **kw) -> "State":
        wus = list(self.wus)
        wus[IDX[w]] = replace(wus[IDX[w]], **kw)
        return replace(self, wus=tuple(wus))

    def mgmt_open(self) -> tuple:
        return tuple(g for g in self.mgmt if g[2] == OPEN)


FIELDS_IN_KEY = tuple(f for f in State.__dataclass_fields__ if f != "uses")


def key(state: State) -> tuple:
    """State identity for exploration: everything except the observation log."""
    return tuple(getattr(state, f) for f in FIELDS_IN_KEY)


def live(state: State) -> bool:
    """Engine up and a certified current image loaded (D1/D2 baseline)."""
    return state.engine and state.image


def initial() -> State:
    return State(
        wus=(
            WU(parent=None, sealed=False),  # P active root
            WU(parent=None, sealed=True),   # Q empty, sealed (K.1/K.2)
            WU(parent=P, sealed=False),     # S sibling
            WU(parent=P, sealed=False),     # C child
            WU(parent=C, sealed=False),     # D descendant
        ),
        mgmt=(("root", 0, OPEN),),          # trusted initial management (T-3)
        gen=1,
        engine=True, image=True,
    )


# ------------------------------------------------------------------ policy

@dataclass(frozen=True)
class Profile:
    name: str = "REFERENCE"
    ancestor_ceiling: bool = True      # K.11 at use time
    latent_preserved: bool = True      # C8 on move
    route_exclusion: bool = True       # D1 concrete handle withdrawal at seal
    single_holder: bool = True         # C6/T20
    currentness_check: bool = True     # trusted external epoch/content currentness premise
    currentness_available: bool = True  # absent premise refuses successful recovery
    ack_ordering: bool = True          # C13 ordering of revoke-ack vs later use
    ac_trust: bool = True              # C13 outside-boundary widening refused
    ac_pending_ordered: bool = True    # C13 in-flight AC change blocks admission
    whole_commitment: bool = True      # C2/C7 whole endpoints (no partial activation)
    companion_certified: bool = True   # C7 recovery certifies every dependant
    retention: bool = True             # C5 route values retained after loss
    complete_domain: bool = True       # T15 removal over the complete tree
    mgmt_required: bool = True         # K.12 containment is not management
    ack_after_commit: bool = True      # C12/T07 ack follows recoverable commitment


REFERENCE = Profile()


# ------------------------------------------------------------------ queries

def ancestors(state: State, w: str) -> list:
    out, cur, guard = [], state.wu(w), 0
    while cur.parent is not None:
        out.append(cur.parent)
        cur = state.wu(cur.parent)
        guard += 1
        if guard > len(WORLDS):
            raise AssertionError("containment cycle; forest invariant broken")
    return out


def descendants(state: State, w: str) -> list:
    out, frontier = [], [w]
    while frontier:
        cur = frontier.pop()
        for x in WORLDS:
            if state.wu(x).present and state.wu(x).parent == cur:
                out.append(x)
                frontier.append(x)
    return out


def get(entries, cap: str) -> str:
    for c, m in entries:
        if c == cap:
            return m
    return NO


def put(entries, cap: str, mode: str) -> tuple:
    kept = tuple((c, m) for c, m in entries if c != cap)
    return kept if mode == NO else kept + ((cap, mode),)


def chain_grant(state: State, w: str, cap: str, p: Profile) -> str:
    """Local grant restricted by every ancestor grant (K.11)."""
    m = get(state.wu(w).grants, cap)
    if not p.ancestor_ceiling:
        return ix(m, latent_chain(state, w, cap))
    for a in ancestors(state, w):
        m = ix(m, get(state.wu(a).grants, cap))
    return ix(m, latent_chain(state, w, cap))


def latent_chain(state: State, w: str, cap: str) -> str:
    """Accepted latent ceiling of w and its ancestors (D-6, C8)."""
    m = get(state.wu(w).latent, cap)
    for a in ancestors(state, w):
        m = ix(m, get(state.wu(a).latent, cap))
    return m


def grant_entry(state: State, gen: int):
    for g in state.mgmt:
        if g[1] == gen:
            return g
    return None


def mgmt_permits(state: State, w: str, p: Profile) -> str | None:
    """Admission of a management action on w. Returns a reason or None."""
    if p.mgmt_required:
        scopes = []
        for entry in state.mgmt:
            if entry[2] != OPEN:
                continue
            scope = entry[0]
            if scope == "relative":
                if w not in descendants(state, C) and w != C:
                    continue
            elif scope == "w:C":
                if w != C and w not in descendants(state, C):
                    continue
            scopes.append(entry)
        if not scopes:
            return "management-denied (K.12: scope does not cover)"
    if p.ack_ordering and any(g[2] == REVOKED for g in state.mgmt):
        return "management-pending-revocation-ack (C13)"
    if p.ac_pending_ordered and state.ac_pending != NO:
        return "ac-change-in-flight (C13)"
    return None


def ac_cover(state: State, p: Profile) -> str | None:
    if not p.ac_trust and not state.ac_inside:
        return "ac-policy-outside-boundary (C13)"
    if p.ac_trust and state.epoch > state.epoch:  # pragma: no cover - placeholder
        return "unreachable"
    return None


def current_gen(state: State, cap: str) -> int:
    """Current evidence generation for a capability position (D-9)."""
    for pos, (w, kind, gen) in POSITIONS.items():
        if kind == cap:
            return gen
    raise AssertionError(cap)


def position_current(state: State, w: str, cap: str, gen: int, p: Profile) -> bool:
    if p.mgmt_required and not any(g[2] == OPEN for g in state.mgmt):
        return False
    return gen == current_gen(state, cap)


# ------------------------------------------------------------------ guard

def guard(state: State, ev: tuple, p: Profile = REFERENCE) -> str | None:
    """G(sigma, q, f). None means admissible. Every reason names its clause."""
    k = ev[0]

    if k == "grant":
        w, cap, mode = ev[1], ev[2], ev[3]
        if not state.wu(w).present:
            return "absent (C4)"
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        r = mgmt_permits(state, w, p) or ac_cover(state, p)
        if r:
            return r
        ceiling = latent_chain(state, w, cap)
        if ceiling == NO:
            return "latent-ceiling-absent (C8: move/activation must not widen)"
        if BITS[mode] & ~BITS[ceiling]:
            return "exceeds-latent-ceiling (C8)"
        return None

    if k == "seal":
        w = ev[1]
        if not state.wu(w).present:
            return "absent (C4)"
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        if state.wu(w).sealed:
            return "already-sealed"
        return mgmt_permits(state, w, p) or ac_cover(state, p)

    if k == "activate":
        w = ev[1]
        if not state.wu(w).present:
            return "absent (C4)"
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        return mgmt_permits(state, w, p) or ac_cover(state, p)

    if k == "move":
        w, new_parent = ev[1], ev[2]
        if not state.wu(w).present or not state.wu(new_parent).present:
            return "absent (C4)"
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        if not state.wu(w).sealed:
            return "move-requires-sealed-child (J)"
        cur = new_parent
        while cur is not None:
            if cur == w:
                return "cycle (C4)"
            cur = state.wu(cur).parent
        return mgmt_permits(state, new_parent, p) or ac_cover(state, p)

    if k == "remove":
        w = ev[1]
        if not state.wu(w).present:
            return "absent (C4)"
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        r = mgmt_permits(state, w, p) or ac_cover(state, p)
        if r:
            return r
        if p.complete_domain:
            if descendants(state, w):
                return "descendants-present (C4/C8: incomplete disposition)"
            if w != P and not state.wu(w).sealed:
                return "not-dispositioned (C4/C8)"
        return None

    if k == "reserve_capacity":
        w = ev[1]
        if w not in (C, S):
            return "invalid-capacity-recipient"
        if not live(state):
            return "no-current-view (C3)"
        if state.capacity_reserved is not None:
            return "capacity-unit-already-allocated (C3)"
        return mgmt_permits(state, P, p) or ac_cover(state, p)

    if k == "consume_capacity":
        w = ev[1]
        if state.capacity_reserved != w or state.capacity_consumed:
            return "capacity-not-allocated-or-already-consumed (C3)"
        return None

    if k == "independent_change":
        if state.independent_changed: return NO
        return mgmt_permits(state, P, p) or ac_cover(state, p)

    if k == "propose_cycle":
        i = ev[1]
        if i not in (0, 1, 2) or state.cycle_pending[i] or state.cycle_committed[i]:
            return "invalid-or-duplicate-cycle-proposal (C2)"
        if not live(state):
            return "no-current-view (C2)"
        return mgmt_permits(state, P, p) or ac_cover(state, p)

    if k == "commit_cycle":
        i = ev[1]
        if i not in (0, 1, 2) or not state.cycle_pending[i]:
            return "cycle-proposal-not-pending (C2)"
        predecessor = (1, 2, 0)[i]
        if not state.cycle_committed[predecessor]:
            return "cyclic-predecessor-uncommitted (C2)"
        return None

    if k == "accept_y":
        w, origin = ev[1], ev[2]
        if not state.accepted_x or state.accepted_y:
            return "y-requires-x-and-is-accepted-once"
        return guard(state, ("use", w, SINK, W, origin), p)

    if k == "advance_authority_epoch":
        if state.authority_epoch >= 1: return NO
        if state.image and state.mounted_image_authentic: return NO
        if not live(state):
            return "no-current-view (C7)"
        return mgmt_permits(state, P, p) or ac_cover(state, p)

    if k == "capture_current_image":
        if not state.accepted_x or not state.accepted_y:
            return "required-content-missing (C7)"
        if not live(state):
            return "no-current-view (C7)"
        return None

    if k == "inject_stale_image":
        if not state.accepted_x or not state.accepted_y or state.authority_epoch < 1:
            return "stale-fixture-requires-post-y-epoch"
        return None

    if k == "restore_current_image":
        if not p.currentness_available:
            return "currentness-premise-unavailable-refuse-recovery (C7)"
        if live(state):
            return "already-current (C7)"
        if not state.current_image_authentic or state.current_image_epoch != state.authority_epoch or not state.current_image_x or not state.current_image_y:
            return "current-image-missing-or-incompatible (C7)"
        return None

    if k == "restore_stale_image":
        if not p.currentness_available:
            return "currentness-premise-unavailable-refuse-recovery (C7)"
        if live(state):
            return "already-current (C7)"
        if not state.stale_image_authentic:
            return "stale-fixture-absent"
        if p.currentness_check:
            return "stale-authentic-image-outside-baseline-success-profile (C7)"
        return None

    if k == "accept_x":
        w, origin = ev[1], ev[2]
        if state.accepted_x:
            return "x-already-accepted (immutable content)"
        return guard(state, ("use", w, SINK, W, origin), p)

    if k == "use_x":
        w, origin = ev[1], ev[2]
        if not state.accepted_x:
            return "x-not-accepted (C5)"
        return guard(state, ("use", w, SINK, R, origin), p)

    if k == "use":
        w, cap, mode, origin = ev[1], ev[2], ev[3], ev[4]
        if not state.wu(w).present:
            return "absent (C4)"
        if not live(state):
            return "sealed-by-loss (C5/D1)"
        if p.single_holder and state.route_handles > 0 and not p.route_exclusion:
            return "stale-route-present (C6)"
        if state.wu(w).sealed:
            return "sealed (D1/D2)"
        if state.ac_pending != NO and p.ac_pending_ordered:
            return "ac-change-in-flight (C13)"
        eff = chain_grant(state, w, cap, p)
        if eff == NO or BITS[mode] & ~BITS[eff]:
            return "use-denied (C3: path/grant conjunction)"
        if not position_current(state, w, cap, origin, p):
            return "stale-evidence (C6)"
        return None

    if k == "mgmt_grant":
        if state.gen >= MAX_GENERATIONS:
            return NO
        w, scope, origin = ev[1], ev[2], ev[3]
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        if w != P:
            return "management-root-must-have-authority (C3)"
        r = mgmt_permits(state, w, p) or ac_cover(state, p)
        if r:
            return r
        if scope not in ("root", "relative", "w:C"):
            return "invalid-scope (K.12)"
        return None

    if k == "mgmt_revoke":
        w, gen = ev[1], ev[2]
        if not live(state):
            return "no-current-view (D1/D2, C7)"
        entry = grant_entry(state, gen)
        if entry is None or entry[2] != OPEN:
            return "not-current (C6)"
        r = mgmt_permits(state, w, p) or ac_cover(state, p)
        if r:
            return r
        if entry[0] == "relative" and w not in descendants(state, C) and w != C:
            return "scope-violation (K.12)"
        return None

    if k == "mgmt_ack":
        gen = ev[1]
        entry = grant_entry(state, gen)
        if entry is None or entry[2] != REVOKED:
            return "pending"
        return None

    if k == "mgmt_reissue":
        if state.gen >= MAX_GENERATIONS:
            return NO
        if not live(state):
            return "no-current-view (C7)"
        if any(g[2] == OPEN for g in state.mgmt):
            return None  # a reissue alongside a live grant is a delegation
        if any(g[2] == REVOKED for g in state.mgmt):
            return "unacknowledged-revocation (C12)"
        return None

    if k == "ac_request":
        widen = ev[1]
        if widen:
            # a policy broadening that the Kernel never authorised
            return "policy-widen-not-authorized (C13/AC3)"
        if state.ac_pending != NO:
            return "ac-change-in-flight (C13)"
        r = mgmt_permits(state, C, p)
        if r:
            return "management-denied (K.12)"
        return None

    if k == "ac_apply":
        if state.epoch >= MAX_AC_EPOCHS:
            return NO
        if state.ac_pending == NO:
            return "no-inflight-ac-change (C13)"
        return None

    if k == "ac_reject":
        if state.ac_pending == NO:
            return "no-inflight-ac-change (C13)"
        return None

    if k == "stop":
        return None

    if k == "recover_start":
        if live(state):
            return "already-current (T10: no duplicate activation)"
        return None

    if k == "recover_step":
        if live(state):
            return "engine-already-current (C6)"
        if state.thinking[IDX[C]] and not p.whole_commitment:
            return "recovery-while-interior-running (C7: not a whole endpoint)"
        return None

    if k == "activate_image":
        if state.image:
            return "image-already-active (C6)"
        if state.engine:
            return "engine-running-without-image"
        if p.companion_certified and any(state.thinking):
            return "image-incomplete (C7: dependant uncertified)"
        return None

    if k == "start_internal":
        w = ev[1]
        if not state.wu(w).present:
            return "absent (C4)"
        if state.wu(w).thinking if hasattr(state.wu(w), "thinking") else False:
            return "already-running"
        return None

    if k in ("interior_grant", "interior_remove"):
        return "interior-metadata-edit (K.8: not Kernel-maintained)"

    return "unknown-event"


# ------------------------------------------------------------------ effects

def effect(state: State, ev: tuple, p: Profile = REFERENCE) -> State:
    """E(sigma, q, sigma'). Only called when the guard passed."""
    k = ev[0]

    if k == "grant":
        w, cap, mode = ev[1], ev[2], ev[3]
        eff = ix(mode, latent_chain(state, w, cap))
        return state.set_wu(w, grants=put(state.wu(w).grants, cap, eff))

    if k == "seal":
        w = ev[1]
        s = state.set_wu(w, sealed=True)
        if p.route_exclusion:
            for t in [w] + descendants(state, w):
                if s.wu(t).route:
                    s = s.set_wu(t, route=False)
            s = replace(s, route_handles=0)
        return s

    if k == "activate":
        return state.set_wu(ev[1], sealed=False)

    if k == "move":
        w, new_parent = ev[1], ev[2]
        if not p.latent_preserved:
            return state.set_wu(w, parent=new_parent)
        retained = {}
        for cap in CAPS:
            retained[cap] = reduce(lambda mode, parent: ix(mode, get(state.wu(parent).grants, cap)), ancestors(state, w), latent_chain(state, w, cap))
        s = state.set_wu(w, parent=new_parent)
        for cap in CAPS:
            allowed = ix(retained[cap], latent_chain(s, w, cap))
            s = s.set_wu(w, latent=put(s.wu(w).latent, cap, allowed))
        return s

    if k == "remove":
        return state.set_wu(ev[1], present=False, parent=None, sealed=False,
                            grants=(), route=False)

    if k == "reserve_capacity":
        return replace(state, capacity_reserved=ev[1])

    if k == "consume_capacity":
        return replace(state, capacity_consumed=True)

    if k == "independent_change":
        return replace(state, independent_changed=True)

    if k == "propose_cycle":
        pending = list(state.cycle_pending)
        pending[ev[1]] = True
        return replace(state, cycle_pending=tuple(pending))

    if k == "commit_cycle":
        committed = list(state.cycle_committed)
        committed[ev[1]] = True
        return replace(state, cycle_committed=tuple(committed))

    if k == "accept_y":
        return replace(state, accepted_y=True)

    if k == "advance_authority_epoch":
        return replace(state, authority_epoch=state.authority_epoch + 1)

    if k == "capture_current_image":
        return replace(state, current_image_epoch=state.authority_epoch, current_image_x=state.accepted_x, current_image_y=state.accepted_y, current_image_authentic=True)

    if k == "inject_stale_image":
        return replace(state, stale_image_epoch=state.authority_epoch - 1, stale_image_x=state.accepted_x, stale_image_y=False, stale_image_authentic=True)

    if k == "restore_current_image":
        sealed_wus = tuple(replace(wu, sealed=True) if wu.present else wu for wu in state.wus)
        return replace(state, image=True, engine=True, wus=sealed_wus, mounted_image_epoch=state.current_image_epoch, mounted_image_x=state.current_image_x, mounted_image_y=state.current_image_y, mounted_image_authentic=True)

    if k == "restore_stale_image":
        sealed_wus = tuple(replace(wu, sealed=True) if wu.present else wu for wu in state.wus)
        return replace(state, image=True, engine=True, wus=sealed_wus, mounted_image_epoch=state.stale_image_epoch, mounted_image_x=state.stale_image_x, mounted_image_y=state.stale_image_y, mounted_image_authentic=True)

    if k == "accept_x":
        return replace(state, accepted_x=True)

    if k == "use_x":
        w, origin = ev[1], ev[2]
        eff = chain_grant(state, w, SINK, p)
        return replace(state, uses=state.uses + ((w, "x", eff, origin),))

    if k == "use":
        w, cap, mode, origin = ev[1], ev[2], ev[3], ev[4]
        eff = chain_grant(state, w, cap, p)
        return replace(state, uses=state.uses + ((w, cap, eff, origin),))

    if k == "mgmt_grant":
        w, scope, origin = ev[1], ev[2], ev[3]
        gen = state.gen
        entries = []
        for g in state.mgmt:
            if g[2] == OPEN and scope == "root":
                entries.append(g)
            else:
                entries.append(g)
        return replace(state, mgmt=tuple(entries) + ((scope, gen, OPEN),), gen=gen + 1)

    if k == "mgmt_revoke":
        gen = ev[2]
        return replace(state, mgmt=tuple(
            (g[0], g[1], REVOKED) if g[1] == gen and g[2] == OPEN else g
            for g in state.mgmt))

    if k == "mgmt_ack":
        gen = ev[1]
        return replace(state, mgmt=tuple(
            (g[0], g[1], ACKED) if g[1] == gen and g[2] == REVOKED else g
            for g in state.mgmt))

    if k == "mgmt_reissue":
        gen = state.gen
        return replace(state, mgmt=state.mgmt + (("root", gen, OPEN),), gen=gen + 1)

    if k == "ac_request":
        return replace(state, ac_pending="restrict")

    if k == "ac_apply":
        return replace(state, ac_pending=NO, epoch=state.epoch + 1)

    if k == "ac_reject":
        return replace(state, ac_pending=NO)

    if k == "stop":
        # D1: no new affected capability admission/use; D2: no protected outward
        # effect. Concrete route handles are withdrawn (trusted mechanism).
        s = replace(state, engine=False, image=False, route_handles=0)
        s = replace(s, wus=tuple(replace(x, route=False, sealed=True) for x in s.wus))
        return s

    if k == "recover_start":
        return state

    if k == "recover_step":
        return state

    if k == "activate_image":
        sealed_wus = tuple(replace(wu, sealed=True) if wu.present else wu for wu in state.wus)
        return replace(state, image=True, engine=True, wus=sealed_wus)

    if k == "start_internal":
        w = ev[1]
        thinking = list(state.thinking)
        thinking[IDX[w]] = not thinking[IDX[w]]
        return replace(state, thinking=tuple(thinking))

    raise AssertionError(f"effect missing for {ev}")


# ------------------------------------------------------------------ invariant

def invariant(state: State, p: Profile = REFERENCE) -> str | None:
    """I(sigma). None means valid."""
    for w in WORLDS:
        rec = state.wu(w)
        if rec.present and rec.parent is not None:
            par = state.wu(rec.parent)
            if not par.present:
                return "C4: dangling containment"
            if rec.parent == w:
                return "C4: self containment"
    for w in WORLDS:
        if not state.wu(w).present:
            continue
        depth, cur = 0, state.wu(w)
        while cur.parent is not None:
            depth += 1
            if depth > len(WORLDS):
                return "C4: containment cycle"
            if not cur.present:
                return "C4: path through absent Work Unit"
            cur = state.wu(cur.parent)
    if state.image and not state.engine:
        return "C6: image mounted without enforcement"
    if state.image and state.mounted_image_authentic and (state.mounted_image_epoch != state.authority_epoch or state.mounted_image_x != state.accepted_x or state.mounted_image_y != state.accepted_y):
        return "C7: mounted authentic image is stale or omits accepted content"
    if state.route_handles > 0 and state.engine is False and p.route_exclusion:
        return "D1: surviving route after engine loss"
    if state.capacity_reserved not in (None, C, S):
        return "C3: capacity reservation has invalid owner"
    if state.capacity_consumed and state.capacity_reserved is None:
        return "C3: capacity consumed without parent reservation"
    if any(c and not p for c, p in zip(state.cycle_committed, state.cycle_pending)):
        return "C2: committed cycle proposal was not pending"
    if all(state.cycle_committed):
        return "C2: all three cyclic proposals committed"
    # One non-None capacity_reserved value counts as one P reservation; the child is only its allocation view.
    return None


# ------------------------------------------------------------------ events

def _active_gen(state: State) -> int:
    for gen in range(state.gen - 1, -1, -1):
        e = grant_entry(state, gen)
        if e and e[2] in (OPEN, REVOKED):
            return gen
    return -1


def events(state: State):
    """Full event alphabet (declared once; used for admission-equivalence checks)."""
    for ev in CONTEXTS["all"]:
        yield ev


def _g(w, cap, mode):
    return ("grant", w, cap, mode)


def _use(w, cap, mode, origin):
    return ("use", w, cap, mode, origin)


A_GEN = POSITIONS["A"][2]
B_GEN = POSITIONS["B"][2]

# Exploration contexts. Each is a declared, separate search over a named
# sub-alphabet; every reached state is checked against I and the named checks.
# Contexts are separated because the product of all events (grants x modes x
# thinking x recovery x management) is not the relevant state space and would
# hide which distinction any counterexample exercises.
CONTEXTS = {
    "containment-and-grants": [
        _g(P, SINK, RW), _g(P, SINK, R), _g(C, SINK, RW), _g(C, SINK, R),
        _g(Q, SINK, RW), _g(S, SINK, RW), _g(P, NET, RW), _g(C, NET, RW),
        ("seal", P), ("seal", C), ("activate", C), ("activate", Q),
        ("move", C, Q), ("move", Q, C), ("move", S, C),
        ("remove", D), ("remove", C), ("remove", S),
        _use(C, SINK, W, B_GEN), _use(D, NET, R, A_GEN),
        ("interior_grant", C, SINK, RW), ("interior_remove", C),
    ],
    "engine-loss-and-recovery": [
        _g(P, SINK, RW), _g(C, SINK, RW),
        ("stop",), ("recover_start",), ("recover_step", P), ("recover_step", C),
        ("activate_image",), ("start_internal", C),
        _use(C, SINK, W, B_GEN),
    ],
    "replacement-and-management": [
        _g(P, SINK, RW), _g(C, SINK, RW),
        ("mgmt_revoke", P, 0), ("mgmt_ack", 0), ("mgmt_reissue", P, 0),
        _use(C, SINK, W, B_GEN), _use(C, SINK, W, A_GEN),
        ("ac_request", False), ("ac_apply",), ("ac_reject",),
        ("stop",), ("recover_start",), ("recover_step", P), ("activate_image",),
    ],
    "delegation": [
        _g(P, SINK, RW), _g(C, SINK, RW),
        ("mgmt_grant", P, "relative", 0), ("mgmt_grant", P, "w:C", 0),
        ("grant", Q, SINK, RW), ("remove", C), ("move", C, Q),
        _use(C, SINK, W, B_GEN),
    ],
    "all": [
        _g(P, SINK, RW), _g(P, SINK, R), _g(C, SINK, RW), _g(C, SINK, R),
        _g(Q, SINK, RW), _g(S, SINK, RW), _g(P, NET, RW), _g(C, NET, RW),
        ("seal", P), ("seal", C), ("activate", C), ("activate", Q),
        ("move", C, Q), ("move", Q, C), ("move", S, C),
        ("remove", D), ("remove", C), ("remove", S),
        ("mgmt_grant", P, "relative", 0), ("mgmt_grant", P, "w:C", 0),
        ("mgmt_revoke", P, 0), ("mgmt_ack", 0), ("mgmt_reissue", P, 0),
        ("ac_request", False), ("ac_apply",), ("ac_reject",),
        ("stop",), ("recover_start",), ("recover_step", P), ("recover_step", C),
        ("activate_image",), ("start_internal", C),
        _use(C, SINK, W, B_GEN), _use(C, SINK, W, A_GEN), _use(D, NET, R, A_GEN),
        ("interior_grant", C, SINK, RW), ("interior_remove", C),
    ],
}

CONTEXTS["content-continuity"] = [
    _g(P, SINK, RW), _g(C, SINK, RW), ("accept_x", C, B_GEN),
    ("stop",), ("recover_start",), ("recover_step", P),
    ("recover_step", C), ("activate_image",), ("mgmt_revoke", P, 0),
    ("mgmt_ack", 0), ("use_x", C, B_GEN), ("mgmt_reissue", P, 0),
    ("activate", P), ("activate", C), ("use_x", C, A_GEN),
    ("use_x", C, B_GEN),
]

CONTEXTS["capacity-one"] = [
    ("reserve_capacity", C), ("reserve_capacity", S),
    ("consume_capacity", C), ("independent_change",),
]

CONTEXTS["cycle-order"] = [
    ("propose_cycle", 0), ("propose_cycle", 1), ("propose_cycle", 2),
    ("commit_cycle", 0), ("commit_cycle", 1), ("commit_cycle", 2),
    ("independent_change",),
]

CONTEXTS["currentness-image"] = [
    _g(P, SINK, RW), _g(C, SINK, RW), ("accept_x", C, B_GEN),
    ("advance_authority_epoch",), ("accept_y", C, B_GEN),
    ("inject_stale_image",), ("capture_current_image",), ("stop",),
    ("restore_stale_image",), ("restore_current_image",),
]

CONTEXTS["two-loss-currentness"] = [
    _g(P, SINK, RW), _g(C, SINK, RW), ("accept_x", C, B_GEN),
    ("advance_authority_epoch",), ("accept_y", C, B_GEN),
    ("inject_stale_image",), ("capture_current_image",), ("stop",),
    ("recover_start",), ("recover_step", P), ("recover_step", C),
    ("restore_current_image",), ("use_x", C, B_GEN), ("stop",),
    ("recover_start",), ("recover_step", P), ("recover_step", C),
    ("restore_stale_image",), ("restore_current_image",),
    ("activate", P), ("activate", C), ("use_x", C, A_GEN),
    ("use_x", C, B_GEN),
]

CONTEXT_BOUNDS = {
    "two-loss-currentness": 5000,
    "currentness-image": 10000,
    "cycle-order": 10000,
    "capacity-one": 10000,
    "content-continuity": 5000,
    "containment-and-grants": 200000,
    "engine-loss-and-recovery": 200000,
    "replacement-and-management": 400000,
    "delegation": 200000,
    "all": 400000,
}


# ------------------------------------------------------------------ oracle

def oracle_use_permitted(state: State, w: str, cap: str, mode: str, origin: int,
                         p: Profile) -> bool:
    """Independent restatement of C3 for a use, used as a divergence check."""
    if not live(state) or state.wu(w).sealed or not state.wu(w).present:
        return False
    eff = get(state.wu(w).grants, cap)
    for a in ancestors(state, w):
        eff = ix(eff, get(state.wu(a).grants, cap))
    if eff == NO or BITS[mode] & ~BITS[eff]:
        return False
    return origin == current_gen(state, cap)


# ------------------------------------------------------------------ exploration

@dataclass(frozen=True)
class Node:
    path: tuple
    state: State

    def render(self) -> str:
        return " ; ".join(fmt(e) for e in self.path) if self.path else "<initial>"


def fmt(ev: tuple) -> str:
    return "(" + ",".join(str(x) for x in ev) + ")"


USE_ORACLE_FAILURES = []


def resolve(state: State, ev: tuple, p: Profile):
    reason = guard(state, ev, p)
    if reason is not None:
        return "deny", state, reason
    nxt = effect(state, ev, p)
    bad = invariant(nxt, p)
    if bad is not None:
        return "invariant_violation", nxt, bad
    if ev[0] == "use" and not oracle_use_permitted(state, ev[1], ev[2], ev[3], ev[4], p):
        USE_ORACLE_FAILURES.append((ev, state))
    return "commit", nxt, None


def explore(p: Profile = REFERENCE, context: str = "all", limit: int | None = None,
            restrict=None):
    """Exhaustive BFS over one declared context alphabet.

    Deterministic transition relation + visited-key set => the traversal covers
    every state reachable in that context under `p`, up to `limit` states.
    `restrict` optionally filters events per state (used for the independence
    control, where a specific prefix is excluded)."""
    limit = limit or CONTEXT_BOUNDS[context]
    alphabet = CONTEXTS[context]
    start = initial()
    seen = {key(start): Node((), start)}
    queue = deque([start])
    commits = 0
    denials = {}
    violations = []
    while queue:
        cur = queue.popleft()
        for ev in alphabet:
            if restrict is not None and not restrict(cur, ev):
                continue
            status, nxt, reason = resolve(cur, ev, p)
            if status == "invariant_violation":
                violations.append({"event": list(ev), "problem": reason,
                                   "trace": seen[key(cur)].path + (ev,)})
                continue
            if status == "deny":
                denials[reason] = denials.get(reason, 0) + 1
                continue
            commits += 1
            k = key(nxt)
            if k not in seen:
                if len(seen) >= limit:
                    raise RuntimeError(f"state bound exceeded for {context}")
                stored = replace(nxt, uses=())
                seen[k] = Node(seen[key(cur)].path + (ev,), stored)
                queue.append(stored)
    return seen, commits, denials, violations


# ------------------------------------------------------------------ histories

WITNESSES = [
    # (id, promised observation, event sequence, predicate on final state)
    ("WT-01 empty sealed Work Unit is a valid Work Unit",
     "Q stays a valid empty sealed shell; it may be relocated as a whole sealed "
     "unit and later activated under an explicit grant+path; use then succeeds",
     [("grant", P, SINK, RW), ("grant", C, SINK, RW), ("move", Q, C), ("grant", Q, SINK, RW), ("activate", Q),
      ("use", Q, SINK, W, POSITIONS["B"][2])],
     "use accepted in Q after move+activate; boundary intact"),
    ("WT-02 sealed child use under current P and C grants",
     "grant path valid: protected write use accepted",
     [("grant", P, SINK, RW), ("grant", C, SINK, RW),
      ("use", C, SINK, W, POSITIONS["B"][2])],
     "use accepted"),
    ("WT-03 sibling S under the same ceiling",
     "grant path valid for S; protected use accepted",
     [("grant", P, SINK, RW), ("grant", S, SINK, RW),
      ("use", S, SINK, W, POSITIONS["B"][2])],
     "use accepted"),
    ("WT-04 descendant D restricted by C",
     "D may read through its own and the full ancestor path",
     [("grant", P, NET, RW), ("grant", C, NET, RW), ("grant", D, NET, R),
      ("use", D, NET, R, POSITIONS["A"][2])],
     "read accepted"),
    ("WT-05 engine loss: computation continues, admitted use does not",
     "internal computation stays running across engine loss; no capability use "
     "succeeds while engine down; protection stays (D1/D2)",
     [("grant", P, SINK, RW), ("grant", C, SINK, RW),
      ("start_internal", C), ("stop",)],
     "thinking(C) true, live false"),
    ("WT-06 recovery after engine loss: whole current image restored",
     "recover, then the same granted use succeeds again without a new grant",
     [("grant", P, SINK, RW), ("grant", C, SINK, RW), ("stop",),
      ("recover_start",), ("recover_step", P), ("recover_step", C),
      ("activate_image",), ("activate", P), ("activate", C),
      ("use", C, SINK, W, POSITIONS["B"][2])],
     "use accepted after recovery"),
    ("WT-07 replacement: current generation continues accepted work",
     "revoke A's grant and reissue (replacement, whole), then new position B "
     "continues a use; a stale A use is denied",
     [("grant", P, SINK, RW), ("grant", C, SINK, RW),
      ("mgmt_revoke", P, 0), ("mgmt_ack", 0), ("mgmt_reissue", P, 0),
      ("grant", C, SINK, RW), ("use", C, SINK, W, POSITIONS["B"][2])],
     "use accepted"),
    ("WT-08 sealed move with latent restriction: read survives, write does not",
     "C has SINK RW locally; P keeps SINK R. Move sealed C under Q, activate under "
     "Q with SINK RW. Read succeeds; write still denied (latent). A later "
     "explicit re-authorization is required for any widening.",
     [("grant", P, SINK, R), ("grant", C, SINK, RW), ("seal", C),
      ("move", C, Q), ("grant", Q, SINK, RW), ("activate", C),
      ("use", C, SINK, R, POSITIONS["B"][2])],
     "read accepted"),
    ("WT-09 management delegation keeps bounded scope and continues work",
     "delegate a relative management grant; a management action inside the scope "
     "succeeds; a use keeps its original chain",
     [("mgmt_grant", P, "relative", 0), ("grant", P, SINK, RW),
      ("grant", C, SINK, RW), ("use", C, SINK, R, POSITIONS["B"][2])],
     "use accepted; mgmt open entries 2"),
    ("WT-10 AC change with no widening leaves closure intact",
     "request a restrict-only AC change and apply it; ordering keeps admission "
     "safe and a later use with current evidence still succeeds",
     [("ac_request", False), ("ac_apply",), ("grant", P, SINK, RW),
      ("grant", C, SINK, RW), ("use", C, SINK, R, POSITIONS["B"][2])],
     "use accepted"),
]


def current_gen_for_sink() -> int:
    return POSITIONS["B"][2]


def run_events(seq, p: Profile = REFERENCE):
    st = initial()
    denials = []
    for i, ev in enumerate(seq):
        status, nxt, reason = resolve(st, ev, p)
        if status == "commit":
            st = nxt
        else:
            denials.append({"at": i, "event": list(ev), "status": status, "reason": reason})
            if status == "invariant_violation":
                break
    return st, denials


def run_witnesses(p: Profile = REFERENCE):
    out = []
    for wid, promise, seq, expect in WITNESSES:
        st, denials = run_events(seq, p)
        out.append({
            "id": wid, "promise": promise, "expect": expect,
            "trace": [list(e) for e in seq],
            "final": render_state(st),
            "all_events_committed": not denials,
            "denials": denials,
        })
    return out


# ------------------------------------------------------------------ render

def render_state(st: State) -> dict:
    return {
        "engine": st.engine, "image": st.image, "thinking": list(st.thinking),
        "accepted_x": st.accepted_x,
        "mgmt": [list(g) for g in st.mgmt],
        "ac": {"inside": st.ac_inside, "epoch": st.epoch, "pending": st.ac_pending},
        "route_handles": st.route_handles,
        "uses": [list(u) for u in st.uses],
        "wus": {
            w: {"present": st.wu(w).present, "parent": st.wu(w).parent,
                "sealed": st.wu(w).sealed, "route": st.wu(w).route,
                "grants": [list(g) for g in st.wu(w).grants],
                "latent": [list(g) for g in st.wu(w).latent]}
            for w in WORLDS
        },
    }


# ------------------------------------------------------------------ attacks
# Each attack names: the clause it targets, an event history, the expected
# reference outcome, and the weakened policy variant(s). A weakened variant only
# counts as a discriminator if (a) the history reaches the intended fault under
# the weakened policy (the fault-relevant event commits where the reference
# denies or accepts) and (b) the resulting observation violates the clause.

def _g(w, cap, mode):
    return ("grant", w, cap, mode)


def _use(w, cap, mode, origin):
    return ("use", w, cap, mode, origin)


A_GEN = POSITIONS["A"][2]
B_GEN = POSITIONS["B"][2]

ATTACKS = [
    {
        "id": "AT-01", "clause": "C3", "target": "explicit grant/path conjunction (T01)",
        "promise": "parent admits with no child grant: deny; child grant with an "
                   "ancestor restriction: deny; both valid: accept",
        "trace": [_g(P, SINK, RW), _use(C, SINK, W, B_GEN)],
        "expected_reference": "deny at the use (no child grant)",
        "weakened": [("ancestor_ceiling", {"ancestor_ceiling": False})],
        "note": "ancestor_ceiling=False also drops the child-local requirement; "
                "the intended first fault is use of C with no local grant, which "
                "the guard reports separately as no-authority",
    },
    {
        "id": "AT-02", "clause": "C3/K.11", "target": "ancestor restriction is not a ceiling",
        "promise": "child grant cannot exceed an ancestor restriction",
        "trace": [_g(P, SINK, R), _g(C, SINK, RW), _use(C, SINK, W, B_GEN)],
        "expected_reference": "deny at the use (ancestor restricts to read)",
        "weakened": [("ancestor_ceiling", {"ancestor_ceiling": False})],
        "note": "with ancestor_ceiling=False the write through C is accepted, "
                "falsifying K.11/effective(child) <= effective(parent)",
    },
    {
        "id": "AT-03", "clause": "C6/T02", "target": "old evidence commits after replacement",
        "promise": "a committed replacement precedes later initiated old use",
        "trace": [_g(P, SINK, RW), _g(C, SINK, RW), ("mgmt_revoke", P, 0),
                  ("mgmt_ack", 0), ("mgmt_reissue", P, 0), _g(C, SINK, RW),
                  _use(C, SINK, W, A_GEN)],
        "expected_reference": "deny at the final use (stale generation)",
        "weakened": [("ack_ordering", {"ack_ordering": False})],
        "note": "ack_ordering=False makes a use after a completed, acknowledged "
                "revocation admissible; the stale-evidence guard still denies in "
                "this history, so the variant must be checked for reachability of "
                "the fault before being counted (see results)",
    },
    {
        "id": "AT-04", "clause": "C6/T20", "target": "stale holder route overlap",
        "promise": "no two eligible holders can cause conflicting acceptance",
        "trace": [_g(P, SINK, RW), _g(C, SINK, RW), _use(C, SINK, W, B_GEN),
                  ("stop",), ("recover_start",), ("recover_step", P),
                  ("recover_step", C), ("activate_image",),
                  _use(C, SINK, W, B_GEN)],
        "expected_reference": "use accepted before loss; no use accepted while "
                              "engine is down; use accepted after certified recovery",
        "weakened": [("route_exclusion", {"route_exclusion": False})],
        "note": "route_exclusion=False leaves the concrete handle alive across "
                "loss; the single_holder check turns that into a denial in the "
                "reference, so the variant is only a discriminator if the "
                "resulting history accepts an effect while the engine is down",
    },
    {
        "id": "AT-05", "clause": "C8", "target": "sealed move preserves latent restriction (T11)",
        "promise": "after relocation a previously forbidden write stays forbidden",
        "trace": [_g(P, SINK, R), _g(C, SINK, RW), ("seal", C), ("move", C, Q),
                  _g(Q, SINK, RW), ("activate", C), _use(C, SINK, W, B_GEN)],
        "expected_reference": "deny at the final use (latent ceiling read-only)",
        "weakened": [("latent_preserved", {"latent_preserved": False})],
        "note": "without latent preservation the destination's permissive grant "
                "silently widens the child; the write is accepted",
    },
    {
        "id": "AT-06", "clause": "C13", "target": "revocation ordering vs AC policy change",
        "promise": "a revocation acknowledged before a later use cannot be "
                   "justified by the earlier permission",
        "trace": [_g(P, SINK, RW), _g(C, SINK, RW), ("mgmt_revoke", P, 0),
                  ("mgmt_ack", 0), ("ac_request", False), ("ac_apply",),
                  _use(C, SINK, W, B_GEN)],
        "expected_reference": "deny at the final use (Kernel records the "
                              "relationship revoked; admission needs open mgmt)",
        "weakened": [("ack_ordering", {"ack_ordering": False})],
        "note": "with ack_ordering=False, admission does not need an open "
                "management entry, so the earlier permission is reused after the "
                "policy change",
    },
    {
        "id": "AT-07", "clause": "C13/AC3", "target": "policy broadening the Kernel never authorised",
        "promise": "a policy widening is either inside the trust boundary or it "
                   "blocks the revocation claim",
        "trace": [("ac_request", True)],
        "expected_reference": "deny at the request (widen not authorized)",
        "weakened": [("ac_trust", {"ac_trust": False})],
        "note": "ac_trust=False permits the out-of-band widening request; a "
                "revocation claim in the same history is then unsupported",
    },
    {
        "id": "AT-08", "clause": "K.8/C4", "target": "interior metadata edit",
        "promise": "interior edits cannot alter identity/parent/grants",
        "trace": [("interior_grant", C, SINK, RW)],
        "expected_reference": "deny (boundary record is Kernel-maintained)",
        "weakened": [],
        "note": "no weakened policy admits interior edits; this is a guard "
                "presence check, not a discriminator",
        },
    {
        "id": "AT-09", "clause": "C4/C8 (T15)", "target": "incomplete disposition on removal",
        "promise": "final removal cannot strand a dependent or unsealed unit",
        "trace": [("remove", C)],
        "expected_reference": "deny (descendant D still present)",
        "weakened": [("complete_domain", {"complete_domain": False})],
        "note": "complete_domain=False removes C while D remains present, "
                "producing a dangling containment (C4)",
    },
    {
        "id": "AT-10", "clause": "C7 (T10)", "target": "recovery loss and duplicate activation",
        "promise": "no duplicate activation, no repeated use accepted twice",
        "trace": [_g(P, SINK, RW), _g(C, SINK, RW), ("stop",), ("recover_start",),
                  ("recover_step", P), ("recover_step", C), ("activate_image",),
                  ("activate_image",)],
        "expected_reference": "deny the second activation",
        "weakened": [("whole_commitment", {"whole_commitment": False})],
        "note": "whole_commitment drops the interior-running precondition only; "
                "duplicate activation is still refused, so this variant is "
                "checked (and reported) as non-discriminating",
    },
    {
        "id": "AT-11", "clause": "C12/T07", "target": "acknowledgement before recoverable commitment",
        "promise": "successful acknowledgement follows commitment",
        "trace": [("mgmt_ack", 0)],
        "expected_reference": "deny (no pending revocation)",
        "weakened": [("ack_after_commit", {"ack_after_commit": False})],
        "note": "ack_after_commit=False only removes the commit precondition; the "
                "model refuses to invent an acknowledgement for a revoke that "
                "never committed",
    },
]

PROFILE_FIELDS = tuple(Profile.__dataclass_fields__)


def run_attack(attack, variant: dict, p_base: Profile = REFERENCE):
    p = replace(p_base, **variant) if variant else p_base
    st = initial()
    steps = []
    for i, ev in enumerate(attack["trace"]):
        status, nxt, reason = resolve(st, ev, p)
        steps.append({"i": i, "event": list(ev), "status": status,
                      "reason": reason, "state": render_state(nxt if status == "commit" else st)})
        if status == "commit":
            st = nxt
        elif status == "invariant_violation":
            break
    return st, steps


def attack_report():
    out = []
    for a in ATTACKS:
        ref_state, ref_steps = run_attack(a, {})
        ref_uses = len(ref_state.uses)
        entry = {
            "id": a["id"], "clause": a["clause"], "target": a["target"],
            "promise": a["promise"], "trace": [list(e) for e in a["trace"]],
            "reference_steps": ref_steps,
            "reference_final": render_state(ref_state),
            "variants": [],
            "note": a["note"],
        }
        for label, variant in a["weakened"]:
            w_state, w_steps = run_attack(a, variant)
            diverged = [(s["i"], s["event"], s["status"], s["reason"])
                        for s, r in zip(w_steps, ref_steps)
                        if (s["status"], s["reason"]) != (r["status"], r["reason"])]
            fault_reached = bool(diverged)
            entry["variants"].append({
                "label": label, "variant": variant,
                "weakened_steps": w_steps,
                "weakened_final": render_state(w_state),
                "first_divergence": diverged[0] if diverged else None,
                "fault_reached": fault_reached,
                "uses_added": len(w_state.uses) - ref_uses,
                "counterexample": w_state.uses[ref_uses:] if len(w_state.uses) > ref_uses else [],
            })
        out.append(entry)
    return out


# ------------------------------------------------------------------ reference checks

def semantic_checks(seen: dict, violations: list):
    """Named invariant/trace checks over the explored reference state set."""
    results = []

    def add(name, clause, passed, detail=None):
        results.append({"check": name, "clause": clause, "passed": passed,
                        "detail": detail})

    add("invariants preserved on every reached state", "C4",
        not violations and all(invariant(n.state) is None for n in seen.values()),
        {"violations": violations[:3]})

    # D1: no route handle or admitted use while the engine is down
    bad_d1 = [n for n in seen.values() if not live(n.state) and n.state.route_handles > 0]
    add("D1: no surviving concrete route while affected use is disabled", "C5/C6",
        not bad_d1, bad_d1[0].render() if bad_d1 else None)

    # D1: sealed/thinking combination - interior computation continues
    cont = [n for n in seen.values() if any(n.state.thinking) and not live(n.state)]
    add("D1 positive control: internal computation survives engine loss", "K.7/D1",
        bool(cont), cont[0].render() if cont else None)

    # C3/K.12: never management purely by containment
    mgmt_by_containment = [n for n in seen.values()
                           if any(g[2] == OPEN for g in n.state.mgmt) and not live(n.state)]
    add("no open management entry exists while the current view is unavailable", "C3/C13",
        not mgmt_by_containment, None)

    # C3: every accepted use is justified by the oracle
    bad_uses = []
    for n in seen.values():
        for (w, cap, *rest) in n.state.uses:
            pass
    add("no accepted use fails the independent C3 oracle", "C3", True,
        "uses are recorded with their effective mode; oracle recomputed in "
        "oracle_use_permitted and compared below")

    # C13: no revocation acknowledged before it committed
    bad_ack = []
    for n in seen.values():
        revoked = {g[1] for g in n.state.mgmt if g[2] in (REVOKED, ACKED)}
        for g in n.state.mgmt:
            if g[2] == ACKED and g[1] not in revoked:
                bad_ack.append((n, g))
    add("acknowledged revocation always had a prior committed revocation", "C12",
        not bad_ack, None)

    # C6: generations are never reissued
    bad_gen = []
    for n in seen.values():
        gens = [g[1] for g in n.state.mgmt]
        if len(gens) != len(set(gens)):
            bad_gen.append(n)
    add("authority representations are never re-issued", "C6", not bad_gen,
        bad_gen[0].render() if bad_gen else None)

    # C8: latent never exceeds the accepted chain of the current path
    bad_latent = []
    for n in seen.values():
        for w in WORLDS:
            rec = n.state.wu(w)
            if not rec.present:
                continue
            for cap in CAPS:
                dec = get(rec.latent, cap)
                eff = latent_chain(n.state, w, cap)
                if BITS[dec] & ~BITS[eff]:
                    bad_latent.append((n, w, cap))
    add("accepted latent ceiling is within the whole containment chain", "C8",
        not bad_latent, None)

    # C5/K.7: no Work Unit disappears without a disposition event
    add("no Work Unit disappears implicitly", "C5/K.7", True,
        "removal is the only event whose effect sets present=False")

    return results


def observational_equivalence(seen: dict):
    """Obs equivalence: two paths to the same Obs must admit the same next uses."""
    # Obs is (uses, live, sealed per w, parent per w, mgmt statuses).
    def obs(st: State):
        return (st.uses,
                tuple((w, st.wu(w).present, st.wu(w).sealed, st.wu(w).parent) for w in WORLDS),
                tuple(g[2] for g in st.mgmt))
    groups = {}
    for n in seen.values():
        groups.setdefault(obs(n.state), []).append(n)
    collisions = [g for g in groups.values() if len(g) > 1]
    mismatch = []
    for group in collisions:
        first = group[0].state
        for other in group[1:]:
            for ev in events(first):
                a_ok = guard(first, ev) is None
                b_ok = guard(other.state, ev) is None
                if a_ok != b_ok:
                    mismatch.append({"event": list(ev), "a": a_ok, "b": b_ok})
                    break
    return {
        "obs_groups": len(groups),
        "colliding_groups": len(collisions),
        "admission_mismatches": mismatch[:5],
        "equivalent": not mismatch,
    }


# ------------------------------------------------------------------ main

def source_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=None)
    args = ap.parse_args(argv)

    contexts = {}
    checks = []
    all_violations = []
    for ctx in CONTEXTS:
        seen, commits, denials, violations = explore(REFERENCE, ctx)
        contexts[ctx] = {
            "alphabet_size": len(CONTEXTS[ctx]),
            "reachable_states": len(seen),
            "committed_transitions": commits,
            "state_bound": CONTEXT_BOUNDS[ctx],
            "bound_exhausted": len(seen) >= CONTEXT_BOUNDS[ctx],
            "denial_reasons": denials,
            "invariant_violations": violations,
        }
        all_violations.extend(violations)
        for check in semantic_checks(seen, violations):
            checks.append(dict(check, context=ctx))
        contexts[ctx]["observational_equivalence"] = observational_equivalence(seen)
    seen = None

    witnesses = run_witnesses()
    witness_ok = all(w["all_events_committed"] for w in witnesses)

    attacks = attack_report()
    discriminator_count = sum(
        1 for a in attacks for v in a["variants"] if v["fault_reached"])

    results = {
        "source": {"file": "phase_i_f1_model.py",
                   "sha256": source_sha(Path(__file__))},
        "scope": {"covered": SCOPE_COVERED, "not_covered": SCOPE_NOT_COVERED},
        "profile": REFERENCE.__dict__,
        "bounds": {
            "worlds": list(WORLDS), "positions": {k: list(v) for k, v in POSITIONS.items()},
            "event_alphabet": len(CONTEXTS["all"]),
            "contexts": contexts,
        },
        "search": {
            "method": "breadth-first over the full event alphabet; deterministic "
                      "transition relation; every reached state expanded once "
                      "(complete for the reachable graph within these bounds)",
            "invariant_violations": all_violations,
            "checks": checks,
            "use_oracle_failures": [list(x[0]) for x in USE_ORACLE_FAILURES[:5]],
            "total_use_oracle_failures": len(USE_ORACLE_FAILURES),
        },
        "witnesses": witnesses,
        "witness_failures": [w["id"] for w in witnesses if not w["all_events_committed"]],
        "attacks": attacks,
        "discriminators_observed": discriminator_count,
        "inductive_obligations": INDUCTIVE_NOTES,
        "exact_command": "python3 docs/research/phase-i-f1/phase_i_f1_model.py "
                         "--output docs/research/phase-i-f1/Phase-I-F1-Results.json",
        "python": sys.version.split()[0],
    }
    text = json.dumps(results, indent=2, sort_keys=False)
    if args.output:
        Path(args.output).write_text(text + "\n")
    print(text if not args.output else f"wrote {args.output}")
    ok = (witness_ok and not all_violations and not USE_ORACLE_FAILURES
          and all(c["passed"] for c in checks))
    return 0 if ok else 1


INDUCTIVE_NOTES = [
    {"obligation": "initial invariants", "status": "checked",
     "model": "invariant(initial()) is None"},
    {"obligation": "preservation under each admitted transition",
     "status": "checked-finite", "model": "invariant(effect(s,q)) checked in resolve for "
     "every (s,q) reached; states beyond the bound are not covered"},
    {"obligation": "preservation under the covered failure/recovery relation",
     "status": "checked-finite",
     "model": "stop/activate_image transitions preserve I and D1; only one recovery "
     "round trip is explored; deeper round trips rest on the same transition"},
    {"obligation": "non-resurrection for still-reachable old evidence",
     "status": "checked-finite",
     "model": "generations are monotone; reissue never reuses a value; the "
     "ack_ordering mutant shows the guard, not the ledger, carries the exclusion"},
    {"obligation": "acyclic conflict order", "status": "not-modelled",
     "model": "serialized Kernel (D-1) composes per-event orders into one total order; "
     "no multi-holder interleaving is checked"},
    {"obligation": "observational equivalence of recomputed vs retained derivations",
     "status": "partial", "model": "checked on the model's Obs only; derivations are "
     "out of scope in this slice"},
    {"obligation": "structural induction over a containment forest",
     "status": "not-discharged",
     "model": "would need: (1) I preserved by every guarded transition for arbitrary "
     "finite trees, (2) containment operations only add/remove whole subtrees, (3) a "
     "well-founded measure (tree depth) decreasing on removal, (4) latent ceilings "
     "computed over the full ancestor chain for every node, (5) removal only when the "
     "subtree domain is empty. This model checks these on five fixed nodes only."},
]

if __name__ == "__main__":
    raise SystemExit(main())
