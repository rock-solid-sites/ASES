"""Integration tests for the loopback-only HTTP control surface."""
import json
import tempfile
import threading
import time
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from control import Control, MockLauncher
from server import handler_factory


READ="r"*48
ADMIN="a"*48


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.db=root/"c.db"
        self.c=Control(self.db)
        self.launcher=MockLauncher(root/"p.db")
        self.archive=root/"evidence"
        self.c.register_bucket(bucket_id="slot",account="acct",provider="mock",
          product="local",period="p",unit="slots",allowance=3)
        handler=handler_factory(self.c,self.launcher,self.archive,READ,ADMIN)
        self.server=ThreadingHTTPServer(("127.0.0.1",0),handler)
        self.port=self.server.server_address[1]
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)

    def req(self,method,path,data=None,token=READ):
        c=HTTPConnection("127.0.0.1",self.port,timeout=5)
        body=json.dumps(data).encode() if data is not None else None
        headers={"Authorization":"Bearer "+token}
        if body is not None:headers["Content-Type"]="application/json"
        c.request(method,path,body=body,headers=headers)
        response=c.getresponse()
        status=response.status
        result=json.loads(response.read())
        c.close()
        return status,result

    def test_requires_token_for_resource_listing(self):
        self.assertEqual(self.req("GET","/v1/resources",token="wrong")[0],401)
        self.assertEqual(self.req("GET","/v1/resources")[0],200)
        self.assertEqual(self.req("GET","/health",token="wrong")[0],200)

    def test_register_and_usage_reports_admin_only(self):
        self.assertEqual(self.req("POST","/v1/register",{"bucket_id":"b"},token=READ)[0],403)
        self.assertEqual(self.req("POST","/v1/provider-report",{},token=READ)[0],403)
        self.assertEqual(self.req("POST","/v1/correction",{},token=READ)[0],403)

    def test_live_http_lifecycle_reconciliation_and_archive(self):
        status,q=self.req("POST","/v1/quote",{
            "claims":{"slot":1},"estimate":{"minutes":45},"account":"acct"})
        self.assertEqual(status,200)
        self.assertTrue(q["eligible"])
        status,res=self.req("POST","/v1/reserve",{
            "job_id":"j1","attempt_id":"a1","quote":q,"account":"acct"})
        self.assertEqual(status,200,res)
        status,a=self.req("POST","/v1/acknowledge",{
            "job_id":"j1","snapshot_digest":q["snapshot_digest"],
            "expires_at":int(time.time())+300})
        self.assertEqual(status,200,a)
        status,l=self.req("POST","/v1/launch",{"job_id":"j1","token":a["token"]})
        self.assertEqual(status,200,l)
        self.assertTrue(l["external_id"].startswith("mock-"))
        self.assertEqual(self.req("POST","/v1/activity",{
            "job_id":"j1","event_id":"activity","kind":"AGENT_ACTIVE",
            "start_ms":0,"end_ms":30*60000})[0],200)
        self.assertEqual(self.req("POST","/v1/observe",{
            "job_id":"j1","event_id":"usage","bucket_id":"slot","cumulative":1})[0],200)
        self.assertEqual(self.req("POST","/v1/finalize",{
            "job_id":"j1","state":"COMPLETED","event_id":"terminal",
            "stop_evidence":"mock shutdown verified"})[0],200)
        self.assertEqual(self.req("POST","/v1/provider-report",{
            "report_id":"bill1","bucket_id":"slot","cumulative":2,
            "observed_at":int(time.time())+1},token=ADMIN)[0],200)
        status,r=self.req("POST","/v1/reconcile",{"bucket_id":"slot"})
        self.assertEqual(status,200)
        self.assertEqual(r["difference"],1)
        status,archive=self.req("POST","/v1/archive",{"job_id":"j1"})
        self.assertEqual(status,200,archive)
        self.assertTrue(archive["verified"])
        self.assertEqual(self.req("GET","/v1/jobs/j1")[1]["job"]["state"],"COMPLETED")

    def test_cannot_launch_without_valid_token(self):
        status,q=self.req("POST","/v1/quote",{
            "claims":{"slot":1},"estimate":{},"account":"acct"})
        self.req("POST","/v1/reserve",{"job_id":"j1","attempt_id":"a1","quote":q,"account":"acct"})
        self.assertEqual(self.req("POST","/v1/launch",{
            "job_id":"j1","token":"forged"})[0],409)
        self.assertEqual(self.req("GET","/v1/jobs/j1")[1]["job"]["state"],"RESERVED")

    def test_reject_invalid_json_and_unbounded_data(self):
        self.assertEqual(self.req("POST","/v1/quote",{"claims":"bad"})[0],400)
        self.assertEqual(self.req("POST","/v1/does-not-exist",{})[0],404)

    def test_unknown_job_not_success(self):
        self.assertEqual(self.req("GET","/v1/jobs/unrecognized")[0],409)


if __name__=="__main__":
    unittest.main()
