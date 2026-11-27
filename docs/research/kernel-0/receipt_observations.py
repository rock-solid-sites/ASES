"""Compare completed low-scope replies across hidden appends using the SQL handler."""
from itertools import combinations
import sqlite3

from local_handover_owner import SCHEMA, install, worker_request


def replies(hidden_at, scoped):
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(SCHEMA)
        x = install(db, "W", "P", -1)[1]
        q = install(db, "W", "Q", -1)[1]
        y = None
        visible = []
        low_step = 0
        for pos in range(7 + len(hidden_at)):
            if pos in hidden_at:
                result = worker_request(db, ["append", q, str(pos), "B", "other"], scoped)
                assert result[0] == "receipt"
                continue
            if low_step == 2:
                y = install(db, "W", "P", 0)[1]
                visible.append(["issued", "Y"])  # compare fresh handles up to renaming
            else:
                calls = {0: ["append", x, "start", "A", "one"],
                         1: ["read", x],
                         3: ["append", x, "start", "A", "one"],
                         4: ["append", x, "new", "A", "two"],
                         5: ["append", y, "start", "B", "three"],
                         6: ["read", y]}
                visible.append(worker_request(db, calls[low_step], scoped))
            low_step += 1
        return visible
    finally:
        db.close()


if __name__ == "__main__":
    for scoped in (False, True):
        baseline = replies((), scoped)
        checked = different = 0
        for n in range(4):
            for positions in combinations(range(7 + n), n):
                checked += 1
                different += replies(positions, scoped) != baseline
        assert checked == 165
        # Only the two slots after the last P append preserve global ordinals.
        unchanged_global = sum(n + 1 for n in range(4))
        assert different == (0 if scoped else checked - unchanged_global)
        print("scoped" if scoped else "global", different, "changed low traces of", checked)
