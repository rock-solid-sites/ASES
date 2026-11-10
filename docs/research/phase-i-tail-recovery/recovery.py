#!/usr/bin/env python3
"""Explicit bounded recovery for one verified, unterminated append tail.

The caller must hold the native stable sink-writer lock for the whole call.
This module never acquires a second lock and never contacts anything except the
loopback witness endpoint supplied by the trusted local probe.
"""
import hashlib
import json
import os
import secrets
from pathlib import Path
import urllib.error
import urllib.request

MAX_JOURNAL = 65536


def _post(port, path, request):
    data = json.dumps(request, sort_keys=True).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=2) as response:
        return response.status, json.loads(response.read(65537))


def recover(journal, root, port, validate, trusted_root):
    """Validate, witness-check, quarantine and select the complete prefix.

    `validate(path)` must invoke native managed replay plus retry-ID replay and
    return the fully reconstructed state. `journal` and all generated files
    must be in the trusted disposable test root. The caller holds sink-writer.lock.
    """
    journal = Path(journal).resolve()
    trusted_root = Path(trusted_root).resolve()
    if journal.parent != trusted_root:
        raise ValueError("journal path is outside trusted test root")
    if not journal.exists():
        raise ValueError("missing journal: no complete prefix")
    with journal.open("rb") as stream:
        original = stream.read(MAX_JOURNAL + 1)
    if not original or len(original) > MAX_JOURNAL:
        raise ValueError("empty or oversized journal")

    if original.endswith(b"\n"):
        state = validate(journal)
        current = _cut(state, original)
        _check(root, port, current)
        return {"mode": "no-tail", "journal_sha256": current["journal_sha256"]}

    boundary = original.rfind(b"\n") + 1
    if boundary == 0:
        raise ValueError("no complete validated prefix")
    prefix, tail = original[:boundary], original[boundary:]
    # Validate against a bounded scratch file in the same trusted root. This
    # does not replace or alter the original journal.
    scratch = journal.with_name(journal.name + ".validate-" + secrets.token_hex(8))
    try:
        with scratch.open("xb") as stream:
            stream.write(prefix)
            stream.flush()
            os.fsync(stream.fileno())
        state = validate(scratch)
    finally:
        try:
            scratch.unlink()
        except FileNotFoundError:
            pass
    current = _cut(state, prefix)
    _check(root, port, current)

    digest = hashlib.sha256(original).hexdigest()
    quarantine = journal.with_name(journal.name + ".quarantine-" + digest)
    if quarantine.exists():
        if quarantine.read_bytes() != original:
            raise ValueError("quarantine content mismatch")
    else:
        with quarantine.open("xb") as stream:
            stream.write(original)
            stream.flush()
            os.fsync(stream.fileno())
    _gate("quarantined")

    prepared = journal.with_name(journal.name + ".prefix.tmp")
    with prepared.open("wb") as stream:
        stream.write(prefix)
        stream.flush()
        os.fsync(stream.fileno())
    _gate("prepared")
    os.replace(prepared, journal)
    _gate("selected")
    return {"mode": "append-only-interrupted-tail", "original_sha256": digest,
            "prefix_sha256": hashlib.sha256(prefix).hexdigest(),
            "tail_sha256": hashlib.sha256(tail).hexdigest(), "tail_bytes": len(tail),
            "quarantine": quarantine.name}


def _cut(state, raw):
    authority = {"created": state.created, "granted": state.granted,
                 "active": state.active, "authority_version": state.version,
                 "holder": state.holder}
    return {"authority": authority, "journal_sha256": hashlib.sha256(raw).hexdigest()}


def _check(root, port, candidate):
    request = {"root": root, "nonce": secrets.token_hex(16), "candidate": candidate}
    try:
        status, reply = _post(port, "/check", request)
    except (OSError, urllib.error.URLError, ValueError) as error:
        raise ValueError("live witness check unavailable") from error
    if (status != 200 or reply.get("root") != root or reply.get("nonce") != request["nonce"]
            or type(reply.get("revision")) is not int or reply.get("allowed") is not True
            or reply.get("current") != candidate):
        raise ValueError("live witness cut mismatch")


def _gate(stage):
    # Set by the disposable parent process for real SIGKILL crash gates.
    if os.environ.get("ASES_TAIL_GATE") != stage:
        return
    print(json.dumps({"event": "tail-gate", "stage": stage, "pid": os.getpid()}), flush=True)
    if os.read(0, 1) != b"\n":
        os._exit(88)
