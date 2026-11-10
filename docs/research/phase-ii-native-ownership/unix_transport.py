"""AF_UNIX adapter for the existing local HTTP handlers; no route changes."""
import http.client
import http.server
import json
import os
from pathlib import Path
import socket
import socketserver
import stat

_server_paths: list[Path] = []
_witness_path: Path | None = None


class UnixHTTPConnection(http.client.HTTPConnection):
    """HTTP/1.1 framing over one caller-selected Unix stream socket."""
    def __init__(self, path, timeout=2.0):
        self.unix_path = str(Path(path))
        super().__init__("localhost", timeout=timeout)

    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if self.timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(self.timeout)
        if self.source_address:
            sock.bind(self.source_address)
        sock.connect(self.unix_path)
        self.sock = sock


def call_unix(path, method, request_path, data=None, timeout=2.0):
    if not isinstance(method, str) or not method.isascii() or not method.isalpha():
        raise ValueError("invalid-http-method")
    if not isinstance(request_path, str) or not request_path.startswith("/") or "\r" in request_path or "\n" in request_path:
        raise ValueError("invalid-http-path")
    body = None if data is None else json.dumps(data, separators=(",", ":")).encode()
    connection = UnixHTTPConnection(path, timeout=timeout)
    try:
        headers = {} if body is None else {"Content-Type": "application/json"}
        connection.request(method, request_path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        return response.status, json.loads(raw) if raw else {}
    finally:
        connection.close()


def install(listen_path, witness_path=None):
    """Replace shared ThreadingHTTPServer with a private AF_UNIX factory.

    Existing Handler implementations and their HTTP routes stay unchanged.
    witness_path is an existing client destination in another process; this
    process never binds or removes it.
    """
    global _server_paths, _witness_path
    listen = Path(listen_path).absolute()
    if listen.parent.is_symlink() or not listen.parent.is_dir():
        raise FileNotFoundError(listen.parent)
    if listen.parent.stat().st_mode & 0o077:
        raise PermissionError("unix-socket-parent-not-private")
    if listen.exists() or listen.is_symlink():
        raise FileExistsError(listen)
    _server_paths = [listen]
    _witness_path = None if witness_path is None else Path(witness_path).absolute()
    original = http.server.ThreadingHTTPServer

    class UnixThreadingHTTPServer(original):
        address_family = socket.AF_UNIX

        def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, **kwargs):
            if not _server_paths:
                raise RuntimeError("unix-server-paths-exhausted")
            self.unix_path = _server_paths[0]
            _server_paths.clear()
            self._bound_identity = None
            super().__init__(str(self.unix_path), RequestHandlerClass,
                             bind_and_activate=bind_and_activate, **kwargs)
            if bind_and_activate:
                st = self.unix_path.stat()
                self._bound_identity = (st.st_dev, st.st_ino)
                os.chmod(self.unix_path, 0o600)
            # Native ready frames continue to report the old port field as 0.
            self.server_address = ("unix", 0)

        def server_bind(self):
            # HTTPServer.server_bind unpacks a TCP (host, port) tuple. Bypass
            # only that TCP-specific override while retaining TCPServer bind.
            socketserver.TCPServer.server_bind(self)
            self.server_name = "unix"
            self.server_port = 0

        def server_close(self):
            super().server_close()
            try:
                st = self.unix_path.lstat()
                if self._bound_identity == (st.st_dev, st.st_ino) and stat.S_ISSOCK(st.st_mode):
                    self.unix_path.unlink()
            except FileNotFoundError:
                pass

    http.server.ThreadingHTTPServer = UnixThreadingHTTPServer
    return UnixThreadingHTTPServer


def default_witness_path():
    return _witness_path

