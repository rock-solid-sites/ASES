"""Crash-cut experiment for staging contents before the surviving admission decision."""

from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import select
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event


def initialize(root):
    for filename, schema in {
        "content.db": "CREATE TABLE blobs (digest TEXT PRIMARY KEY, value BLOB NOT NULL);",
        "witness.db": """
            CREATE TABLE scope (generation INTEGER NOT NULL);
            INSERT INTO scope VALUES (1);
            CREATE TABLE accepted (
                ordinal INTEGER PRIMARY KEY,
                generation INTEGER NOT NULL,
                nonce TEXT NOT NULL,
                digest TEXT NOT NULL,
                UNIQUE (generation, nonce)
            );
        """,
        "owner.db": "CREATE TABLE local (digest TEXT PRIMARY KEY);",
    }.items():
        with closing(sqlite3.connect(root / filename)) as db:
            db.executescript(schema)


def stage(root, digest, value):
    with closing(sqlite3.connect(root / "content.db")) as db, db:
        db.execute("INSERT OR IGNORE INTO blobs VALUES (?, ?)", (digest, value))
        assert db.execute("SELECT value FROM blobs WHERE digest=?", (digest,)).fetchone() == (value,)


def pause(cut, here, reply=None):
    if cut == here:
        print(json.dumps({"cut": here, "visible_reply": reply}), flush=True)
        Event().wait()


def append(root, generation, nonce, value, cut=None, variant="normal"):
    digest = sha256(value).hexdigest()
    if variant != "unstaged":
        stage(root, digest, value)
    pause(cut, "after stage")

    if variant == "owner first":
        with closing(sqlite3.connect(root / "owner.db")) as db, db:
            db.execute("INSERT INTO local VALUES (?)", (digest,))
        pause(cut, "owner acknowledged first", ["accepted", 1])
        raise AssertionError("owner-first control must stop before witness")

    with closing(sqlite3.connect(root / "witness.db")) as db:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute(
            "SELECT ordinal, digest FROM accepted WHERE generation=? AND nonce=?",
            (generation, nonce),
        ).fetchone()
        current, = db.execute("SELECT generation FROM scope").fetchone()
        if old is not None:
            ordinal, original = old
            reply = ["accepted", ordinal] if original == digest else ["conflict"]
        elif generation != current:
            reply = ["stale"]
        else:
            ordinal = db.execute(
                "INSERT INTO accepted(generation, nonce, digest) VALUES (?, ?, ?)",
                (generation, nonce, digest),
            ).lastrowid
            reply = ["accepted", ordinal]
        pause(cut, "before witness commit")
        db.commit()
    pause(cut, "after witness commit")
    if reply[0] == "accepted":
        with closing(sqlite3.connect(root / "owner.db")) as db, db:
            db.execute("INSERT OR IGNORE INTO local VALUES (?)", (digest,))
    pause(cut, "after cache publication")
    pause(cut, "after reply", reply)
    return reply


def observed(root):
    with closing(sqlite3.connect(root / "witness.db")) as db:
        entries = db.execute("SELECT ordinal, digest FROM accepted ORDER BY ordinal").fetchall()
    with closing(sqlite3.connect(root / "content.db")) as db:
        values = []
        for ordinal, digest in entries:
            row = db.execute("SELECT value FROM blobs WHERE digest=?", (digest,)).fetchone()
            if row is None or sha256(row[0]).hexdigest() != digest:
                raise ValueError(f"missing or invalid committed material for ordinal {ordinal}")
            values.append((ordinal, row[0]))
        return values


def kill_at(root, cut, variant="normal"):
    with subprocess.Popen(
        [sys.executable, __file__, "child", str(root), cut, variant],
        stdout=subprocess.PIPE, text=True,
    ) as child:
        try:
            ready, _, _ = select.select([child.stdout], [], [], 15)
            assert ready, f"child failed to reach {cut!r}"
            receipt = json.loads(child.stdout.readline())
            assert receipt["cut"] == cut, receipt
        finally:
            child.kill()
            child.wait(timeout=15)
    assert child.returncode < 0
    return receipt["visible_reply"]


def run_cut(cut, committed):
    with TemporaryDirectory() as directory:
        root = Path(directory)
        initialize(root)
        image = (root / "owner.db").read_bytes()
        visible = kill_at(root, cut)
        assert visible == (["accepted", 1] if cut == "after reply" else None)
        (root / "owner.db").write_bytes(image)
        with closing(sqlite3.connect(root / "witness.db")) as db, db:
            assert db.execute("UPDATE scope SET generation=2 WHERE generation=1").rowcount == 1
        old_contents = [(1, b"alpha")] if committed else []
        assert observed(root) == old_contents
        expected = ["accepted", 1] if committed else ["stale"]
        for _ in range(2):
            assert append(root, 1, "id", b"alpha") == expected
            assert observed(root) == old_contents
        assert append(root, 1, "fresh", b"stale work") == ["stale"]
        if committed:
            assert append(root, 1, "id", b"changed content") == ["conflict"]
        successor_ordinal = len(old_contents) + 1
        assert append(root, 2, "id", b"beta") == ["accepted", successor_ordinal]
        assert observed(root) == [*old_contents, (successor_ordinal, b"beta")]
        print(f"{cut}: killed worker, restored owner image, committed={committed}, replay checked")


def early_ack_control():
    retained = []
    replies = []
    for cut, variant in [("after stage", "normal"), ("owner acknowledged first", "owner first")]:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            initialize(root)
            image = (root / "owner.db").read_bytes()
            replies.append(kill_at(root, cut, variant))
            (root / "owner.db").write_bytes(image)
            retained.append(tuple((root / name).read_bytes() for name in
                                  ("owner.db", "content.db", "witness.db")))
            assert observed(root) == []
    assert retained[0] == retained[1] and replies == [None, ["accepted", 1]]
    print("early-ack control: identical recovered files despite a lost acknowledged append")


def unstaged_control():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        initialize(root)
        assert kill_at(root, "after reply", "unstaged") == ["accepted", 1]
        try:
            observed(root)
        except ValueError as error:
            assert "missing or invalid committed material" in str(error)
        else:
            raise AssertionError("commit without surviving data did not fail")
        print("unstaged control: acknowledged witness refers to missing committed material")


def main():
    print(f"SQLite {sqlite3.sqlite_version}")
    for cut, committed in [
        ("after stage", False), ("before witness commit", False),
        ("after witness commit", True), ("after cache publication", True),
        ("after reply", True),
    ]:
        run_cut(cut, committed)
    early_ack_control()
    unstaged_control()


if __name__ == "__main__":
    if sys.argv[1:2] == ["child"]:
        append(Path(sys.argv[2]), 1, "id", b"alpha", sys.argv[3], sys.argv[4])
    else:
        main()
