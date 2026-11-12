"""Unprivileged public-document reachability snapshot.

HEAD status and caching headers are *not* provider availability, pricing,
account entitlement, or launch permission. Never send credentials.
"""
import concurrent.futures
import datetime
import json
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

CATALOG = pathlib.Path(__file__).parent / "candidate_inventory_v0.json"


def check(item):
    provider, product, url = item
    parsed = urllib.parse.urlsplit(url)
    record = {"provider_id": provider, "product_id": product, "url": url,
              "http_status": None, "etag": None, "last_modified": None,
              "observation": "unknown"}
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        record["observation"] = "invalid_url"
        return record
    request = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "ASES-provider-catalog-source-check/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=8) as resp:
            record["http_status"] = resp.status
            record["etag"] = resp.headers.get("ETag")
            record["last_modified"] = resp.headers.get("Last-Modified")
            record["observation"] = "http_response"
    except urllib.error.HTTPError as exc:
        record["http_status"] = exc.code
        record["observation"] = "http_rejected_or_head_unsupported"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        record["observation"] = "transport_error"
        record["error_type"] = type(exc).__name__
    return record


def main():
    catalogue = json.loads(CATALOG.read_text(encoding="utf-8"))
    targets = [(p["id"], prod, route["source_url"]) for p in catalogue["providers"]
               for prod, route in (p.get("documented_execution_routes") or {}).items()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        observations = list(executor.map(check, targets))
    report = {
        "schema_version": 1,
        "kind": "read_only_public_document_transport_check",
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "interpretation": "HEAD reachability only; not provider availability, API launch test, account entitlement or pricing",
        "observations": observations,
    }
    output = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ases-provider-source-health.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checked": len(observations),
                      "http_responses": sum(o["observation"] == "http_response" for o in observations),
                      "output": str(output)}))


if __name__ == "__main__":
    main()
