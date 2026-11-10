"""Experimental native F3 issuer over actual L5 selection and L6 inventory."""
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CAPTURE = HERE.parent / "phase-i-sol-integration/evidence/sources"
L5PATH = CAPTURE / "l5/research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_integrated.py"
L6PATH = CAPTURE / "l6/research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/store.py"
PROFILE = "native-f3-owner-v1"
FIELDS = {"identity_genesis", "created_by", "project", "consumer_evidence"}


def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


l5 = load("owned_native_l5", L5PATH)
l6 = load("owned_native_l6", L6PATH)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-json-key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def identity(path):
    path = Path(path)
    require(not path.is_symlink(), "symlink-authority-root")
    st = path.stat()
    return [st.st_dev, st.st_ino]


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_f1_pair(cx):
    row = cx.execute("SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone()
    require(row is not None and row[:3] == ("work", "independent", 1), "unsupported-f1-view")
    current = cx.execute("SELECT record FROM consumer_observations WHERE id=1").fetchone()
    require(current is not None, "missing-f1-pair")
    pair = decode(current[0])
    require(isinstance(pair, dict) and set(pair) == {"accepted_content", "required"}
            and isinstance(pair["accepted_content"], str)
            and isinstance(pair["required"], dict) and set(pair["required"]) == FIELDS
            and all(isinstance(v, str) for v in pair["required"].values()), "malformed-f1-pair")
    require(decode(row[3])["content"] == pair["accepted_content"], "f1-subject-mismatch")
    require(pair in [decode(r[0]) for r in cx.execute("SELECT record FROM retained_observations")],
            "f1-pair-not-retained")
    return pair


def publish(root, state, event):
    protected = root / "protected"
    numbers = [int(p.name[7:13]) for p in protected.iterdir()
               if re.fullmatch(r"record-[0-9]{6}\.json", p.name)]
    number = max(numbers, default=0) + 1
    require(number <= 999999, "native-record-capacity-exhausted")
    state["events"].append(event)
    name = f"record-{number:06d}.json"
    raw = (canonical(state) + "\n").encode()
    require(len(raw) <= 262144, "native-record-size-exhausted")
    temp = protected / (name + ".tmp")
    with temp.open("xb") as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, protected / name)
    sync_directory(protected)
    selector = protected / "CURRENT.tmp"
    with selector.open("wb") as stream:
        stream.write((name + "\n").encode()); stream.flush(); os.fsync(stream.fileno())
    os.replace(selector, protected / "CURRENT")
    sync_directory(protected)
    return name, digest(raw)


# Actual original manager transitions call this storage helper. The policy,
# current-state comparison, move/latent ceilings and activation remain original.
l5.commit = publish


def letters(number):
    out = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        out = chr(97 + remainder) + out
    return "object" + out


