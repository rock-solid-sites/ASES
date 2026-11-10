#!/usr/bin/env python3
"""CLI joining the frozen composed sink to the cold-state factory."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ADMISSION_DIR = RESEARCH / "phase-i-effect-admission"
COMPOSED_SINK = RESEARCH / "phase-i-composed-effects" / "composed_sink.py"
COLD_FACTORY = RESEARCH / "phase-i-cold-activation" / "cold_sink.py"

# admission_sink imports `admission` by module name. Load this branch-local
# derivative first so the additional selected-schema check is in the actual
# composed admission guard.
sys.path.insert(0, str(ADMISSION_DIR))


def load(name, path):
    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[name] = module
    module_spec.loader.exec_module(module)
    return module


composed = load("continuation_composed_sink", COMPOSED_SINK)
cold = load("continuation_cold_factory", COLD_FACTORY)


def main(argv):
    if len(argv) == 3 and argv[1] == "--witness":
        composed.admission.cut.witness_server(argv[2])
        return 0
    if (len(argv) != 8 or argv[1] != "--sink" or argv[2] not in ("fresh", "recover")
            or argv[5] != "published-cut"):
        raise SystemExit("usage: --witness ROOT | --sink MODE JOURNAL PORT published-cut ROOT CONFIG")
    recover = argv[2] == "recover"
    config = composed.admission.decode(Path(argv[7]).read_text())
    composed.admission.cut.ORIGINAL_STATE = cold.state_type(composed.retry.RetryState, recover)
    return composed.admission.serve(config, Path(argv[3]), recover, int(argv[4]), argv[6])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
