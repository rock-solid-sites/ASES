#!/usr/bin/env python3
"""Exercise the HTTP handler unchanged over a private AF_UNIX transport."""
import errno
import http.server
import json
import os
from pathlib import Path
import socket
import stat
import tempfile
import threading

from unix_transport import call_unix, default_witness_path, install


def main():
    output = Path(__file__).resolve().parent / "evidence/transport"
    output.mkdir(parents=True, exist_ok=True)
    raw = {}
    with tempfile.TemporaryDirectory(prefix="ases-owner-unix-") as temp:
        root = Path(temp)
        path = root / "owner.sock"
        witness_path = root / "witness.sock"
        witness = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        witness.bind(str(witness_path))
        os.chmod(witness_path, 0o600)
        witness.listen(1)

        def witness_once():
            connection, _ = witness.accept()
            with connection:
                data = bytearray()
                while b"\r\n\r\n" not in data:
                    data.extend(connection.recv(4096))
                header, body = bytes(data).split(b"\r\n\r\n", 1)
                length = int(next(line.split(b":", 1)[1].strip() for line in header.split(b"\r\n")
                                  if line.lower().startswith(b"content-length:")))
                while len(body) < length:
                    body += connection.recv(4096)
                request = json.loads(body[:length])
                reply = json.dumps({"received": request, "path": "/witness"},
                                   separators=(",", ":")).encode()
                connection.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                                   + f"Content-Length: {len(reply)}\r\nConnection: close\r\n\r\n".encode()
                                   + reply)

        witness_thread = threading.Thread(target=witness_once)
        witness_thread.start()

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length))
                payload = json.dumps({"received": request, "path": self.path},
                                     separators=(",", ":")).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_args):
                pass

        server_type = install(path, witness_path)
        witness_identity_before = (witness_path.stat().st_dev, witness_path.stat().st_ino)
        if default_witness_path() != witness_path:
            raise AssertionError("witness-path-not-retained")
        server = server_type(("127.0.0.1", 0), Handler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
        thread.start()
        mode = path.stat().st_mode & 0o777
        status, reply = call_unix(path, "POST", "/echo", {"op": "native-smoke", "value": 7})
        witness_status, witness_reply = call_unix(witness_path, "POST", "/witness", {"op": "witness-smoke"})
        witness_thread.join(timeout=2)
        wrong_path = root / "missing.sock"
        try:
            call_unix(wrong_path, "POST", "/echo", {"op": "should-fail"})
            wrong_errno = None
        except OSError as error:
            wrong_errno = error.errno
        raw = {
            "transport": "AF_UNIX",
            "server_class": server.__class__.__name__,
            "server_address": list(server.server_address),
            "socket_family": server.socket.family,
            "socket_mode": oct(mode),
            "http_status": status,
            "request": {"op": "native-smoke", "value": 7},
            "reply": reply,
            "wrong_path_errno": wrong_errno,
            "witness_status": witness_status,
            "witness_reply": witness_reply,
            "witness_untouched_by_install": witness_identity_before == (witness_path.stat().st_dev, witness_path.stat().st_ino),
            "tcp_socket": False,
        }
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        raw["socket_path_removed_on_close"] = not path.exists()
        witness.close()
        witness_path.unlink(missing_ok=True)
    expected = {"received": raw["request"], "path": "/echo"}
    raw["pass"] = (raw["server_address"] == ["unix", 0]
                   and raw["socket_family"] == socket.AF_UNIX
                   and raw["socket_mode"] == "0o600"
                   and raw["http_status"] == 200
                   and raw["reply"] == expected
                   and raw["witness_status"] == 200
                   and raw["witness_reply"] == {"received": {"op": "witness-smoke"}, "path": "/witness"}
                   and raw["witness_untouched_by_install"]
                   and raw["wrong_path_errno"] == errno.ENOENT
                   and raw["socket_path_removed_on_close"])
    (output / "smoke.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps(raw, sort_keys=True))
    if not raw["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
