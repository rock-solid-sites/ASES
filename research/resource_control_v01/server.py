"""Loopback-only experimental HTTP facade for the resource authorization prototype.

No real provider credentials or launch routes. Start with a strong API token in
RESOURCE_CONTROL_TOKEN; separate RESOURCE_CONTROL_ADMIN_TOKEN authorizes writes
that change provider facts or manually correct accounts.
"""
import argparse
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from archive import archive, verify, restore
from control import Control, MockLauncher, Rejected, run_mock, recover_mock


def handler_factory(control, launcher, archive_directory, read_token, admin_token):
    if len(read_token)<32 or len(admin_token)<32:
        raise ValueError("tokens must be 32+ characters")
    class Handler(BaseHTTPRequestHandler):
        protocol_version="HTTP/1.1"

        def respond(self, status, data):
            body=json.dumps(data,sort_keys=True,allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.send_header("Cache-Control","no-store")
            self.send_header("Connection","close")
            self.close_connection=True
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def authorized(self, admin=False):
            bearer=self.headers.get("Authorization","")
            if not bearer.startswith("Bearer "):return False
            provided=bearer[len("Bearer "):]
            token=admin_token if admin else read_token
            return hmac.compare_digest(provided,token) or (
                not admin and hmac.compare_digest(provided,admin_token))

        def do_GET(self):
            path=urlsplit(self.path)
            if path.path=="/health":
                return self.respond(200,{"ok":True,"mode":"experimental-mock-only"})
            if not self.authorized():
                return self.respond(401,{"error":"UNAUTHORIZED"})
            try:
                if path.path=="/v1/resources":
                    account=parse_qs(path.query).get("account",[None])[0]
                    result=control.snapshot(account=account)
                elif path.path.startswith("/v1/jobs/"):
                    result=control.status(path.path[len("/v1/jobs/"):])
                elif path.path=="/v1/events":
                    job_id=parse_qs(path.query).get("job_id",[None])[0]
                    result=control.events(job_id)
                elif path.path=="/v1/pending":
                    result=control.unresolved_launches()
                else:return self.respond(404,{"error":"NOT_FOUND"})
                self.respond(200,result)
            except (Rejected,ValueError) as e:
                self.respond(409,{"error":getattr(e,"code","INVALID_REQUEST")})

        def do_POST(self):
            if not self.authorized():
                return self.respond(401,{"error":"UNAUTHORIZED"})
            path=urlsplit(self.path).path
            privileged=path in ("/v1/register","/v1/provider-report","/v1/correction","/v1/usage-adjustment","/v1/bucket-refresh")
            if privileged and not self.authorized(admin=True):
                return self.respond(403,{"error":"ADMIN_REQUIRED"})
            try:
                length=int(self.headers.get("Content-Length","-1"))
                if length<0 or length>1_000_000:
                    return self.respond(413,{"error":"INVALID_LENGTH"})
                obj=json.loads(self.rfile.read(length))
                if not isinstance(obj,dict):raise ValueError("object required")
                # Explicit allowlist: never call arbitrary python attributes.
                if path=="/v1/quote":result=control.quote(**obj)
                elif path=="/v1/reserve":result=control.reserve(**obj)
                elif path=="/v1/acknowledge":result=control.acknowledge(**obj)
                elif path=="/v1/launch":result={"external_id":run_mock(control,launcher,**obj)}
                elif path=="/v1/observe":result=control.observe(**obj)
                elif path=="/v1/activity":result=control.record_activity(**obj)
                elif path=="/v1/interrupt":result=control.interrupt(**obj)
                elif path=="/v1/finalize":result=control.finalize(**obj)
                elif path=="/v1/reconcile":result=control.reconcile_bucket(**obj)
                elif path=="/v1/provider-report":result=control.provider_report(**obj)
                elif path=="/v1/correction":result=control.manual_correction(**obj)
                elif path=="/v1/usage-adjustment":result=control.adjust_usage(**obj)
                elif path=="/v1/register":result=control.register_bucket(**obj) or {"registered":True}
                elif path=="/v1/bucket-refresh":result=control.refresh_bucket(**obj)
                elif path=="/v1/recover":result=recover_mock(control,launcher)
                elif path=="/v1/expire":result=control.expire_unlaunched(**obj)
                elif path=="/v1/archive":result=archive(control,obj["job_id"],archive_directory)
                else:return self.respond(404,{"error":"NOT_FOUND"})
                self.respond(200,result)
            except Rejected as e:
                self.respond(409,{"error":e.code})
            except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
                self.respond(400,{"error":"INVALID_REQUEST","detail":str(e)[:160]})

        def log_message(self, fmt, *args):
            # Deliberately avoid printing URLs, bearer credentials or request bodies.
            return
    return Handler


def serve(*, db, mock_db, archive_directory, token, admin_token, host="127.0.0.1", port=8765):
    if host not in ("127.0.0.1","::1"):
        raise ValueError("loopback only")
    control=Control(db)
    launcher=MockLauncher(mock_db)
    handler=handler_factory(control,launcher,archive_directory,token,admin_token)
    server=ThreadingHTTPServer((host,port),handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",required=True)
    parser.add_argument("--mock-db",required=True)
    parser.add_argument("--archive-directory",required=True)
    parser.add_argument("--port",type=int,default=8765)
    args=parser.parse_args()
    token=os.environ.get("RESOURCE_CONTROL_TOKEN","")
    admin=os.environ.get("RESOURCE_CONTROL_ADMIN_TOKEN","")
    serve(db=args.db,mock_db=args.mock_db,archive_directory=args.archive_directory,
          token=token,admin_token=admin,port=args.port)
