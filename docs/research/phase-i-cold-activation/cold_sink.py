#!/usr/bin/env python3
"""Disposable cold-sealed wrapper around the pinned published-cut sink."""
import importlib.util
import sys
from pathlib import Path


def load(path):
    spec = importlib.util.spec_from_file_location("pinned_cut_sink", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv):
    if len(argv) != 8 or argv[1] != "--cold-sink" or argv[2] not in ("fresh", "recover") or argv[5] != "published-cut":
        raise SystemExit("usage: cold_sink.py --cold-sink MODE JOURNAL PORT published-cut ROOT PINNED_CUT_SINK")
    cut = load(Path(argv[7]))
    original = cut.ORIGINAL_STATE

    class ColdSealedState(original):
        def __init__(self, *args, **kwargs):
            self.cold_admission_open = argv[2] != "recover"
            self.replaced_this_boot = False
            super().__init__(*args, **kwargs)

        def eligible(self, token):
            return self.cold_admission_open and super().eligible(token)

        def apply(self, path, data):
            routes = {
                "/create": set(), "/grant": set(), "/activate": {"authority_version"},
                "/revoke": set(), "/replace": {"holder"},
                "/submit": {"authority_version", "request_id", "payload"},
            }
            if path not in routes:
                return 404, {"error": "unknown route"}
            if not isinstance(data, dict) or set(data) != routes[path]:
                return 400, {"error": "route input rejected"}
            if path == "/activate" and type(data.get("authority_version")) is not int:
                return 400, {"error": "integer token required"}
            if path == "/replace" and not isinstance(data.get("holder"), str):
                return 400, {"error": "string holder required"}
            if path == "/submit" and (type(data.get("authority_version")) is not int
                    or not isinstance(data.get("request_id"), str) or not isinstance(data.get("payload"), str)):
                return 400, {"error": "invalid submit input"}
            if path == "/activate" and not self.cold_admission_open and not self.replaced_this_boot:
                return 409, {"outcome": "fresh-replacement-required", "local_control_committed": False}
            status, reply = super().apply(path, data)
            if path == "/replace" and status == 200 and reply.get("outcome") == "accepted":
                self.replaced_this_boot = True
            if path == "/activate" and status == 200 and reply.get("outcome") == "accepted":
                self.cold_admission_open = True
            return status, reply

        def snapshot(self):
            return dict(super().snapshot(), cold_admission_open=self.cold_admission_open,
                        replaced_this_boot=self.replaced_this_boot)

    cut.ORIGINAL_STATE = ColdSealedState
    return cut.serve_sink(Path(argv[3]), argv[2] == "recover", int(argv[4]), argv[6])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
