"""Check cardinality-stamped recovery with known prepared data and precedence."""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
import subprocess
import sys


def ideal(mask, edges):
    return all(not (mask >> later & 1) or mask >> earlier & 1 for earlier, later in edges)


def check_orders(n):
    pairs = tuple(combinations(range(n), 2))
    total = ambiguous = 0
    for selected in range(1 << len(pairs)):
        edges = [pair for j, pair in enumerate(pairs) if selected >> j & 1]
        counts = Counter(mask.bit_count() for mask in range(1 << n) if ideal(mask, edges))
        # Independent execution oracle: every prefix of every admissible order.
        cuts = defaultdict(set)
        for order in permutations(range(n)):
            if any(order.index(a) > order.index(b) for a, b in edges):
                continue
            chosen = 0
            cuts[0].add(chosen)
            for k, i in enumerate(order, 1):
                chosen |= 1 << i
                cuts[k].add(chosen)
        assert counts == {k: len(v) for k, v in cuts.items()}
        thin = max(counts.values()) == 1
        # Arcs are forward in this labelling. All adjacent relations must
        # be present for the reachability order to be a chain.
        assert thin == all((i, i+1) in edges for i in range(n-1))
        total += 1
        ambiguous += not thin
    print(n, "events", total, "forward graphs", ambiguous, "with ambiguous rank")


def prepared(path):
    with sqlite3.connect(path / "prepared.db") as db:
        db.execute("CREATE TABLE choices(unit TEXT, old TEXT, proposed TEXT)")
        db.executemany("INSERT INTO choices VALUES(?,?,?)", (("A", "", "alpha"), ("B", "", "beta")))
    with sqlite3.connect(path / "stamp.db") as stamp:
        stamp.execute("CREATE TABLE progress(k INTEGER NOT NULL)")
        stamp.execute("INSERT INTO progress VALUES(0)")


def publish(path, unit):
    with sqlite3.connect(path / "prepared.db") as db:
        row = db.execute("SELECT proposed FROM choices WHERE unit=?", (unit,)).fetchone()
        assert row
    with sqlite3.connect(path / "stamp.db") as stamp:
        stamp.execute("UPDATE progress SET k=k+1")
    print(json.dumps(["accepted", unit, row[0]]), flush=True)


def recovery_view(path):
    # Compare complete physical images, including incidental representation differences.
    return tuple((path / name).read_bytes() for name in ("prepared.db", "stamp.db"))


def histories():
    views = []
    replies = []
    for unit in ("A", "B"):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            prepared(path)
            child = subprocess.run([sys.executable, __file__, "publish", directory, unit],
                                   check=True, capture_output=True, text=True, timeout=15)
            replies.append(json.loads(child.stdout))
            views.append(recovery_view(path))
    assert views[0] == views[1]
    assert replies == [["accepted", "A", "alpha"], ["accepted", "B", "beta"]]
    print("different acknowledged updates; both recovered SQLite files byte-identical")


if __name__ == "__main__":
    if sys.argv[1:2] == ["publish"]:
        publish(Path(sys.argv[2]), sys.argv[3])
    else:
        for n in (3, 4, 5):
            check_orders(n)
        # Three independent chains of length four.
        ranks = Counter(map(sum, product(range(5), repeat=3)))
        assert ranks[6] == 19
        print("three chains of four, cuts at rank six", ranks[6])
        histories()
