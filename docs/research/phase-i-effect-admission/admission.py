"""Disposable commit-point experiment. Fixed test import is NOT native authority."""
from contextlib import contextmanager, ExitStack
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CAPTURE = HERE.parent / "phase-i-sol-integration/evidence/sources"
L5_SOURCE = CAPTURE / "l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py"
sys.path.insert(0, str(L5_SOURCE.parent))
spec = importlib.util.spec_from_file_location("admission_l5", L5_SOURCE)
l5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l5)
FIELDS = {"identity_genesis", "created_by", "project", "consumer_evidence"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate-key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def identity(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("symlink-trust-root")
    value = path.stat()
    return [value.st_dev, value.st_ino]


class Denied(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Denied(reason)


@contextmanager
def transaction(path):
    # mode=rw prevents recovery/bootstrap from creating a missing authority store.
    db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=rw", uri=True,
                         isolation_level=None, timeout=.15)
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
    finally:
        if db.in_transaction:
            db.execute("ROLLBACK")  # Admission is a read, not a new accepted fact.
        db.close()


class Admission:
    def __init__(self, config):
        require(config.get("profile") == "experimental-import-v1" and config.get("test_only") is True,
                "unsupported-import-profile")
        self.config = config
        self.trace = []

    def event(self, kind, **fields):
        self.trace.append(dict(ns=time.monotonic_ns(), kind=kind, **fields))

    def gate(self, stage):
        if self.config.get("gate") == stage:
            value = dict(event="GATE", stage=stage, pid=os.getpid(), ns=time.monotonic_ns())
            print(canonical(value), flush=True)
            require(sys.stdin.readline().strip() == "continue", "gate-not-continued")

    def roots(self):
        for path, expected in self.config["custody"]:
            require(identity(path) == expected, "changed-trust-root:" + path)

    @contextmanager
    def guard(self, effect):
        append_started = False
        try:
            envelope = decode(effect["payload"])
            c = self.config
            require(isinstance(envelope, dict), "invalid-envelope")
            require(set(envelope) == {"kind", "import_id", "epoch", "pair", "l5", "request_id"},
                    "invalid-envelope-fields")
            require(envelope["kind"] == "use-current-descendant", "unsupported-effect-kind")
            require(envelope["import_id"] == c["import_id"] and envelope["epoch"] == c["epoch"],
                    "wrong-import-or-epoch")
            require(isinstance(envelope["request_id"], str) and bool(envelope["request_id"])
                    and envelope["request_id"] == effect["request_id"], "request-identity-mismatch")
            pair = envelope["pair"]
            require(isinstance(pair, dict) and set(pair) == {"accepted_content", "required"}
                    and isinstance(pair["accepted_content"], str)
                    and isinstance(pair["required"], dict) and set(pair["required"]) == FIELDS
                    and all(isinstance(v, str) for v in pair["required"].values()), "invalid-pair")
            require(pair == c["pair"], "unregistered-evidence-world")
            self.gate("before-admission")
            with ExitStack() as stack:
                self.roots()
                f1 = stack.enter_context(transaction(c["f1"]))
                fd = os.open(c["l5_lock"], os.O_RDWR | os.O_NOFOLLOW)
                stack.callback(os.close, fd)
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # close(fd) releases this request's exclusive lock on every exit/kill.
                inv = stack.enter_context(transaction(c["l6"]))
                self.roots()

                root, profile, version, view_raw = f1.execute(
                    "SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone()
                view = decode(view_raw)
                obs = f1.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()
                require(root == "work" and profile == "independent" and version == 1,
                        "wrong-f1-interpretation")
                require(obs is not None and decode(obs[0]) == pair
                        and view["content"] == pair["accepted_content"], "f1-selected-pair-mismatch")
                retained = [decode(row[0]) for row in f1.execute("SELECT record FROM retained_observations")]
                require(pair in retained, "f1-pair-not-retained")

                l5root = Path(c["l5_root"])
                selector, state = l5.load_current(l5root)
                require(isinstance(state, dict) and type(state.get("schema")) is int
                        and state["schema"] == 1, "unsupported-l5-interpretation")
                raw_record = (l5root / "protected" / selector).read_bytes()
                generation = dict(selector=selector, sha256=sha(raw_record))
                require(envelope["l5"] == generation, "stale-l5-generation")
                require(l5.graph_valid(state) and l5.enabled(state, "D", "W-L5")
                        and "write" in l5.permissions(state, "D"), "l5-current-path-denied")
                contents = state["work_units"]["C"]["accepted_contents"]
                require(len(contents) == 1, "unsupported-l5-contents")
                meta = contents[0]
                content = pair["accepted_content"].encode()
                require(meta["identity"] == c["import_id"] and meta["accepted_pair"] == pair,
                        "l5-import-binding-mismatch")
                require(l5.verified_content(l5root, meta) == content, "l5-content-mismatch")

                require(inv.execute("SELECT live,sealed FROM unit").fetchall() == [(1, 1)],
                        "l6-unit-not-live-sealed")
                rows = inv.execute("SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
                live = {row[0]: row for row in rows if not row[4]}
                require(c["l6_name"] in live, "l6-dependent-disposed-or-missing")
                expected = (c["l6_name"], "accepted", sha(content), len(content), 0)
                require(live[c["l6_name"]] == expected, "l6-dependent-binding-mismatch")
                objects = Path(c["l6"]).parent / "objects"
                files = list(objects.iterdir())
                require(all(p.is_file() and not p.is_symlink() for p in files), "unsupported-l6-material")
                require({p.name for p in files} <= {row[0] for row in rows}, "l6-unknown-material")
                for name, kind, digest, size, disposed in rows:
                    if not disposed:
                        raw = (objects / name).read_bytes()
                        require(sha(raw) == digest and len(raw) == size, "l6-live-integrity-mismatch")
                require((objects / c["l6_name"]).read_bytes() == content, "l6-content-mismatch")
                certificate = dict(profile=c["profile"], test_only=True, import_id=c["import_id"],
                                   epoch=c["epoch"], pair_sha256=sha(canonical(pair).encode()),
                                   l5=generation, descendant="D", ingress="W-L5",
                                   l6_name=c["l6_name"], authorization_point="local-journal-append")
                self.event("admitted-view", certificate=certificate)
                self.gate("guarded")
                append_started = True
                yield certificate
                self.event("local-append-returned", request_id=effect["request_id"])
                self.gate("after-append")
        except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as error:
            if append_started:
                # An append failure may have written a prefix or a whole effect.
                # Never relabel it as a no-effect admission denial.
                self.event("append-or-postappend-failed", error=type(error).__name__, reason=str(error))
                raise OSError("local-append-outcome-requires-recovery:" + str(error)) from error
            self.event("denied-or-failed", error=type(error).__name__, reason=str(error))
            if isinstance(error, Denied):
                raise
            raise Denied(type(error).__name__ + ":" + str(error)) from error