class Owner:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.selected()

    @classmethod
    def establish(cls, root, f1_db, created_by, project):
        root, f1_db = Path(root), Path(f1_db).resolve()
        require(f1_db.is_file() and created_by and project, "invalid-native-bootstrap-input")
        root.mkdir(mode=0o700)
        lock = root / "management-writer.lock"
        fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600); os.close(fd)
        protected = root / "protected"
        l6.bootstrap(protected)
        domain = "domain-" + uuid.uuid4().hex
        units = {}
        for key, parent, grants in (("P", None, ["read", "write"]),
                                     ("Q", None, ["read"]), ("C", "P", ["read", "write"]),
                                     ("D", "C", ["read", "write"])):
            units[key] = dict(id=key, parent=parent, grants=grants, active=False,
                              sealed=True, accepted_contents=[])
        units["D"]["depends_on"] = ["C"]
        state = dict(schema=1, current_ingress=None, work_units=units, events=[], native_owner=dict(
            profile=PROFILE, domain_id=domain, genesis=domain, created_by=created_by, project=project,
            epoch=1, source=dict(db=str(f1_db), identity=identity(f1_db)),
            inventory=dict(root="protected", identity=identity(protected)),
            custody=dict(root=identity(root), lock=identity(lock)), lifecycle="live",
            children=dict(D="live"), registrations=[], selected=None, effects={}, sink_binding=None))
        require(l5.graph_valid(state), "native-initial-graph-invalid")
        publish(root, state, dict(op="native-establish-domain", domain_id=domain))
        sync_directory(root)
        return cls(root)

    def selected(self):
        name = (self.root / "protected/CURRENT").read_text().strip()
        require(re.fullmatch(r"record-[0-9]{6}\.json", name), "unsupported-native-selector")
        state = decode((self.root / "protected" / name).read_bytes())
        require(type(state.get("schema")) is int and state["schema"] == 1
                and l5.graph_valid(state), "unsupported-native-graph")
        owner = state.get("native_owner", {})
        require(owner.get("profile") == PROFILE and owner.get("lifecycle") in ("live", "removed")
                and type(owner.get("epoch")) is int and 0 < owner["epoch"] < 2**63
                and owner.get("children", {}).get("D") in ("live", "disposed"),
                "unsupported-native-owner")
        require(owner["custody"]["root"] == identity(self.root)
                and owner["custody"]["lock"] == identity(self.root / "management-writer.lock")
                and owner["inventory"]["identity"] == identity(self.root / "protected")
                and owner["source"]["identity"] == identity(owner["source"]["db"]),
                "native-authority-root-changed")
        return name, state

    def view(self):
        selector, state = self.selected()
        return dict(selector=selector, state=state,
                    generation=dict(selector=selector, sha256=digest(
                        (self.root / "protected" / selector).read_bytes())),
                    inventory=l6.snapshot(self.root / "protected"))

    @contextmanager
    def locked(self):
        _selector, initial = self.selected()
        source = initial["native_owner"]["source"]
        f1 = sqlite3.connect(Path(source["db"]).as_uri() + "?mode=rw", uri=True,
                             isolation_level=None, timeout=.15)
        fd = None; inventory = None
        try:
            f1.execute("BEGIN IMMEDIATE")
            fd = os.open(self.root / "management-writer.lock", os.O_RDWR | os.O_NOFOLLOW)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            selector, state = self.selected()
            require(state["native_owner"]["source"] == source, "native-source-retargeted")
            inventory = l6.Store(self.root / "protected")
            inventory.cx.execute("BEGIN IMMEDIATE")
            for registration in state["native_owner"]["registrations"]:
                if registration["status"] != "live": continue
                meta = registration["metadata"]
                l5.verified_content(self.root, meta)
                row = inventory.cx.execute(
                    "SELECT sha256,size,disposed FROM dependencies WHERE name=?",
                    (Path(meta["object"]).name,)).fetchone()
                require(row == (meta["sha256"], meta["size"], 0),
                        "native-live-registration-inventory-mismatch")
            yield Session(self, f1, inventory, selector, state)
        finally:
            if inventory is not None:
                if inventory.cx.in_transaction: inventory.cx.execute("ROLLBACK")
                inventory.cx.close()
            if fd is not None: os.close(fd)
            if f1.in_transaction: f1.execute("ROLLBACK")
            f1.close()

    def apply(self, request):
        if request.get("op") == "read": return dict(result="READ", snapshot=self.view())
        with self.locked() as session:
            return session.apply(request)


