#!/usr/bin/env python3
"""Isolated retry-observation subclass over the pinned receipt-extended L5 cut sink."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parent / "phase-i-sol-integration/evidence/sources/receipt/research/phase-i-t18-sink-order-20261103"
CUT_SOURCE = SOURCE_ROOT / "published-cut/cut_sink.py"
MANAGED_SOURCE = SOURCE_ROOT / "managed-revocation/managed_sink.py"
RUN_SOURCE = SOURCE_ROOT / "run.py"
GATE = os.environ.get("ASES_RETRY_GATE", "")
TAIL_GATE = os.environ.get("ASES_TAIL_GATE", "")
TAIL_OPTIONS = None
VALIDATING = False
WRITE_FAULT = os.environ.get("ASES_TAIL_WRITE_FAULT", "")



def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cut = load("retry_pinned_cut_sink", CUT_SOURCE)
managed = cut.managed


def gate(stage):
    if GATE != stage:
        return
    print(json.dumps({"event": "gate", "stage": stage, "pid": os.getpid()}), flush=True)
    line = sys.stdin.readline()
    if line != "continue\n":
        os._exit(87)


class RetryState(managed.State):
    """Add a replay-derived request index; leave pinned persistence/cut logic intact."""

    def __init__(self, *args, **kwargs):
        self.request_index = {}
        journal = args[0] if args else kwargs.get("journal")
        recover = args[1] if len(args) > 1 else kwargs.get("recover", False)
        if recover and TAIL_OPTIONS is not None and not VALIDATING:
            import recovery
            root, port = TAIL_OPTIONS
            recovery.recover(journal, root, port, self._validate_path, os.environ.get("ASES_TAIL_TEST_ROOT", ""))
        super().__init__(*args, **kwargs)
        self._rebuild_request_index()

    @classmethod
    def _validate_path(cls, path):
        # Native managed replay and retry duplicate-ID rules both run here.
        global VALIDATING
        VALIDATING = True
        try:
            return cls(path, True)
        finally:
            VALIDATING = False

    @staticmethod
    def _valid_text(value):
        if type(value) is not str:
            return False
        try:
            value.encode("utf-8", "strict")
        except UnicodeEncodeError:
            return False
        return True

    def _rebuild_request_index(self):
        index = {}
        for event in self.effects:
            request_id = event.get("request_id")
            payload = event.get("payload")
            if (not self._valid_text(request_id) or not request_id
                    or not self._valid_text(payload)):
                raise ValueError("invalid request identity in effect journal")
            if request_id in index:
                raise ValueError("duplicate effect request_id in journal")
            index[request_id] = event
        self.request_index = index

    def _observation(self, event):
        current = self.cut()
        proof = next((entry for entry in reversed(self.cut_protocol_log)
                      if entry.get("path") == "/check"), None)
        reply = None if proof is None else proof.get("response")
        verified = bool(proof and proof.get("valid") is True
                        and proof.get("transport_valid") is True
                        and reply.get("allowed") is True
                        and reply.get("current") == current
                        and type(reply.get("revision")) is int)
        if not verified:
            return 503, dict(outcome="published-cut-unavailable",
                             local_control_committed=False)
        return 200, dict(outcome="already-accepted", event_seq=event["seq"],
                         accepted_authority_version=event["accepted_under_version"],
                         verified_journal_sha256=current["journal_sha256"],
                         verified_revision=reply["revision"])

    def apply(self, path, data):
        # Obligation operations are outside the frozen F4 request-ID contract.
        # Refuse before the pinned implementation can append or deliver one.
        if path in ("/commit-obligation", "/deliver-obligation"):
            return 403, dict(outcome="unsupported-in-retry-candidate",
                             reason="obligation workflows are outside the F4 experiment")
        if path == "/submit":
            request_id = data.get("request_id")
            payload = data.get("payload")
            if not self._valid_text(request_id) or not request_id:
                raise ValueError("nonempty UTF-8 request_id required")
            if not self._valid_text(payload):
                raise ValueError("UTF-8 string payload required")
            previous = self.request_index.get(request_id)
            if previous is not None:
                if previous["payload"] != payload:
                    return 409, dict(outcome="request-id-conflict",
                                     event_seq=previous["seq"])
                return self._observation(previous)
            gate("before-append")
            status, reply = super().apply(path, data)
            if status == 201 and reply.get("outcome") == "accepted":
                event = self.effects[-1]
                if event.get("request_id") != request_id or event.get("payload") != payload:
                    raise RuntimeError("new effect does not match validated request")
                self.request_index[request_id] = event
                gate("after-append")
            return status, reply

        return super().apply(path, data)

    def snapshot(self):
        value = super().snapshot()
        value["request_index"] = {key: event["seq"] for key, event in self.request_index.items()}
        return value


# cut_sink.serve_sink defines its own receipt-aware subclass around ORIGINAL_STATE.
cut.ORIGINAL_STATE = RetryState

# Wrap only the real generated cut-aware state's return edge to expose the actual
# publication-complete / caller-reply-not-yet-sent crash point.
original_managed_serve = managed.serve


def reply_gate_serve(journal, recover=False):
    generated_state = managed.State

    class ReplyGateState(generated_state):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            original_apply = self.apply

            def apply(path, data):
                previous = None
                if path == "/submit":
                    request_id = data.get("request_id")
                    payload = data.get("payload")
                    if not RetryState._valid_text(request_id) or not request_id:
                        raise ValueError("nonempty UTF-8 request_id required")
                    if not RetryState._valid_text(payload):
                        raise ValueError("UTF-8 string payload required")
                    previous = self.request_index.get(request_id)
                    # A known payload conflict is decided under the inherited sink
                    # lock before the receipt wrapper's live-cut check.
                    if previous is not None and previous["payload"] != payload:
                        return 409, dict(outcome="request-id-conflict",
                                         event_seq=previous["seq"])
                status, reply = original_apply(path, data)
                if (path == "/submit" and previous is not None
                        and reply.get("outcome") == "published-cut-unavailable"):
                    reply = dict(reply, outcome="retry-observation-unresolved",
                                 local_control_committed=True,
                                 local_event_seq=previous["seq"])
                if reply.get("outcome") == "cut-publication-unknown":
                    publication = next((entry for entry in reversed(self.cut_protocol_log)
                                        if entry.get("path") == "/publish"), None)
                    remote = None if publication is None else publication.get("response")
                    request = None if publication is None else publication.get("request")
                    if (publication and isinstance(remote, dict) and isinstance(request, dict)
                            and remote.get("root") == request.get("root")
                            and remote.get("nonce") == request.get("nonce")
                            and type(remote.get("revision")) is int
                            and remote.get("published") is False):
                        # Keep the locally committed effect explicit; distinguish a
                        # witnessed rejection from a publication whose receipt vanished.
                        reply = dict(reply, outcome="cut-publication-rejected",
                                     remote_publication="rejected",
                                     publication_status=publication.get("status"),
                                     publication_reason=remote.get("reason"))
                if (path == "/submit" and status == 201
                        and reply.get("published_revision") is not None):
                    gate("after-publication-before-reply")
                return status, reply

            self.apply = apply

    managed.State = ReplyGateState
    try:
        return original_managed_serve(journal, recover)
    finally:
        managed.State = generated_state


managed.serve = reply_gate_serve

def install_write_fault(journal):
    """Fault one native journal syscall, leaving all other descriptors alone."""
    if not WRITE_FAULT:
        return
    original_write, original_fsync = os.write, os.fsync
    fired = {"value": False}
    def is_journal(fd):
        try:
            return os.path.realpath(f"/proc/{os.getpid()}/fd/{fd}") == os.path.realpath(journal)
        except OSError:
            return False
    def write(fd, data):
        if not fired["value"] and is_journal(fd) and WRITE_FAULT == "partial-write":
            fired["value"] = True
            amount = max(1, len(data) // 2)
            original_write(fd, data[:amount])
            raise OSError("injected after actual partial journal row write")
        return original_write(fd, data)
    def fsync(fd):
        if not fired["value"] and is_journal(fd) and WRITE_FAULT == "complete-write-fsync":
            fired["value"] = True
            raise OSError("injected fsync failure after complete journal row write")
        return original_fsync(fd)
    os.write, os.fsync = write, fsync


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--witness":
        cut.witness_server(args[1])
    elif len(args) == 6 and args[0] == "--sink":
        _, mode, journal, port, profile, root = args
        if mode not in ("fresh", "recover", "recover-tail") or profile != "published-cut":
            raise SystemExit("usage: --sink {fresh|recover|recover-tail} JOURNAL PORT published-cut ROOT")
        journal = str(Path(journal).resolve())
        install_write_fault(journal)
        if mode == "recover-tail":
            TAIL_OPTIONS = (root, int(port))
            # RetryState is constructed under cut_sink's stable writer flock.
            TAIL_OPTIONS = (root, int(port))
            return_code = cut.serve_sink(Path(journal), True, int(port), root)
        else:
            return_code = cut.serve_sink(Path(journal), mode == "recover", int(port), root)
        raise SystemExit(return_code)
    else:
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT")
