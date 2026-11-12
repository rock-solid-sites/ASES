#!/usr/bin/env python3
"""Reconcile exactly one locally committed native F4 effect.

This is an experimental, owner-root-only recovery command. It reuses the
native owner's attachment and settlement path and the pinned F4 replay parser;
it does not accept publication facts from its caller.
"""
from __future__ import annotations

import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
NATIVE = RESEARCH / "phase-ii-native-ownership"
sys.path.insert(0, str(NATIVE))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("source-module-unavailable:" + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


native_sink = load("native_publication_reconcile_sink", NATIVE / "native_sink.py")
legacy = native_sink.legacy
composed = native_sink.composed
cut_module = composed.admission.cut
managed = cut_module.managed
owner_module = load("native_publication_reconcile_owner", NATIVE / "native_owner.py")
unix_transport = load("native_publication_reconcile_unix", NATIVE / "unix_transport.py")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def identity(path: Path) -> list[int]:
    require(not path.is_symlink(), "symlink-attachment-path")
    info = path.stat()
    return [info.st_dev, info.st_ino]


class ReconcileState(composed.retry.RetryState):
    """RetryState replay plus the existing F4 cut and native witness exchange."""

    def __init__(self, journal: Path, witness_path: Path, witness_root: str):
        self.cut_protocol_log = []
        self.witness_path = witness_path
        self.witness_root = witness_root
        super().__init__(journal, True)

    def cut(self):
        raw = self.journal.read_bytes()
        return dict(authority={
            key: getattr(self, "version" if key == "authority_version" else key)
            for key in cut_module.FIELDS
        }, journal_sha256=digest(raw))

    def exchange(self, path: str, **fields):
        request = dict(root=self.witness_root, nonce=secrets.token_hex(16), **fields)
        entry = dict(path=path, request=request)
        try:
            code, reply = unix_transport.call_unix(self.witness_path, "POST", path, request)
            valid = (code == 200 and isinstance(reply, dict)
                     and reply.get("root") == self.witness_root
                     and reply.get("nonce") == request["nonce"]
                     and type(reply.get("revision")) is int
                     and reply["revision"] > 0)
            entry.update(status=code, response=reply, transport_valid=valid)
        except Exception as error:  # Transport loss is deliberately uncertain.
            entry.update(status=None, response=None, transport_valid=False,
                         transport_error=type(error).__name__)
        self.cut_protocol_log.append(entry)
        return entry

    def check_observed(self, candidate):
        proof = self.exchange("/check", candidate=candidate)
        reply = proof.get("response")
        try:
            cut_module.validate_cut(reply.get("current"))
        except (AttributeError, TypeError, ValueError):
            proof["valid"] = False
            return proof
        proof["valid"] = bool(
            proof["transport_valid"] is True
            and reply.get("allowed") is (reply.get("current") == candidate)
        )
        return proof

    def check_cut(self, candidate):
        proof = self.check_observed(candidate)
        proof["valid"] = bool(proof["valid"] and proof["response"].get("allowed") is True
                              and proof["response"].get("current") == candidate)
        return proof


def _binding(owner):
    snapshot = owner.view()
    native = snapshot["state"]["native_owner"]
    binding = native.get("sink_binding")
    require(isinstance(binding, dict), "missing-native-sink-attachment")
    require(set(binding) == {"journal", "journal_parent_identity", "witness_root", "witness_endpoint"},
            "unsupported-native-sink-attachment")
    journal = Path(binding["journal"])
    endpoint_record = binding["witness_endpoint"]
    require(isinstance(endpoint_record, dict)
            and set(endpoint_record) == {"path", "parent_identity"}, "missing-private-witness-endpoint")
    endpoint = Path(endpoint_record["path"])
    require(journal.is_absolute() and endpoint.is_absolute(), "non-absolute-native-attachment")
    require(isinstance(binding["witness_root"], str) and binding["witness_root"], "invalid-witness-root")
    require(not journal.parent.is_symlink() and identity(journal.parent) == binding["journal_parent_identity"],
            "native-journal-parent-identity-changed")
    require(not endpoint.parent.is_symlink() and identity(endpoint.parent) == endpoint_record["parent_identity"],
            "native-witness-parent-identity-changed")
    endpoint_info = endpoint.lstat()
    require(stat.S_ISSOCK(endpoint_info.st_mode), "native-witness-endpoint-not-unix-socket")
    require(not journal.is_symlink() and journal.is_file(), "native-journal-not-existing-regular-file")
    return snapshot, binding, journal, endpoint


def _lock_writer(journal: Path):
    guard = journal.parent / "sink-writer.lock"
    require(not guard.is_symlink(), "native-writer-guard-symlink")
    before = guard.lstat()
    require(stat.S_ISREG(before.st_mode), "native-writer-guard-not-regular-file")
    fd = os.open(guard, os.O_RDWR | os.O_NOFOLLOW)
    try:
        opened = os.fstat(fd)
        current = guard.lstat()
        require(stat.S_ISREG(opened.st_mode) and (opened.st_dev, opened.st_ino) ==
                (before.st_dev, before.st_ino) == (current.st_dev, current.st_ino),
                "native-writer-guard-identity-changed")
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = guard.lstat()
        require((opened.st_dev, opened.st_ino) == (current.st_dev, current.st_ino),
                "native-writer-guard-identity-changed-after-lock")
        return fd, dict(path=str(guard), device=opened.st_dev, inode=opened.st_ino)
    except BaseException:
        os.close(fd)
        raise


def _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                          original_journal_identity):
    require(not journal.parent.is_symlink() and identity(journal.parent) == original_parent
            and binding["journal_parent_identity"] == original_parent,
            "native-journal-parent-identity-changed")
    require(not journal.is_symlink() and journal.is_file(), "native-journal-replaced")
    require(identity(journal) == original_journal_identity, "native-journal-file-identity-changed")
    require(not endpoint.parent.is_symlink() and identity(endpoint.parent) == original_endpoint_parent
            and binding["witness_endpoint"]["parent_identity"] == original_endpoint_parent,
            "native-witness-parent-identity-changed")
    require(stat.S_ISSOCK(endpoint.lstat().st_mode), "native-witness-endpoint-replaced")


