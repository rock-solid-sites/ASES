"""Process-loss experiment for an owner of one SQLite store. Run directly."""
import json
import multiprocessing as mp
import secrets
import sqlite3
from multiprocessing.connection import wait
from pathlib import Path
from tempfile import TemporaryDirectory

SCHEMA = """
CREATE TABLE IF NOT EXISTS grants(
  token TEXT PRIMARY KEY, w TEXT NOT NULL, p TEXT NOT NULL, generation INTEGER NOT NULL,
  UNIQUE(w, p, generation));
CREATE TABLE IF NOT EXISTS selectors(
  w TEXT, p TEXT, current TEXT NOT NULL REFERENCES grants(token), PRIMARY KEY(w,p));
CREATE TABLE IF NOT EXISTS appends(
  receipt INTEGER PRIMARY KEY, token TEXT NOT NULL REFERENCES grants(token),
  nonce TEXT NOT NULL, resource TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(token,nonce));
"""


def send(pipe, message):
    pipe.send_bytes(json.dumps(message).encode())


def receive(pipe):
    if not pipe.poll(10):
        raise TimeoutError("missing owner or client event")
    return json.loads(pipe.recv_bytes())


def install(db, w, p, expected):
    row = db.execute("""SELECT generation FROM grants JOIN selectors ON token=current
                        WHERE selectors.w=? AND selectors.p=?""", (w, p)).fetchone()
    generation = row[0] if row else -1
    if generation != expected:
        return ["superseded"]
    token = secrets.token_hex(32)
    db.execute("INSERT INTO grants VALUES(?,?,?,?)", (token, w, p, generation + 1))
    db.execute("""INSERT INTO selectors VALUES(?,?,?) ON CONFLICT(w,p)
                  DO UPDATE SET current=excluded.current""", (w, p, token))
    return ["issued", token]


def worker_request(db, request):
    op, token, *args = request
    grant = db.execute("""SELECT g.w,g.p,s.current FROM grants g JOIN selectors s
                          ON g.w=s.w AND g.p=s.p WHERE g.token=?""", (token,)).fetchone()
    if not grant:
        return ["unknown"]
    w, p, current = grant
    if op == "append" and len(args) == 3:
        nonce, resource, payload = args
        if resource not in ("A", "B"):
            return ["resource"]
        old = db.execute("SELECT receipt,resource,payload FROM appends WHERE token=? AND nonce=?",
                         (token, nonce)).fetchone()
        if old:
            return ["receipt", old[0]] if tuple(args[1:]) == old[1:] else ["conflict"]
        if token != current:
            return ["stale"]
        cursor = db.execute("INSERT INTO appends(token,nonce,resource,payload) VALUES(?,?,?,?)",
                            (token, nonce, resource, payload))
        return ["receipt", cursor.lastrowid]
    if op == "read" and not args:
        if token != current:
            return ["stale"]
        rows = db.execute("""SELECT a.resource,a.payload FROM appends a JOIN grants g
                             ON g.token=a.token WHERE g.w=? AND g.p=? ORDER BY a.receipt""",
                          (w, p))
        return ["contents", list(rows)]
    return ["invalid"]


def owner(path, admin, worker):
    with sqlite3.connect(path, isolation_level=None) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA synchronous=FULL")
        db.executescript(SCHEMA)
        pause = None
        send(admin, "ready")
        while True:
            pipe = wait((admin, worker))[0]
            request = receive(pipe)
            if pipe == admin and request[0] == "stop":
                return
            if pipe == admin and request[0] == "pause":
                pause = request[1]
                send(admin, "armed")
                continue
            if pipe == worker and pause == "before admission":
                # A delivered proposal can wait while management replaces X.
                send(admin, "queued")
                command = receive(admin)
                assert command[0] == "install"
                db.execute("BEGIN IMMEDIATE")
                issued = install(db, *command[1:])
                db.commit()
                send(admin, issued)
                pause = None
            db.execute("BEGIN IMMEDIATE")
            if pipe == admin:
                assert request[0] == "install"
                result = install(db, *request[1:])
            else:
                result = worker_request(db, request)
            if pipe == worker and pause == "before commit":
                send(admin, pause)
                receive(admin)  # harness kills this process while parked
            db.commit()
            if pipe == worker and pause == "after commit":
                send(admin, pause)
                receive(admin)
            send(pipe, result)


