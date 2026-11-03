import contextlib
import io
import json
import pathlib
import sys
import tempfile

source = pathlib.Path("docs/research/phase-i-f1").resolve()
sys.path.insert(0, str(source))
import two_store_crash_cuts as base
import exact_authority_cuts as exact

with tempfile.TemporaryDirectory(prefix="f1-paired-stale-") as directory:
    root = pathlib.Path(directory)
    base.make_image(root / "old.sqlite", 0)
    base.make_image(root / "new.sqlite", 1)
    old_digest = base.sha(root / "old.sqlite")
    base.make_store(root / "authority.sqlite", old_digest)
    base.make_store(root / "witness.sqlite", old_digest)
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        exact.reader(root)
    result = json.loads(capture.getvalue())
    print(json.dumps({
        "external_fixture_current_epoch": 1,
        "authority": result["authority"],
        "witness": result["witness"],
        "old_candidate": result["candidates"]["old"],
        "new_candidate": result["candidates"]["new"],
    }, indent=2, sort_keys=True))