class Session:
    def __init__(self, owner, f1, inventory, selector, state):
        self.owner = owner; self.f1 = f1; self.inventory = inventory
        self.selector = selector; self.state = state

    @property
    def native(self): return self.state["native_owner"]

    def commit(self, event):
        self.selector, _digest = publish(self.owner.root, self.state, event)
        return self.selector

    def gate(self, request, phase):
        if request.get("gate") == phase:
            print(canonical(dict(event="GATE", phase=phase, pid=os.getpid(), selector=self.selector)), flush=True)
            require(sys.stdin.readline().strip() == "continue", "gate-not-continued")

    def native_inventory(self, request):
        # Keep F1/flock held across the original native L6 COMMIT boundary.
        if self.inventory.cx.in_transaction: self.inventory.cx.execute("ROLLBACK")
        try:
            return self.inventory.apply(request)
        finally:
            if not self.inventory.cx.in_transaction: self.inventory.cx.execute("BEGIN IMMEDIATE")

    def sealed(self):
        return self.state["current_ingress"] is None and all(
            not u["active"] and u["sealed"] for u in self.state["work_units"].values())

    def pending(self): return any(e["status"] != "published" for e in self.native["effects"].values())

    def reserve_effect(self, request_id, payload_sha256):
        require(request_id not in self.native["effects"], "native-effect-already-reserved")
        self.native["effects"][request_id] = dict(payload_sha256=payload_sha256, status="reserved")
        self.commit(dict(op="native-effect-reserved", request_id=request_id))

    def record_local_effect(self, request_id, seq):
        record = self.native["effects"][request_id]
        require(record["status"] == "reserved" and type(seq) is int, "invalid-native-local-effect")
        record.update(status="local", seq=seq)
        self.commit(dict(op="native-effect-locally-accepted", request_id=request_id, seq=seq))

    def apply(self, q):
        op = q["op"]
        if op == "recover":
            require(self.native["lifecycle"] == "live", "native-domain-removed")
            self._seal()
            self.commit(dict(op="native-recover-sealed"))
            return self.reply()
        require(self.native["lifecycle"] == "live", "native-domain-removed")
        if op == "accept":
            require(self.sealed() and self.native["children"]["D"] == "live", "accept-requires-live-sealed-domain")
            pair = read_f1_pair(self.f1)
            if q.get("expected_pair_sha256") is not None:
                require(q["expected_pair_sha256"] == digest(canonical(pair).encode()), "f1-world-comparison-mismatch")
            prior = next((r for r in self.native["registrations"] if r["id"] == self.native["selected"]), None)
            if prior and prior["status"] == "live" and prior["pair"] == pair:
                return self.reply(registration=prior, duplicate=True)
            count = len(self.native["registrations"]) + 1
            require(self.native["epoch"] < 2**63 - 1, "native-epoch-exhausted")
            name = letters(count)
            result = self.native_inventory(dict(op="put", name=name, kind="candidate", payload=pair["accepted_content"]))
            require(result["result"] == "COMMITTED", "native-material-preparation-refused")
            self.gate(q, "material-prepared")
            registration_id = self.native["domain_id"] + ":" + str(count)
            raw = pair["accepted_content"].encode()
            meta = dict(identity=registration_id, accepted_pair=pair, object="objects/" + name,
                        sha256=digest(raw), size=len(raw))
            require(l5.verified_content(self.owner.root, meta) == raw, "prepared-input-substitution")
            registration = dict(id=registration_id, pair=pair, metadata=meta, status="live")
            self.native["registrations"].append(registration)
            self.native["selected"] = registration_id
            self.native["epoch"] += 1
            for unit in ("C", "D"): self.state["work_units"][unit]["accepted_contents"] = [meta]
            self.commit(dict(op="native-accept-f1-subject", registration_id=registration_id))
            self.gate(q, "acceptance-selected")
            return self.reply(registration=registration, duplicate=False)
        if op == "seal":
            self._seal(); self.commit(dict(op="native-seal")); return self.reply()
        if op in ("move", "activate"):
            require(self.native["children"]["D"] == "live", "native-child-disposed")
            client, server = socket.socketpair()
            request = dict(op="authorize_" + op, authorized_by="initial-manager", credential=l5.CREDENTIAL)
            if op == "move": request.update(child="C", destination="Q")
            try:
                _received, reply = l5.manager_roundtrip(client, server, request, self.state, self.owner.root)
                require(json.loads(client.makefile("rb", buffering=0).readline()) == reply, "native-manager-wire-mismatch")
                self.selector, self.state = self.owner.selected()
                return dict(reply, snapshot=self.owner.view())
            finally:
                client.close(); server.close()
        require(self.sealed(), "disposition-requires-sealed-domain")
        if op == "dispose_child":
            require(q.get("unit", "D") == "D" and self.native["children"]["D"] == "live", "not-live-native-child")
            require(not self.pending(), "pending-in-domain-effect")
            self.native["children"]["D"] = "disposed"
            self.state["work_units"]["D"]["accepted_contents"] = []
            self.commit(dict(op="native-dispose-child", unit="D")); return self.reply()
        if op == "dispose_content":
            require(self.native["children"]["D"] == "disposed" and not self.pending(), "native-dependent-or-effect-remains")
            reg = next((r for r in self.native["registrations"] if r["id"] == q.get("id", q.get("registration_id"))), None)
            require(reg is not None and reg["status"] == "live", "not-live-native-registration")
            reg["status"] = "disposed"
            if self.native["selected"] == reg["id"]:
                self.native["selected"] = None
                self.state["work_units"]["C"]["accepted_contents"] = []
            self.commit(dict(op="native-dispose-content", registration_id=reg["id"]))
            self.gate(q, "disposition-selected")
            result = self.native_inventory(dict(op="dispose", name=Path(reg["metadata"]["object"]).name,
                                                **({"gate": "postcommit"} if q.get("gate") == "inventory-disposed" else {})))
            return self.reply(inventory_reply=result)
        if op == "cleanup":
            for reg in self.native["registrations"]:
                if reg["status"] != "disposed": continue
                name = Path(reg["metadata"]["object"]).name
                row = self.inventory.cx.execute("SELECT disposed FROM dependencies WHERE name=?", (name,)).fetchone()
                if row and not row[0]: self.native_inventory(dict(op="dispose", name=name))
                elif (self.inventory.root / "objects" / name).exists(): self.native_inventory(dict(op="cleanup", name=name))
            return self.reply()
        if op == "remove":
            require(self.native["children"]["D"] == "disposed", "native-child-remains")
            require(not self.pending(), "pending-in-domain-effect")
            require(all(r["status"] == "disposed" for r in self.native["registrations"]), "native-content-remains")
            snapshot = l6.snapshot(self.inventory.root)
            require(not snapshot["files"] and not snapshot["unknown_files"]
                    and not any(not r["disposed"] for r in snapshot["dependencies"]), "native-inventory-not-empty")
            self.native["lifecycle"] = "removed"
            self.commit(dict(op="native-remove-domain"))
            return self.reply(inventory_reply=self.native_inventory(dict(op="remove")))
        raise ValueError("unsupported-native-owner-operation")

    def _seal(self):
        require(self.native["epoch"] < 2**63 - 1, "native-epoch-exhausted")
        self.native["epoch"] += 1
        self.state["current_ingress"] = None
        for unit in self.state["work_units"].values(): unit.update(active=False, sealed=True)

    def reply(self, **fields):
        return dict(result="COMMITTED", snapshot=self.owner.view(), **fields)
