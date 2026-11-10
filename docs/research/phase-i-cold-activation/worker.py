#!/usr/bin/env python3
"""Bounded independent CPU worker used by the local continuation probe."""
import hashlib
import http.client
import json
import sys


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    for line in sys.stdin:
        request = json.loads(line)
        if request.get("op") == "stop":
            print(json.dumps({"stopped": True}), flush=True)
            return
        count = request.get("iterations")
        if type(count) is not int or not 0 <= count <= 2_000_000:
            print(json.dumps({"error": "bounded iteration count required"}), flush=True)
            continue
        value = 0
        for index in range(count):
            value = (value * 33 + index + 17) & 0xFFFFFFFF
        result = {"iterations": count, "progress": value}
        if "port" in request:
            body = canonical({"authority_version": request["version"], "request_id": request["request_id"],
                              "payload": request["payload"]})
            conn = http.client.HTTPConnection("127.0.0.1", request["port"], timeout=5)
            try:
                conn.request("POST", "/submit", body, {"Content-Type": "application/json"})
                reply = conn.getresponse()
                raw = reply.read().decode()
                result["effect"] = {"status": reply.status, "body": json.loads(raw)}
            except OSError as error:
                result["effect"] = {"transport_error": type(error).__name__}
            finally:
                conn.close()
        print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
