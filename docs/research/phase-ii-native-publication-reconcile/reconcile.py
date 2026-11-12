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

    def __init__(self, journal: Path, witness_path: Path, witness_root: str, test_gate=False):
        self.cut_protocol_log = []
        self.witness_path = witness_path
        self.witness_root = witness_root
        self.test_gate = test_gate
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
            valid = (isinstance(reply, dict)
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
            and proof.get("status") == 200
            and reply.get("allowed") is (reply.get("current") == candidate)
        )
        return proof

    def check_cut(self, candidate):
        proof = self.check_observed(candidate)
        proof["valid"] = bool(proof["valid"] and proof["response"].get("allowed") is True
                              and proof["response"].get("current") == candidate)
        if proof["valid"]:
            self.target_confirmed = True
        if proof["valid"] and self.test_gate:
            print(json.dumps(dict(event="GATE", phase="after-confirmed-publication-before-settlement",
                                  pid=os.getpid(), request_id=self.request_id), sort_keys=True), flush=True)
            require(sys.stdin.readline() == "continue\n", "test-gate-not-continued")
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


def _validate_local_effect(owner, state, request_id, raw, binding, allow_reserved=False):
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
            and certificate.get("presented_l5") == envelope.get("l5"),
            "invalid-native-admission-binding")
    require(type(envelope.get("epoch")) is int and envelope["epoch"] > 0,
            "invalid-native-effect-epoch")

    with owner.locked() as session:
        native = session.state["native_owner"]
        effects = native.get("effects")
        pending = effects.get(request_id) if isinstance(effects, dict) else None
        permitted = ("local", "published", "reserved") if allow_reserved else ("local", "published")
        require(isinstance(pending, dict) and pending.get("status") in permitted
                and (pending.get("seq") == event.get("seq") if pending.get("status") != "reserved"
                     else "seq" not in pending)
                and pending.get("payload_sha256") == digest(payload.encode()),
                "native-owner-local-effect-mismatch")
        other_pending = [key for key, item in effects.items() if item.get("status") != "published"]
        require((other_pending == [request_id] if pending["status"] in ("local", "reserved")
                 else not other_pending),
                "other-or-unsupported-native-pending-effect")
        require(certificate.get("domain_id") == native.get("domain_id"),
                "native-effect-wrong-domain")
        if pending["status"] in ("local", "reserved"):
            registration = next((item for item in native.get("registrations", [])
                                 if item.get("id") == envelope.get("import_id")), None)
            require(registration is not None and registration.get("status") == "live"
                    and registration.get("pair") == envelope.get("pair"),
                    "native-effect-registration-world-mismatch")
            pair = registration["pair"]
            require(certificate.get("pair_sha256") == digest(legacy.canonical(pair).encode()),
                    "native-effect-pair-hash-mismatch")
            source = session.f1.execute("SELECT root,profile,version FROM kernel WHERE id=1").fetchone()
            retained = [legacy.decode(item[0]) for item in session.f1.execute(
                "SELECT record FROM retained_observations")]
            require(source == ("work", "independent", 1) and pair in retained,
                    "native-source-retained-world-mismatch")
            historical_l5 = certificate.get("l5")
            presented_l5 = certificate.get("presented_l5")
            for generation in (presented_l5, historical_l5):
                require(isinstance(generation, dict) and set(generation) == {"selector", "sha256"}
                        and re.fullmatch(r"record-[0-9]{6}\.json", generation.get("selector", ""))
                        and re.fullmatch(r"[0-9a-f]{64}", generation.get("sha256", "")),
                        "native-effect-owner-generation-mismatch")
                generation_path = owner.root / "protected" / generation["selector"]
                require(not generation_path.is_symlink() and generation_path.is_file()
                        and digest(generation_path.read_bytes()) == generation["sha256"],
                        "native-effect-historical-owner-record-missing")
            historical_path = owner.root / "protected" / historical_l5["selector"]
            historical_state = legacy.decode(historical_path.read_bytes())
            historical_native = historical_state.get("native_owner", {})
            historical_registration = next((item for item in historical_native.get("registrations", [])
                                             if item.get("id") == registration["id"]), None)
            reserved = historical_native.get("effects", {}).get(request_id)
            require(historical_native.get("domain_id") == native.get("domain_id")
                    and historical_native.get("epoch") == certificate.get("epoch")
                    and historical_native.get("selected") == registration["id"]
                    and historical_native.get("lifecycle") == "live"
                    and historical_registration is not None
                    and historical_registration.get("status") == "live"
                    and historical_registration.get("pair") == pair
                    and isinstance(reserved, dict) and reserved.get("status") == "reserved"
                    and reserved.get("payload_sha256") == digest(payload.encode()),
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
        require(attachment == binding and attachment.get("journal") == str(state.journal.resolve())
                and attachment.get("journal_parent_identity") == legacy.identity(state.journal.parent),
                "native-settlement-wrong-attachment")
        require(pending["status"] != "published" or native.get("lifecycle") in ("live", "removed"),
                "unsupported-published-native-owner-state")
    return event, pending["status"]


def _record_reserved_local_observation(owner, state, request_id, event, raw, binding):
    """Promote only the parsed final journal event through the original callback."""
    journal = state.journal
    require(journal.read_bytes() == raw and event == state.request_index.get(request_id)
            and state.events and state.events[-1] == event,
            "native-journal-changed-before-local-observation")
    payload = event["payload"]
    envelope = legacy.decode(payload)
    certificate = event["admission"]
    pair = envelope["pair"]
    attachment_identity = legacy.identity(journal.parent)
    with owner.locked() as session:
        native = session.state["native_owner"]
        effects = native.get("effects", {})
        pending = effects.get(request_id)
        require(isinstance(pending, dict) and pending.get("status") == "reserved"
                and "seq" not in pending
                and pending.get("payload_sha256") == digest(payload.encode()),
                "native-reservation-changed-before-local-observation")
        require([key for key, item in effects.items() if item.get("status") != "published"] == [request_id],
                "other-or-unsupported-native-pending-effect")
        require(certificate.get("domain_id") == native.get("domain_id"),
                "native-effect-wrong-domain")
        registration = next((item for item in native.get("registrations", [])
                             if item.get("id") == envelope.get("import_id")), None)
        require(registration is not None and registration.get("status") == "live"
                and registration.get("pair") == pair,
                "native-effect-registration-world-mismatch")
        retained = [legacy.decode(item[0]) for item in session.f1.execute(
            "SELECT record FROM retained_observations")]
        source = session.f1.execute("SELECT root,profile,version FROM kernel WHERE id=1").fetchone()
        require(source == ("work", "independent", 1) and pair in retained,
                "native-source-retained-world-mismatch")
        require(certificate.get("pair_sha256") == digest(legacy.canonical(pair).encode())
                and envelope.get("l5") == certificate.get("presented_l5"),
                "native-effect-historical-proof-mismatch")
        require((native.get("sink_binding") or {}) == binding
                and binding.get("journal") == str(journal.resolve())
                and binding.get("journal_parent_identity") == attachment_identity,
                "native-settlement-wrong-attachment")
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
        for generation in (certificate["presented_l5"], certificate["l5"]):
            require(isinstance(generation, dict) and set(generation) == {"selector", "sha256"}
                    and re.fullmatch(r"record-[0-9]{6}\.json", generation.get("selector", ""))
                    and re.fullmatch(r"[0-9a-f]{64}", generation.get("sha256", "")),
                    "native-effect-owner-generation-mismatch")
            generation_path = owner.root / "protected" / generation["selector"]
            require(not generation_path.is_symlink() and generation_path.is_file()
                    and digest(generation_path.read_bytes()) == generation["sha256"],
                    "native-effect-historical-owner-record-missing")
        historical_l5 = certificate["l5"]
        reserved_record = owner.root / "protected" / historical_l5["selector"]
        require(not reserved_record.is_symlink() and reserved_record.is_file()
                and digest(reserved_record.read_bytes()) == historical_l5["sha256"],
                "native-effect-historical-owner-record-missing")
        historic = legacy.decode(reserved_record.read_bytes()).get("native_owner", {})
        historic_reg = next((item for item in historic.get("registrations", [])
                             if item.get("id") == registration["id"]), None)
        historic_effect = historic.get("effects", {}).get(request_id)
        require(historic.get("domain_id") == native.get("domain_id")
                and historic.get("epoch") == certificate.get("epoch")
                and historic.get("selected") == registration["id"]
                and historic.get("lifecycle") == "live"
                and historic_reg is not None and historic_reg.get("status") == "live"
                and historic_reg.get("pair") == pair
                and isinstance(historic_effect, dict) and historic_effect.get("status") == "reserved"
                and historic_effect.get("payload_sha256") == digest(payload.encode()),
                "native-effect-historical-registration-mismatch")
        # Existing typed callback: no caller sequence or new status is accepted.
        session.record_local_effect(request_id, event["seq"])
        return session.state["native_owner"]["effects"][request_id]


def _protocol_valid(entry):
    return entry.get("transport_valid") is True


def _run_reconcile(owner_root: Path, request_id: str, test_gate=False,
                   allow_reserved=False, test_gate_local=False):
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
        sink = ReconcileState(journal, endpoint, binding["witness_root"], test_gate)
        sink.request_id = request_id
        sink.target_confirmed = False
        sink.lock.acquire()
        sink_lock_acquired = True
        require(sink.next_seq > 1 and len(sink.events) <= 65536,
                "empty-or-invalid-native-journal")
        require(digest(journal.read_bytes()) == digest(raw), "native-journal-changed-during-replay")
        event, owner_status = _validate_local_effect(owner, sink, request_id, raw, binding,
                                                     allow_reserved=allow_reserved)
        full_cut = sink.cut()
        cut_module.validate_cut(full_cut)
        prefix = b"".join(state_line for state_line in raw.splitlines(keepends=True)[:-1])
        prior_cut = dict(authority=full_cut["authority"], journal_sha256=digest(prefix))
        cut_module.validate_cut(prior_cut)
        require(sink.request_index.get(request_id) == event, "retry-state-replay-disagreement")
        sink_protocol_initial = len(sink.cut_protocol_log)

        _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                              original_journal_identity)
        observed = sink.check_observed(full_cut)
        require(_protocol_valid(observed) and observed.get("valid") is True,
                "unresolved-witness-observation")
        response = observed["response"]
        current = response["current"]
        require(current == full_cut or current == prior_cut,
                "witness-cut-not-exact-target-or-preceding-cut")
        observation_status = None
        if owner_status == "reserved":
            require(allow_reserved, "reserved-native-effect-requires-explicit-observer")
            observation_status = "unknown"
            try:
                _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                                      original_journal_identity)
                require(journal.read_bytes() == raw and sink.cut() == full_cut,
                        "native-journal-changed-before-local-observation")
                observed_owner = _record_reserved_local_observation(owner, sink, request_id, event, raw, binding)
                require(observed_owner.get("status") == "local"
                        and observed_owner.get("seq") == event["seq"],
                        "native-local-observation-selection-unconfirmed")
                owner_status = "local"
                observation_status = "local"
            except Exception as error:
                return dict(status="unresolved-publication", reason=str(error), error=type(error).__name__,
                            request_id=request_id, event_seq=event["seq"], cas_count=0,
                            publication_attempted=False, publication_confirmed=False,
                            observation_attempted=True, observation_status="unknown",
                            settlement_status="not-attempted", publication_reply_lost=False,
                            writer_guard=writer_guard,
                            protocol=sink.cut_protocol_log[sink_protocol_initial:])
            if test_gate_local and current == prior_cut:
                print(json.dumps(dict(event="GATE", phase="after-local-observation-before-publication",
                                      pid=os.getpid(), request_id=request_id), sort_keys=True), flush=True)
                try:
                    require(sys.stdin.readline() == "continue\n", "local-observation-test-gate-not-continued")
                except Exception as error:
                    return dict(status="unresolved-publication", reason=str(error), error=type(error).__name__,
                                request_id=request_id, event_seq=event["seq"], cas_count=0,
                                publication_attempted=False, publication_confirmed=False,
                                observation_attempted=True, observation_status="local",
                                settlement_status="not-attempted", publication_reply_lost=False,
                                writer_guard=writer_guard,
                                protocol=sink.cut_protocol_log[sink_protocol_initial:])
        if owner_status == "published" and current != full_cut:
            return dict(status="unresolved-publication", reason="published-owner-lacks-current-target-proof",
                        request_id=request_id, event_seq=event["seq"], cas_count=0,
                        publication_attempted=False, publication_confirmed=False,
                        observation_attempted=False, observation_status=None,
                        settlement_status="not-attempted", publication_reply_lost=False,
                        writer_guard=writer_guard,
                        protocol=sink.cut_protocol_log[sink_protocol_initial:])
        cas_count = 0
        publication_attempted = False
        publication_reply_lost = False
        try:
            if owner_status == "local" and current == prior_cut:
                _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                                      original_journal_identity)
                publication_attempted = True
                cas = sink.exchange("/publish", previous=prior_cut, candidate=full_cut,
                                    expected_revision=response["revision"])
                cas_count = 1
                publication_reply_lost = not _protocol_valid(cas)

            # Release every Owner.locked section before invoking the native
            # helper: it supplies the fresh confirmation check and takes its own
            # owner lock. Pending status keeps disposal blocked across this gap.
            _attachment_unchanged(binding, journal, endpoint, original_parent, original_endpoint_parent,
                                  original_journal_identity)
            require(digest(journal.read_bytes()) == full_cut["journal_sha256"],
                    "native-journal-changed-before-settlement")
            rechecked_event, rechecked_status = _validate_local_effect(owner, sink, request_id, raw, binding)
            require(rechecked_event == event and rechecked_status == owner_status,
                    "native-effect-owner-state-changed-before-settlement")
            settlement = native_sink.settle_from_native_sink(owner, sink, request_id)
            status = settlement.get("status")
            confirmed = sink.target_confirmed
            result_status = "published" if status == "published" else "unresolved-publication"
            return dict(status=result_status, settlement=settlement, request_id=request_id,
                        event_seq=event["seq"], cas_count=cas_count,
                        publication_attempted=publication_attempted,
                        publication_confirmed=confirmed,
                        observation_attempted=observation_status is not None,
                        observation_status=observation_status,
                        settlement_status="published" if status == "published" else "not-confirmed",
                        publication_reply_lost=publication_reply_lost,
                        writer_guard=writer_guard, protocol=sink.cut_protocol_log[sink_protocol_initial:])
        except Exception as error:
            confirmed = sink.target_confirmed
            return dict(status="unresolved-settlement" if confirmed else "unresolved-publication",
                        reason=str(error), error=type(error).__name__, request_id=request_id,
                        event_seq=event["seq"], cas_count=cas_count,
                        publication_attempted=publication_attempted,
                        publication_confirmed=confirmed,
                        observation_attempted=observation_status is not None,
                        observation_status=observation_status,
                        settlement_status="unknown" if confirmed else "not-confirmed",
                        publication_reply_lost=publication_reply_lost,
                        writer_guard=writer_guard, protocol=sink.cut_protocol_log[sink_protocol_initial:])
    finally:
        if "sink_lock_acquired" in locals() and sink_lock_acquired:
            sink.lock.release()
        os.close(fd)


def reconcile(owner_root: Path, request_id: str, test_gate=False):
    """Strict default path; reserved-only owner state remains refused."""
    return _run_reconcile(owner_root, request_id, test_gate=test_gate)


def observe_local(owner_root: Path, request_id: str, test_gate_phase=None):
    """Explicitly observe an actual final F4 event for an existing reservation."""
    return _run_reconcile(
        owner_root, request_id,
        test_gate=test_gate_phase == "after-confirmed-publication-before-settlement",
        allow_reserved=True,
        test_gate_local=test_gate_phase == "after-local-observation-before-publication",
    )


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
