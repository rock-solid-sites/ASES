#!/usr/bin/env python3
"""Still-live finite research service. See Kernel-0-Realization-Experiment.md.

No model imports, persistence, network listener, caller-asserted identity, or
state-loading endpoint. Bootstrap descriptors/configuration are trusted input.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import os
import socket
import sys
import threading


CONTENTS = ("accepted\u0000zero\n", "accepted\u0000one\n")
POSITIONS = (0, 0, 0, 1)
MAX_FRAME = 4096


@dataclass(frozen=True)
class View:
    established: bool = False
    data: tuple = (0, 0)
    content: str | None = None
    issued: int = 0
    rights: tuple = (0, 0, 0, 0)
    parents: tuple = (-1, -1, -1, -1)
    cycle: tuple = (0, 0, 0)  # Only used in the separate cycle profile.


@dataclass(frozen=True)
class Proposal:
    kind: str
    target: int = 0
    value: int | str = 0
    other: int = 0


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate field")
        out[key] = value
    return out


def decode(raw):
    obj = json.loads(raw, object_pairs_hook=unique_object)
    if type(obj) is not dict:
        raise ValueError("object required")
    if obj == {"kind": "read"}:
        return Proposal("read")
    if set(obj) != {"kind", "target", "value", "other"}:
        raise ValueError("exact proposal fields required")
    k, t, v, o = (obj[key] for key in ("kind", "target", "value", "other"))
    if type(k) is not str or k not in {
        "establish", "grant", "restrict", "replace", "delegate", "set",
        "flip", "pair", "accept", "resume", "mixed", "cycle",
    }:
        raise ValueError("unknown effect")
    if type(t) is not int or t not in range(4) or type(o) is not int or o not in range(4):
        raise ValueError("invalid context or target")
    if k in ("accept", "resume"):
        if type(v) is not str or v not in CONTENTS:
            raise ValueError("content outside finite witness")
    elif type(v) is not int or v not in range(8):
        raise ValueError("invalid value")
    if k in ("set", "flip") and (t > 1 or v > 1):
        raise ValueError("invalid field")
    if k == "pair" and v > 3 or k == "cycle" and (t > 2 or v > 1):
        raise ValueError("invalid composite or cycle")
    return Proposal(k, t, v, o)


def valid(s, profile):
    if not s.established:
        return s == View()
    if s.content not in CONTENTS or any(x not in (0, 1) for x in s.data + s.cycle):
        return False
    if profile == "coupled" and sum(s.data) > 1:
        return False
    active = [i for i, mask in enumerate(s.rights) if mask]
    if profile == "exclusive" and len(active) > 1:
        return False
    if any(sum(POSITIONS[a] == p for a in active) > 1 for p in (0, 1)):
        return False
    if any(not s.issued & (1 << a) for a in active):
        return False
    for child, parent in enumerate(s.parents):
        if parent != -1 and (child != 3 or parent not in (0, 1, 2)
                             or not s.rights[child] or s.rights[child] & ~s.rights[parent]):
            return False
    return all(0 <= mask <= 7 for mask in s.rights)


def candidate(s, a, q, profile):
    """Concrete policy, independently implemented from the model oracle."""
    k, t, v, o = q.kind, q.target, q.value, q.other
    if a not in (-1, 0, 1, 2, 3):
        return None
    if k == "establish":
        return replace(s, established=True, content=CONTENTS[0]) if a == -1 and not s.established else None
    if not s.established:
        return None
    if k in ("grant", "restrict", "replace", "delegate"):
        masks, parents = list(s.rights), list(s.parents)
        issued = s.issued

        def withdraw_or_limit(context, mask):
            masks[context] = mask
            if not mask:
                parents[context] = -1
            for child in range(4):
                if parents[child] == context:
                    masks[child] &= mask
                    if not masks[child]:
                        parents[child] = -1

        if k == "restrict":
            if a != -1 or not masks[t] or v & ~masks[t]:
                return None
            withdraw_or_limit(t, v)
        else:
            destination = o if k == "replace" else t
            if issued & (1 << destination):
                return None
            if k == "delegate":
                if a not in (0, 1, 2) or t != 3 or not v or v & ~masks[a]:
                    return None
                masks[t], parents[t] = v, a
            elif k == "grant":
                if a != -1 or not v:
                    return None
                masks[t], parents[t] = v, -1
            else:
                if a != -1 or not masks[t] or POSITIONS[t] != POSITIONS[o]:
                    return None
                previous = masks[t]
                withdraw_or_limit(t, 0)
                masks[o], parents[o] = previous, -1
            issued |= 1 << destination
        return replace(s, issued=issued, rights=tuple(masks), parents=tuple(parents))

    required = {"set": 1 << t, "flip": 1 << t, "pair": 3,
                "accept": 4, "resume": 1, "mixed": 1, "cycle": 1}.get(k)
    if a < 0 or required is None or required & ~s.rights[a]:
        return None
    if k == "mixed":
        return None  # Its authority-grant portion is forbidden to every worker.
    if k == "accept":
        return replace(s, content=v)  # Actual immutable decoded string retained.
    if k == "resume":
        return replace(s, data=(CONTENTS.index(v), s.data[1])) if v == s.content else None
    if k == "cycle":
        if profile != "cycle" or s.cycle[(t + 1) % 3] != v:
            return None
        return replace(s, cycle=tuple(1 if i == t else bit for i, bit in enumerate(s.cycle)))
    data = list(s.data)
    if k == "pair":
        data = [v & 1, v >> 1]
    else:
        data[t] = v if k == "set" else 1 - data[t]
    return replace(s, data=tuple(data))


class Boundary:
    def __init__(self, profile):
        if profile not in ("independent", "coupled", "exclusive", "cycle"):
            raise ValueError("unknown profile")
        self.profile, self.state = profile, View()
        self.lock = threading.Lock()

    def resolve(self, context, q, gate=lambda stage: None):
        with self.lock:
            if q is None or q.kind == "read":
                return {"outcome": "deny" if q is None else "read", "state": asdict(self.state)}
            successor = candidate(self.state, context, q, self.profile)
            admitted = successor is not None and valid(successor, self.profile)
            gate("validated")
            if admitted:
                self.state = successor  # Sole post-bootstrap protected publication.
            reply = {"outcome": "commit" if admitted else "deny", "state": asdict(self.state)}
        gate("published")
        return reply


def serve(config):
    boundary = Boundary(config["profile"])
    gate_config = config.get("gate")  # Trusted test bootstrap only; no wire control API.
    gate_used = threading.Event()

    def handle(lane, context, fd):
        def gate(stage):
            if (gate_config and not gate_used.is_set() and gate_config["lane"] == lane
                    and gate_config["kind"] == q.kind and gate_config["stage"] == stage):
                gate_used.set()
                os.write(gate_config["event_fd"], b"G")
                os.read(gate_config["release_fd"], 1)

        with socket.socket(fileno=fd) as conn, conn.makefile("rb") as incoming:
            while True:
                raw = incoming.readline(MAX_FRAME + 1)
                if not raw or len(raw) > MAX_FRAME or not raw.endswith(b"\n"):
                    return  # Incomplete/oversized proposal has no protected effect.
                try:
                    q = decode(raw)
                except (ValueError, TypeError, RecursionError):
                    q = None
                if q is not None:
                    gate("received")
                reply = boundary.resolve(context, q, gate)
                try:
                    conn.sendall(json.dumps(reply).encode() + b"\n")
                except (BrokenPipeError, ConnectionResetError):
                    return  # Lost acknowledgement does not undo publication.

    threads = []
    for lane, (context, fd) in enumerate(config["channels"]):
        if context not in (-1, 0, 1, 2, 3):
            raise ValueError("invalid trusted channel association")
        thread = threading.Thread(target=handle, args=(lane, context, fd), daemon=True)
        thread.start()
        threads.append(thread)
    print("ready", flush=True)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    serve(json.loads(sys.argv[1]))
