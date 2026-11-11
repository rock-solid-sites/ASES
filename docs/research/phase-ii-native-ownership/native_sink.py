#!/usr/bin/env python3
"""Native F3 registration in the existing cold/current/history F4 append path."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RESEARCH / "phase-i-effect-admission"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


continuation = load("owned_continuation", RESEARCH / "phase-i-continuation-stack/continuation_sink.py")
composed = continuation.composed
legacy = sys.modules["admission"]
from native_owner import Owner

PROFILE = "native-f3-owner-v1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def generation(root, selector):
    return dict(selector=selector, sha256=sha((root / "protected" / selector).read_bytes()))


class NativeAdmission(legacy.Admission):
    def __init__(self, config):
        legacy.require(set(config) <= {"profile", "owner_root", "gate"}
                       and config.get("profile") == PROFILE, "unsupported-native-owner-config")
        self.config = config
        self.trace = []
        self.owner = Owner(Path(config["owner_root"]))
        self.active_session = None

    @contextmanager
    def guard(self, effect):
        reserved = False
        try:
            envelope = legacy.decode(effect["payload"])
            legacy.require(isinstance(envelope, dict) and set(envelope) ==
                           {"kind", "import_id", "epoch", "pair", "l5", "request_id"},
                           "invalid-native-envelope")
            legacy.require(envelope["kind"] == "use-current-descendant"
                           and envelope["request_id"] == effect["request_id"], "wrong-native-use")
            self.gate("before-admission")
            with self.owner.locked() as session:
                state = session.state
                owner = state["native_owner"]
                legacy.require(owner["profile"] == PROFILE and owner["lifecycle"] == "live",
                               "native-domain-not-live")
                legacy.require(type(envelope["epoch"]) is int
                               and envelope["epoch"] == owner["epoch"], "stale-native-epoch")
                legacy.require(owner["children"].get("D") == "live", "native-child-not-live")
                registration = next((r for r in owner["registrations"]
                                     if r["id"] == owner["selected"]), None)
                legacy.require(registration is not None and registration["status"] == "live"
                               and envelope["import_id"] == registration["id"],
                               "native-registration-not-selected")
                pair = registration["pair"]
                legacy.require(envelope["pair"] == pair, "native-evidence-world-mismatch")
                root, profile, version, raw_view = session.f1.execute(
                    "SELECT root,profile,version,view FROM kernel WHERE id=1").fetchone()
                current = session.f1.execute(
                    "SELECT record FROM consumer_observations WHERE id=1").fetchone()
                retained = [legacy.decode(r[0]) for r in session.f1.execute(
                    "SELECT record FROM retained_observations")]
                legacy.require(root == "work" and profile == "independent" and version == 1
                               and current is not None and legacy.decode(current[0]) == pair
                               and legacy.decode(raw_view)["content"] == pair["accepted_content"]
                               and pair in retained, "native-f1-selected-retained-mismatch")
                presented = generation(self.owner.root, session.selector)
                legacy.require(envelope["l5"] == presented, "stale-native-selector")
                legacy.require(type(state.get("schema")) is int and state["schema"] == 1
                               and legacy.l5.graph_valid(state)
                               and legacy.l5.enabled(state, "D", "W-L5")
                               and "write" in legacy.l5.permissions(state, "D"),
                               "native-current-path-denied")
                contents = state["work_units"]["C"]["accepted_contents"]
                meta = registration["metadata"]
                content = pair["accepted_content"].encode()
                legacy.require(contents == [meta] and meta["identity"] == registration["id"]
                               and meta["accepted_pair"] == pair
                               and legacy.l5.verified_content(self.owner.root, meta) == content,
                               "native-retained-material-mismatch")
                inventory = session.inventory
                legacy.require(inventory.cx.execute("SELECT live,sealed FROM unit").fetchall() == [(1, 1)],
                               "native-storage-inventory-not-live")
                rows = inventory.cx.execute(
                    "SELECT name,kind,sha256,size,disposed FROM dependencies ORDER BY name").fetchall()
                files = list((self.owner.root / "protected/objects").iterdir())
                legacy.require(all(p.is_file() and not p.is_symlink() for p in files)
                               and {p.name for p in files} <= {r[0] for r in rows},
                               "native-unknown-material")
                live = {r[0]: r for r in rows if not r[4]}
                name = Path(meta["object"]).name
                legacy.require(name in live and live[name][2:4] == (sha(content), len(content)),
                               "native-inventory-binding-mismatch")
                for item, _kind, digest, size, disposed in rows:
                    if not disposed:
                        raw = (self.owner.root / "protected/objects" / item).read_bytes()
                        legacy.require(sha(raw) == digest and len(raw) == size,
                                       "native-live-material-integrity")
                # Publication may fail after selecting its durable reservation.
                # From this attempt onward, never report a no-effect denial.
                reserved = True
                session.reserve_effect(effect["request_id"], sha(effect["payload"].encode()))
                self.active_session = session
                certificate = dict(profile=PROFILE, native_registration=True,
                                   domain_id=owner["domain_id"], import_id=registration["id"],
                                   epoch=owner["epoch"], pair_sha256=sha(legacy.canonical(pair).encode()),
                                   presented_l5=presented,
                                   l5=generation(self.owner.root, session.selector),
                                   descendant="D", authorization_point="local-journal-append")
                self.event("native-admitted-view", certificate=certificate)
                self.gate("guarded")
                yield certificate
                self.event("local-append-returned", request_id=effect["request_id"])
                self.gate("after-append")
        except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as error:
            if reserved:
                self.event("native-reservation-outcome-unresolved", reason=str(error))
                raise OSError("native-effect-requires-reconciliation:" + str(error)) from error
            if isinstance(error, legacy.Denied):
                raise
            raise legacy.Denied(type(error).__name__ + ":" + str(error)) from error
        finally:
            self.active_session = None

    def after_append(self, event):
        legacy.require(self.active_session is not None and event["event"] == "effect_accepted",
                       "native-append-session-missing")
        self.active_session.record_local_effect(event["request_id"], event["seq"])


def attach_sink(owner, journal, witness_root):
    journal.parent.mkdir(parents=True, exist_ok=True)
    binding = dict(journal=str(journal.resolve()),
                   journal_parent_identity=legacy.identity(journal.parent), witness_root=witness_root)
    socket_path = os.environ.get("ASES_NATIVE_WITNESS_SOCKET")
    if socket_path:
        endpoint = Path(socket_path).absolute()
        binding["witness_endpoint"] = dict(path=str(endpoint), parent_identity=legacy.identity(endpoint.parent))
    with owner.locked() as session:
        native = session.state["native_owner"]
        prior = native.get("sink_binding")
        if prior is not None:
            legacy.require(prior == binding, "native-sink-attachment-conflict")
            return
        legacy.require(native["lifecycle"] == "live", "cannot-attach-removed-domain")
        native["sink_binding"] = binding
        session.commit(dict(op="native-attach-f4-sink", binding=binding))


def settle_from_native_sink(owner, sink, request_id):
    """Called only inside the real F4 request mutex, never from client evidence."""
    event = sink.request_index.get(request_id)
    if event is None:
        return dict(status="unresolved-no-local-observation")
    current = sink.cut()
    proof = sink.check_cut(current)  # Actual fresh nonce-bearing native witness exchange.
    if not proof["valid"]:
        return dict(status="unresolved-publication")
    raw = sink.journal.read_bytes()
    legacy.require(sha(raw) == current["journal_sha256"], "native-journal-changed-at-settlement")
    matches = [legacy.decode(line) for line in raw.splitlines()
               if line and legacy.decode(line).get("event") == "effect_accepted"
               and legacy.decode(line).get("request_id") == request_id]
    legacy.require(matches == [event], "native-event-not-exact-in-validated-journal")
    with owner.locked() as session:
        native = session.state["native_owner"]
        binding = native.get("sink_binding") or {}
        legacy.require(binding.get("journal") == str(sink.journal.resolve())
                       and binding.get("journal_parent_identity") == legacy.identity(sink.journal.parent)
                       and binding.get("witness_root") == proof["request"]["root"],
                       "native-settlement-wrong-attachment")
        certificate = event.get("admission", {})
        legacy.require(certificate.get("profile") == PROFILE
                       and certificate.get("domain_id") == native["domain_id"],
                       "native-effect-wrong-domain")
        pending = native["effects"].get(request_id)
        legacy.require(pending is not None and pending["payload_sha256"] == sha(event["payload"].encode()),
                       "native-effect-reservation-mismatch")
        if pending["status"] == "published":
            legacy.require(pending["seq"] == event["seq"], "native-published-sequence-mismatch")
            return dict(status="published", event_seq=event["seq"], replayed=True)
        legacy.require(pending["status"] in ("reserved", "local"), "unsupported-native-effect-status")
        if pending["status"] == "local":
            legacy.require(pending["seq"] == event["seq"], "native-local-sequence-mismatch")
        pending.update(status="published", seq=event["seq"], receipt=dict(
            journal_sha256=current["journal_sha256"], revision=proof["response"]["revision"],
            root=proof["request"]["root"], nonce=proof["request"]["nonce"]))
        session.commit(dict(op="native-effect-published", request_id=request_id, seq=event["seq"]))
        return dict(status="published", event_seq=event["seq"], replayed=False)


def main(argv):
    listen_path = os.environ.get("ASES_NATIVE_LISTEN_SOCKET")
    if listen_path:
        from unix_transport import install, call_unix
        witness_path = os.environ.get("ASES_NATIVE_WITNESS_SOCKET")
        install(listen_path, witness_path)
        if witness_path:
            composed.admission.cut.managed.base.call = lambda _port, method, path, data=None: call_unix(
                witness_path, method, path, data)
    if len(argv) == 3 and argv[1] == "--witness":
        return composed.admission.cut.witness_server(argv[2])
    if len(argv) != 8 or argv[1] != "--sink" or argv[2] not in ("fresh", "recover") or argv[5] != "published-cut":
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL WITNESS_PORT published-cut ROOT CONFIG")
    config = legacy.decode(Path(argv[7]).read_text())
    admission = NativeAdmission(config)
    journal = Path(argv[3])
    attach_sink(admission.owner, journal, argv[6])
    composed.admission.Admission = lambda _config: admission
    composed.admission.cut.ORIGINAL_STATE = continuation.cold.state_type(composed.retry.RetryState,
                                                                          argv[2] == "recover")
    managed = composed.admission.cut.managed
    prior_serve = managed.serve

    def serve_with_owner(journal_path, recover=False):
        generated = managed.State

        class OwnerOutcomeState(generated):
            def apply(self, path, data):
                try:
                    status, reply = super().apply(path, data)
                except OSError as error:
                    request_id = data.get("request_id") if isinstance(data, dict) else None
                    effect = admission.owner.view()["state"]["native_owner"]["effects"].get(request_id)
                    if path != "/submit" or effect is None:
                        raise
                    # A durable owner reservation may precede an uncertain local
                    # write. The local-append case already has its actual seq.
                    return 503, dict(outcome="native-effect-requires-reconciliation",
                                     owner_reservation_committed=True,
                                     local_control_committed=True if effect["status"] in ("local", "published") else None,
                                     local_event_seq=effect.get("seq"), reason=str(error))
                if path == "/submit" and isinstance(data, dict):
                    request_id = data.get("request_id")
                    if isinstance(request_id, str) and request_id in self.request_index:
                        admission.gate("before-settlement")
                        try:
                            reply = dict(reply, owner_effect=settle_from_native_sink(admission.owner, self, request_id))
                        except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as error:
                            reply = dict(reply, owner_effect=dict(status="unresolved", reason=str(error)))
                return status, reply

        managed.State = OwnerOutcomeState
        try:
            return prior_serve(journal_path, recover)
        finally:
            managed.State = generated

    managed.serve = serve_with_owner
    return composed.admission.serve(config, journal, argv[2] == "recover", int(argv[4]), argv[6])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