class Fixture:
    def __init__(self, path):
        self.path = path
        self.ctx = mp.get_context("spawn")
        self.start()

    def start(self):
        self.admin, control = self.ctx.Pipe()
        self.worker, calls = self.ctx.Pipe()
        self.process = self.ctx.Process(target=owner, args=(self.path, control, calls))
        self.process.start()
        control.close()
        calls.close()
        assert receive(self.admin) == "ready"

    def stop(self, crash=False):
        if crash:
            self.process.kill()
        else:
            send(self.admin, ["stop"])
        self.process.join(10)
        assert self.process.exitcode is not None
        assert (self.process.exitcode < 0) if crash else (self.process.exitcode == 0)
        self.admin.close()
        self.worker.close()

    def call(self, pipe, message):
        send(pipe, message)
        return receive(pipe)

    def grant(self, expected, w="W", p="P"):
        result = self.call(self.admin, ["install", w, p, expected])
        assert result[0] == "issued"
        return result[1]


def trial(path, window):
    f = Fixture(path)
    try:
        x = f.grant(-1)
        neighbour = f.grant(-1, p="Q")
        assert f.call(f.worker, ["append", neighbour, "first", "A", "private Q"]) == ["receipt", 1]
        assert f.call(f.worker, ["append", "unknown", "first", "A", "bad"]) == ["unknown"]
        assert f.call(f.worker, ["install", x, "W", "P", 0]) == ["invalid"]
        msg = ["append", x, "first", "A", "X bytes"]
        assert f.call(f.admin, ["pause", window]) == "armed"
        # This executor has just the worker channel and its issued request. It
        # exits immediately after sending. The owner need not observe that exit.
        executor = f.ctx.Process(target=send, args=(f.worker, msg))
        executor.start()
        executor.join(10)
        assert executor.exitcode == 0
        stage = receive(f.admin)
        if window == "before admission":
            assert stage == "queued"
            y = f.grant(0)
            assert receive(f.worker) == ["stale"]
        else:
            assert stage == window
            f.stop(crash=True)
            f.start()
            y = f.grant(0)
        committed = window == "after commit"
        assert f.call(f.worker, msg) == (["receipt", 2] if committed else ["stale"])
        altered = ["append", x, "first", "A", "different"]
        assert f.call(f.worker, altered) == (["conflict"] if committed else ["stale"])
        assert f.call(f.worker, ["append", x, "fresh", "B", "old"]) == ["stale"]
        assert f.call(f.worker, ["read", x]) == ["stale"]
        assert f.call(f.worker, ["append", y, "first", "B", "Y bytes"])[0] == "receipt"
        expected = ([["A", "X bytes"]] if committed else []) + [["B", "Y bytes"]]
        assert f.call(f.worker, ["read", y]) == ["contents", expected]
        assert f.call(f.worker, ["read", neighbour]) == ["contents", [["A", "private Q"]]]
        assert f.call(f.admin, ["install", "W", "P", 0]) == ["superseded"]
        print(window, "old retry:", "original receipt" if committed else "stale", "Y sees", expected)
    finally:
        if f.process.is_alive():
            f.stop()


if __name__ == "__main__":
    print("SQLite", sqlite3.sqlite_version)
    with TemporaryDirectory() as temp:
        for index, window in enumerate(("before admission", "before commit", "after commit")):
            trial(str(Path(temp) / f"owner-{index}.db"), window)
