#!/usr/bin/env python3
"""Send the one and only Atria chat-completion request for this review.

Design constraints enforced here:
  * The API key is read at runtime from ~/.secrets/atria.env. It is never passed
    as a command-line argument, never logged, and never printed.
  * Exactly one HTTP POST. No retries, no redirect-driven content changes.
  * The request body is serialized once, written to disk BEFORE sending, and
    the very same bytes are transmitted.
  * The raw response body is stored unchanged, including for HTTP errors.
"""

import datetime
import hashlib
import json
import ssl
import time
import urllib.error
import urllib.request

from pathlib import Path

ED = Path(__file__).resolve().parent

ENDPOINT = "https://api.atria-asi.ai/v1/chat/completions"
REQUESTED_MODEL = "Atria-Dawn-Preview"
SOURCE_COMMIT = "e2e3bc110b1370f3505aa0838990713520bf3f7c"
TIMEOUT_SECONDS = 900
SECRET_PATH = Path.home() / ".secrets" / "atria.env"

BANNED_RESPONSE_HEADERS = {"set-cookie"}


def load_key():
    """Load ATRIA_API_KEY from the secret file without ever printing it."""
    if not SECRET_PATH.is_file():
        raise SystemExit(
            f"ERROR: secret file not found at {SECRET_PATH}. "
            "Provisioning is a prerequisite; refusing to continue."
        )
    key = None
    for raw in SECRET_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("ATRIA_API_KEY="):
            value = line[len("ATRIA_API_KEY="):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            key = value
            break
    if not key:
        raise SystemExit(
            f"ERROR: ATRIA_API_KEY not defined in {SECRET_PATH}. Refusing to continue."
        )
    return key


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    key = load_key()

    prompt_bytes = (ED / "review-prompt.md").read_bytes()
    packet_bytes = (ED / "packet.md").read_bytes()
    message_content = (prompt_bytes + b"\n\n" + packet_bytes).decode("utf-8")

    body = {
        "model": REQUESTED_MODEL,
        "messages": [{"role": "user", "content": message_content}],
    }
    request_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

    # Persist the exact bytes that will be transmitted, before sending.
    (ED / "atria-request.json").write_bytes(request_bytes)

    req = urllib.request.Request(
        ENDPOINT,
        data=request_bytes,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    key = None  # drop the reference as early as possible

    start_iso = utc_now_iso()
    t0 = time.monotonic()
    status = None
    headers_seen = {}
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS, context=context) as resp:
            status = resp.status
            raw = resp.read()
            headers_seen = dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
        headers_seen = dict(exc.headers.items()) if exc.headers else {}
    except Exception as exc:  # network/TLS/timeout failure
        elapsed = round(time.monotonic() - t0, 3)
        (ED / "atria-response.raw.json").write_bytes(b"")
        (ED / "atria-response-metadata.json").write_text(
            json.dumps(
                {
                    "endpoint": ENDPOINT,
                    "method": "POST",
                    "requested_model": REQUESTED_MODEL,
                    "http_status": None,
                    "error_type": type(exc).__name__,
                    "error_detail": str(exc)[:500],
                    "started_utc": start_iso,
                    "ended_utc": utc_now_iso(),
                    "elapsed_seconds": elapsed,
                    "request_sha256": sha256_hex(request_bytes),
                    "packet_sha256": sha256_hex(packet_bytes),
                    "review_prompt_sha256": sha256_hex(prompt_bytes),
                    "raw_response_sha256": sha256_hex(b""),
                    "source_commit": SOURCE_COMMIT,
                    "note": "single request; no retries",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"HTTP_STATUS=NONE error_type={type(exc).__name__}")
        print(f"ELAPSED_SECONDS={elapsed}")
        print(f"RAW_RESPONSE_BYTES=0")
        print(f"METADATA_PATH={ED / 'atria-response-metadata.json'}")
        raise SystemExit(2)

    elapsed = round(time.monotonic() - t0, 3)
    end_iso = utc_now_iso()

    # Store the raw body unchanged, including for HTTP error responses.
    (ED / "atria-response.raw.json").write_bytes(raw)

    safe_headers = {
        k: v for k, v in headers_seen.items() if k.lower() not in BANNED_RESPONSE_HEADERS
    }

    meta = {
        "endpoint": ENDPOINT,
        "method": "POST",
        "requested_model": REQUESTED_MODEL,
        "http_status": status,
        "started_utc": start_iso,
        "ended_utc": end_iso,
        "elapsed_seconds": elapsed,
        "response_headers": safe_headers,
        "set_cookie_present": any(
            k.lower() == "set-cookie" for k in headers_seen
        ),
        "request_sha256": sha256_hex(request_bytes),
        "request_bytes": len(request_bytes),
        "packet_sha256": sha256_hex(packet_bytes),
        "review_prompt_sha256": sha256_hex(prompt_bytes),
        "raw_response_sha256": sha256_hex(raw),
        "raw_response_bytes": len(raw),
        "source_commit": SOURCE_COMMIT,
        "note": "single request; no retries",
    }

    # Best-effort parse for metadata and the content file; failures are recorded.
    parsed = None
    parse_error = None
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        parse_error = f"{type(exc).__name__}: {str(exc)[:200]}"

    if parse_error:
        meta["json_parse_error"] = parse_error

    content_present = False
    content_is_string = False
    reasoning_field_present = False

    if isinstance(parsed, dict):
        for field in ("id", "model", "created", "usage", "system_fingerprint"):
            if field in parsed:
                meta[f"response_{field}"] = parsed[field]
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if "finish_reason" in first:
                    meta["finish_reason"] = first["finish_reason"]
                message = first.get("message")
                if isinstance(message, dict):
                    if any(
                        k in message
                        for k in ("reasoning", "reasoning_content", "thinking", "thought")
                    ):
                        reasoning_field_present = True
                    c = message.get("content")
                    if c is not None:
                        content_present = True
                        if isinstance(c, str):
                            content_is_string = True
                            # Exact content bytes; no trimming, no added newline.
                            (ED / "atria-response.md").write_bytes(c.encode("utf-8"))
    else:
        meta["json_parse_error"] = parse_error or "top-level JSON is not an object"

    meta["content_present"] = content_present
    meta["content_is_string"] = content_is_string
    meta["reasoning_style_field_present"] = "yes" if reasoning_field_present else "no"

    (ED / "atria-response-metadata.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"HTTP_STATUS={status}")
    print(f"RESPONSE_MODEL={meta.get('response_model')}")
    print(f"FINISH_REASON={meta.get('finish_reason')}")
    print(f"ELAPSED_SECONDS={elapsed}")
    print(f"RAW_RESPONSE_BYTES={len(raw)}")
    print(f"REASONING_FIELD_PRESENT={meta['reasoning_style_field_present']}")
    resp_md = ED / "atria-response.md"
    print(f"RESPONSE_MD_BYTES={resp_md.stat().st_size if resp_md.is_file() else 0}")
    print(f"METADATA_PATH={ED / 'atria-response-metadata.json'}")

    if not (200 <= status < 300) or not (content_present and content_is_string):
        print("RESULT=BLOCKER_NON_2XX_OR_MISSING_STRING_CONTENT")
        raise SystemExit(3)

    print("RESULT=OK")


if __name__ == "__main__":
    main()
