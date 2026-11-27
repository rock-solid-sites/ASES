"""One local A-to-B handover of accepted contents across three SQLite files."""
import os
import sqlite3
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

COLUMNS = "seq, issuer, nonce, payload"
CUTS = ("before freeze commit", "frozen", "before first copy commit", "copied first",
        "before ready commit", "ready", "before select commit", "selected",
        "before activation commit", "active")


@contextmanager
def database(path):
    # Fail on an unavailable store; reopening must not create a replacement.
    db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)
    try:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    finally:
        db.close()  # an uncommitted transaction rolls back


def state(db):
    return db.execute("SELECT value FROM control").fetchone()[0]


def set_state(db, value):
    db.execute("UPDATE control SET value=?", (value,))


def status(path):
    with database(path) as db:
        return state(db)


def prefix(db):
    return db.execute(f"SELECT {COLUMNS} FROM log ORDER BY seq").fetchall()


def append(path, actor, nonce, payload):
    if actor not in ("X", "Y"):
        return "unknown"
    with database(path) as db:
        active = state(db)
        if active not in ("X", "Y"):
            return "defer"
        record = db.execute("SELECT seq,payload FROM log WHERE issuer=? AND nonce=?",
                            (actor, nonce)).fetchone()
        if record:
            return record[0] if record[1] == payload else "conflict"
        if actor != active:
            return "stale"
        cursor = db.execute("INSERT INTO log(issuer,nonce,payload) VALUES(?,?,?)",
                            (actor, nonce, payload))
        return cursor.lastrowid


def setup(root):
    for name, mode in (("selector", "X"), ("A", "X"), ("B", "empty")):
        path = root / name
        path.touch()
        with database(path) as db:
            db.execute("CREATE TABLE control(value TEXT NOT NULL)")
            db.execute("INSERT INTO control VALUES(?)", (mode,))
            if name != "selector":
                db.execute("""CREATE TABLE log(seq INTEGER PRIMARY KEY, issuer TEXT NOT NULL,
                              nonce TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(issuer,nonce))""")
    assert append(root / "A", "X", "first", "same bytes") == 1
    assert append(root / "A", "X", "second", "same bytes") == 2


def transfer(root, cut=None):
    def point(name):
        if name == cut:
            os._exit(83)

    if status(root / "selector") == "X":
        with database(root / "A") as db:
            assert state(db) in ("X", "frozen")
            set_state(db, "frozen")
            point("before freeze commit")
        point("frozen")
        with database(root / "A") as db:
            rows = prefix(db)
        for row in rows:
            with database(root / "B") as db:
                assert state(db) in ("empty", "ready")
                db.execute(f"INSERT INTO log({COLUMNS}) VALUES(?,?,?,?) ON CONFLICT(seq) DO NOTHING", row)
                if row[0] == 1:
                    point("before first copy commit")
            if row[0] == 1:
                point("copied first")
        with database(root / "B") as db:
            if prefix(db) != rows:
                raise ValueError("staged rows disagree with frozen source")
            set_state(db, "ready")
            point("before ready commit")
        point("ready")
        # The single coordinator owns this one decision. Freeze and readiness
        # persist monotonically until publication, including across its loss.
        with database(root / "selector") as db:
            assert state(db) == "X"
            set_state(db, "Y")
            point("before select commit")
        point("selected")
    with database(root / "B") as db:
        assert state(db) in ("ready", "Y")
        set_state(db, "Y")
        point("before activation commit")
    point("active")


def crash_at(root, cut):
    child = subprocess.run([sys.executable, __file__, "cut", str(root), cut], timeout=15)
    assert child.returncode == 83, (cut, child.returncode)


def run_cut(root, cut):
    setup(root)
    crash_at(root, cut)
    chosen = status(root / "selector")
    target = status(root / "B")
    assert target != "Y" or chosen == "Y"
    source_reply = append(root / "A", "X", "late", "after interruption")
    late = cut == "before freeze commit"
    assert source_reply == (3 if late else "defer")
    if chosen == "Y":
        # The old file becomes unavailable to all normal owner entry points.
        (root / "A").rename(root / "A.offline")
    else:
        assert append(root / "B", "Y", "premature", "new") == "defer"
    transfer(root)
    assert status(root / "selector") == "Y"
    assert append(root / "B", "X", "first", "same bytes") == 1
    assert append(root / "B", "X", "second", "same bytes") == 2
    assert append(root / "B", "X", "first", "different") == "conflict"
    assert append(root / "B", "X", "fresh", "old") == "stale"
    expected = [(1, "X", "first", "same bytes"), (2, "X", "second", "same bytes")]
    if late:
        expected.append((3, "X", "late", "after interruption"))
    receipt = len(expected) + 1
    assert append(root / "B", "Y", "first", "new") == receipt
    expected.append((receipt, "Y", "first", "new"))
    transfer(root)  # retry after publication must preserve successor appends
    with database(root / "B") as db:
        assert prefix(db) == expected
    return chosen, target, receipt


def identity_control(root):
    setup(root)
    crash_at(root, "ready")
    with database(root / "B") as db:
        db.execute("UPDATE log SET nonce='wrong' WHERE seq=1")
    try:
        transfer(root)
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched identity accepted")
    assert status(root / "selector") == "X"
    with database(root / "A") as a, database(root / "B") as b:
        assert [r[3] for r in prefix(a)] == [r[3] for r in prefix(b)]
        assert prefix(a) != prefix(b)
    # Model a publisher that accepted the byte-only comparison above.
    with database(root / "selector") as db:
        set_state(db, "Y")
    transfer(root)
    assert append(root / "B", "X", "first", "same bytes") == "stale"


def activation_control(root):
    setup(root)
    crash_at(root, "ready")
    # The accurate target contains all accepted rows; only its activation is premature.
    with database(root / "B") as db:
        set_state(db, "Y")
    assert append(root / "B", "Y", "early", "new") == 3
    assert status(root / "selector") == "X"


if __name__ == "__main__":
    if sys.argv[1:2] == ["cut"]:
        transfer(Path(sys.argv[2]), sys.argv[3])
    else:
        print("SQLite", sqlite3.sqlite_version)
        for label in CUTS:
            with TemporaryDirectory() as temp:
                print(label, run_cut(Path(temp), label))
        with TemporaryDirectory() as temp:
            identity_control(Path(temp))
        with TemporaryDirectory() as temp:
            activation_control(Path(temp))
        print("payload-only comparison and premature activation distinguished")