def _validate_local_effect(owner, state, request_id, raw, binding):
    event = state.request_index.get(request_id)
    require(event is not None and state.events and state.events[-1] == event,
            "target-effect-is-not-final-event")
    lines = raw.splitlines(keepends=True)
    require(lines and lines[-1].endswith(b"\n") and len(lines) == len(state.events),
            "journal-not-complete-bounded-replay")
    final = legacy.decode(lines[-1].decode("utf-8"))
    require(final == event and final.get("event") == "effect_accepted",
            "target-effect-is-not-exact-final-line")
    require(state.effects and state.effects[-1] == event
            and sum(1 for item in state.effects if item.get("request_id") == request_id) == 1,
            "target-effect-not-unique-in-replay-index")
    require(event.get("profile") == "flat-managed-v1" and event.get("unit") == "C"
            and event.get("position") == "p" and event.get("check_mode") == "managed-use-current",
            "unsupported-native-effect-profile")
    payload = event.get("payload")
    require(type(payload) is str and digest(payload.encode()) == event.get("payload_sha256"),
            "native-effect-payload-hash-mismatch")
    envelope = legacy.decode(payload)
    require(isinstance(envelope, dict) and set(envelope) ==
            {"kind", "import_id", "epoch", "pair", "l5", "request_id"}
            and envelope.get("kind") == "use-current-descendant"
            and envelope.get("request_id") == request_id, "invalid-native-effect-envelope")
    certificate = event.get("admission")
    fields = {"profile", "native_registration", "domain_id", "import_id", "epoch", "pair_sha256",
              "presented_l5", "l5", "descendant", "authorization_point"}
    require(isinstance(certificate, dict) and set(certificate) == fields
            and certificate.get("profile") == native_sink.PROFILE
            and certificate.get("native_registration") is True
            and certificate.get("descendant") == "D"
            and certificate.get("authorization_point") == "local-journal-append"
            and certificate.get("import_id") == envelope.get("import_id")
            and certificate.get("epoch") == envelope.get("epoch")
            and certificate.get("l5") == envelope.get("l5"), "invalid-native-admission-binding")
    require(type(envelope.get("epoch")) is int and envelope["epoch"] > 0,
            "invalid-native-effect-epoch")

    with owner.locked() as session:
        native = session.state["native_owner"]
        effects = native.get("effects")
        pending = effects.get(request_id) if isinstance(effects, dict) else None
        require(isinstance(pending, dict) and pending.get("status") == "local"
                and pending.get("seq") == event.get("seq")
                and pending.get("payload_sha256") == digest(payload.encode()),
                "native-owner-local-effect-mismatch")
        require([key for key, item in effects.items() if item.get("status") != "published"] == [request_id],
                "other-or-unsupported-native-pending-effect")
        require(certificate.get("domain_id") == native.get("domain_id"),
                "native-effect-wrong-domain")
        registration = next((item for item in native.get("registrations", [])
                             if item.get("id") == envelope.get("import_id")), None)
        require(registration is not None and registration.get("status") == "live"
                and registration.get("pair") == envelope.get("pair"),
                "native-effect-registration-world-mismatch")
        pair = registration["pair"]
        require(certificate.get("pair_sha256") == digest(legacy.canonical(pair).encode()),
                "native-effect-pair-hash-mismatch")
        row = session.f1.execute("SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone()
        retained = [legacy.decode(item[0]) for item in session.f1.execute(
            "SELECT record FROM retained_observations")]
        require(row is not None and row[0] == "work" and row[1] == "independent" and row[2] == 1
                and pair in retained, "native-source-retained-world-mismatch")
        historical_l5 = certificate.get("l5")
        require(isinstance(historical_l5, dict) and set(historical_l5) == {"selector", "sha256"}
                and re.fullmatch(r"record-[0-9]{6}\.json", historical_l5.get("selector", ""))
                and re.fullmatch(r"[0-9a-f]{64}", historical_l5.get("sha256", ""))
                and certificate.get("presented_l5") == historical_l5,
                "native-effect-owner-generation-mismatch")
        historical_path = owner.root / "protected" / historical_l5["selector"]
        require(not historical_path.is_symlink() and historical_path.is_file()
                and digest(historical_path.read_bytes()) == historical_l5["sha256"],
                "native-effect-historical-owner-record-missing")
        historical_state = legacy.decode(historical_path.read_bytes())
        historical_native = historical_state.get("native_owner", {})
        historical_registration = next((item for item in historical_native.get("registrations", [])
                                         if item.get("id") == registration["id"]), None)
        require(historical_native.get("domain_id") == native.get("domain_id")
                and historical_registration is not None
                and historical_registration.get("pair") == pair,
                "native-effect-historical-registration-mismatch")
        metadata = registration["metadata"]
        content = pair["accepted_content"].encode()
        require(metadata.get("identity") == registration["id"]
                and metadata.get("accepted_pair") == pair
                and native_sink.legacy.l5.verified_content(owner.root, metadata) == content,
                "native-effect-owned-material-mismatch")
        item_name = Path(metadata["object"]).name
        catalog = session.inventory.cx.execute(
            "SELECT sha256,size,disposed FROM dependencies WHERE name=?", (item_name,)).fetchone()
        require(catalog == (metadata["sha256"], metadata["size"], 0)
                and digest(content) == metadata["sha256"] and len(content) == metadata["size"],
                "native-effect-inventory-binding-mismatch")
        attachment = native.get("sink_binding") or {}
        require(attachment == binding and attachment.get("journal") == str(journal.resolve())
                and attachment.get("journal_parent_identity") == legacy.identity(journal.parent),
                "native-settlement-wrong-attachment")
    return event


def _protocol_valid(entry):
    return entry.get("transport_valid") is True


def reconcile(owner_root: Path, request_id: str, test_gate=False):
    require(type(request_id) is str and request_id, "nonempty-request-id-required")
    owner = owner_module.Owner(owner_root)
    _snapshot, binding, journal, endpoint = _binding(owner)
    original_parent = identity(journal.parent)
    original_endpoint_parent = identity(endpoint.parent)
    original_journal_identity = identity(journal)
    fd, writer_guard = _lock_writer(journal)
    try:
        # Re-read the protected attachment after acquiring the real F4 writer
        # guard so an active sink/reconciler cannot race this parser.
        _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                              original_journal_identity)
        raw = journal.read_bytes()
        require(len(raw) <= 65536 and raw.endswith(b"\n"), "journal-outside-bounded-complete-profile")
        composed.admission.cut.ORIGINAL_STATE = composed.retry.RetryState
        state_type = native_sink.continuation.cold.state_type(composed.retry.RetryState, True)
        state = state_type(journal)
        require(state.next_seq > 1 and len(state.events) <= 65536,
                "empty-or-invalid-native-journal")
        require(digest(journal.read_bytes()) == digest(raw), "native-journal-changed-during-replay")
        event = _validate_local_effect(owner, state, request_id, raw, binding)
        full_cut = dict(authority={key: getattr(state, "version" if key == "authority_version" else key)
                                   for key in cut_module.FIELDS}, journal_sha256=digest(raw))
        cut_module.validate_cut(full_cut)
        prefix = b"".join(state_line for state_line in raw.splitlines(keepends=True)[:-1])
        prior_cut = dict(authority=full_cut["authority"], journal_sha256=digest(prefix))
        cut_module.validate_cut(prior_cut)
        sink = ReconcileState(journal, endpoint, binding["witness_root"])
        require(sink.request_index.get(request_id) == event and sink.cut() == full_cut,
                "retry-state-replay-disagreement")
        sink_protocol_initial = len(sink.cut_protocol_log)
        sink.lock.acquire()
        sink_lock_acquired = True

        _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                              original_journal_identity)
        observed = sink.check_observed(full_cut)
        require(_protocol_valid(observed) and observed.get("valid") is True,
                "unresolved-witness-observation")
        response = observed["response"]
        current = response["current"]
        require(current == full_cut or current == prior_cut,
                "witness-cut-not-exact-target-or-preceding-cut")
        cas_count = 0
        publication_reply_lost = False
        if current == prior_cut:
            _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                                  original_journal_identity)
            cas = sink.exchange("/publish", previous=prior_cut, candidate=full_cut,
                                expected_revision=response["revision"])
            cas_count = 1
            if not _protocol_valid(cas):
                publication_reply_lost = True
            elif cas["response"].get("published") is not True:
                # A witnessed rejection is not retried. A fresh check can still
                # establish whether the target is now current.
                publication_reply_lost = False

        # Whether the initial observation was already at target or a single CAS
        # was attempted, require one fresh nonce-bearing check before settlement.
        _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                              original_journal_identity)
        confirmation = sink.check_cut(full_cut)
        if not (_protocol_valid(confirmation) and confirmation.get("valid") is True):
            return dict(status="unresolved-publication", reason="target-not-confirmed-by-fresh-check",
                        request_id=request_id, event_seq=event["seq"], cas_count=cas_count,
                        publication_reply_lost=publication_reply_lost,
                        writer_guard=writer_guard, protocol=sink.cut_protocol_log[sink_protocol_initial:])
        if test_gate:
            print(json.dumps(dict(event="GATE", phase="after-confirmed-publication-before-settlement",
                                  pid=os.getpid(), request_id=request_id), sort_keys=True), flush=True)
            require(sys.stdin.readline() == "continue\n", "test-gate-not-continued")

        # Release every Owner.locked section before invoking the native helper:
        # it takes Owner.locked itself. Pending local status keeps disposal blocked.
        _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                              original_journal_identity)
        require(digest(journal.read_bytes()) == full_cut["journal_sha256"],
                "native-journal-changed-before-settlement")
        settlement = native_sink.settle_from_native_sink(owner, sink, request_id)
        status = settlement.get("status")
        result_status = "published" if status == "published" else "unresolved-publication"
        return dict(status=result_status, settlement=settlement, request_id=request_id,
                    event_seq=event["seq"], cas_count=cas_count,
                    publication_reply_lost=publication_reply_lost,
                    writer_guard=writer_guard, protocol=sink.cut_protocol_log[sink_protocol_initial:])
    finally:
        if "sink_lock_acquired" in locals() and sink_lock_acquired:
            sink.lock.release()
        os.close(fd)


def main(argv):
    test_gate = False
    if len(argv) == 5 and argv[3] == "--test-gate":
        if argv[4] != "after-confirmed-publication-before-settlement":
            raise SystemExit("usage: reconcile.py OWNER_ROOT REQUEST_ID [--test-gate after-confirmed-publication-before-settlement]")
        test_gate = True
    elif len(argv) != 3:
        raise SystemExit("usage: reconcile.py OWNER_ROOT REQUEST_ID [--test-gate after-confirmed-publication-before-settlement]")
    try:
        result = reconcile(Path(argv[1]), argv[2], test_gate)
        print(json.dumps(dict(event="native-publication-reconcile", **result), sort_keys=True), flush=True)
        return 0 if result.get("status") == "published" else 1
    except BlockingIOError:
        result = dict(status="refused-writer-guard-busy", reason="existing F4 writer guard is held")
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, RuntimeError) as error:
        result = dict(status="refused", reason=str(error), error=type(error).__name__)
    print(json.dumps(dict(event="native-publication-reconcile", **result), sort_keys=True), flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
