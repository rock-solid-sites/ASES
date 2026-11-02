"""Adversarial and positive-neighbor tests for the resource-control research slice."""
import multiprocessing as mp
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from control import Control, MockLauncher, Rejected, run_mock, recover_mock


def worker_reserve(db, job, attempt, q, output):
    ctl=Control(db)
    try:
        ctl.reserve(job_id=job,attempt_id=attempt,quote=q,account="acct")
        output.put("OK")
    except Rejected as e:
        output.put(e.code)


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.db=self.base/"control.sqlite"
        self.c=Control(self.db)
        self.launcher=MockLauncher(self.base/"mock-provider.sqlite")
        self.now=int(time.time())
        self.c.register_bucket(bucket_id="cpu",account="acct",provider="mock",
                               product="codespace",period="2026-11",unit="core-minutes",
                               allowance=120,observed_at=self.now,ttl_seconds=3600)
        self.c.register_bucket(bucket_id="storage",account="acct",provider="mock",
                               product="codespace",period="2026-11",unit="gb-minutes",
                               allowance=1000,observed_at=self.now,ttl_seconds=3600)

    def quote(self, n=45, claims=None):
        return self.c.quote(claims=claims if claims is not None else {"cpu":n},
                            estimate={"wall_minutes":n,"model":"mock"},account="acct",now=self.now)

    def reserved(self, n=45, job="j1", attempt="a1", claims=None):
        q=self.quote(n,claims)
        self.assertTrue(q["eligible"],q)
        self.c.reserve(job_id=job,attempt_id=attempt,quote=q,account="acct",now=self.now)
        return q

    def started(self, n=45, job="j1", attempt="a1", claims=None):
        q=self.reserved(n,job,attempt,claims)
        auth=self.c.acknowledge(job,snapshot_digest=q["snapshot_digest"],expires_at=self.now+3000)
        run_mock(self.c,self.launcher,job,auth["token"],now=self.now)
        return q,auth

    def capacity(self):
        return {b["id"]:b for b in self.c.snapshot(now=self.now)["buckets"]}

    def assertRejected(self,code,fn):
        with self.assertRaises(Rejected) as cm:fn()
        self.assertEqual(cm.exception.code,code)

    def test_shorter_execution_releases_unused_reservation(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=30)
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="mock stopped")
        self.assertEqual(self.capacity()["cpu"]["available"],90)
        self.assertEqual(self.capacity()["cpu"]["reserved"],0)
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],30)

    def test_longer_execution_records_real_overrun_and_freezes(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=60)
        r=self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="mock stopped")
        self.assertEqual(r["overruns"],[{"bucket_id":"cpu","overrun":15}])
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],60)
        self.assertEqual(self.capacity()["cpu"]["available"],60)
        self.assertTrue(self.capacity()["cpu"]["frozen"])
        self.assertIn(["cpu","FROZEN"],self.quote(1)["issues"])

    def test_activity_not_equated_to_runtime_or_provider_fault(self):
        self.started()
        self.c.record_activity("j1",event_id="e1",kind="ENVIRONMENT_RUNNING",
                               start_ms=0,end_ms=60*60000)
        self.c.record_activity("j1",event_id="e2",kind="AGENT_ACTIVE",
                               start_ms=5*60000,end_ms=35*60000)
        kinds=[e["kind"] for e in self.c.events("j1")]
        self.assertEqual(kinds.count("ACTIVITY"),2)
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=60)
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="mock stopped")
        self.assertFalse(any(e["kind"]=="PROVIDER_FAULT" for e in self.c.events("j1")))

    def test_activity_duplicate_same_data_and_collision_other_data(self):
        self.started()
        args=dict(event_id="clock1",kind="IDLE",start_ms=0,end_ms=60000)
        self.assertFalse(self.c.record_activity("j1",**args)["duplicate"])
        self.assertTrue(self.c.record_activity("j1",**args)["duplicate"])
        self.assertRejected("EVENT_ID_COLLISION",lambda:self.c.record_activity(
            "j1",event_id="clock1",kind="IDLE",start_ms=0,end_ms=123))

    def test_negative_activity_duration_rejected(self):
        self.started()
        with self.assertRaises(ValueError):
            self.c.record_activity("j1",event_id="z",kind="IDLE",start_ms=2,end_ms=1)

    def test_late_observation_after_finalization_is_rejected(self):
        self.started()
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="stopped")
        self.assertRejected("INVALID_STATE",lambda:self.c.observe(
            "j1",event_id="late",bucket_id="cpu",cumulative=2))

    def test_terminated_without_stop_evidence_rejected(self):
        self.started()
        self.assertRejected("MISSING_STOP_EVIDENCE",lambda:self.c.finalize(
            "j1",state="COMPLETED",event_id="done"))
        self.assertEqual(self.capacity()["cpu"]["reserved"],45)

    def test_interrupt_does_not_release_capacity(self):
        self.started()
        self.c.interrupt("j1",event_id="interrupt1")
        self.assertEqual(self.capacity()["cpu"]["reserved"],45)
        self.assertEqual(self.c.status("j1")["job"]["state"],"INTERRUPTED")
        self.assertRejected("MISSING_STOP_EVIDENCE",lambda:self.c.finalize(
            "j1",state="FAILED",event_id="done"))
        self.c.finalize("j1",state="FAILED",event_id="done",stop_evidence="provider stopped")
        self.assertEqual(self.capacity()["cpu"]["reserved"],0)

    def test_empty_claims_fail_prevent_unbounded_agent_launch(self):
        q=self.quote(claims={})
        self.assertRejected("NO_RESOURCE_CLAIMS",lambda:self.c.reserve(
            job_id="j1",attempt_id="a1",quote=q,account="acct",now=self.now))

    def test_free_only_job_uses_finite_nonchargeable_slot(self):
        self.c.register_bucket(bucket_id="slots",account="acct",provider="mock",
            product="local",period="2026-11",unit="launch-slots",
            allowance=1,observed_at=self.now)
        self.reserved(claims={"slots":1})
        self.assertEqual(self.capacity()["slots"]["available"],0)
        self.assertFalse(self.quote(claims={"slots":1})["eligible"])

    def test_multi_meter_is_atomic(self):
        q=self.quote(claims={"cpu":5,"storage":2000})
        self.assertFalse(q["eligible"])
        self.assertRejected("INVALID_QUOTE",lambda:self.c.reserve(
            job_id="j1",attempt_id="a1",quote=q,account="acct",now=self.now))
        self.assertEqual(self.capacity()["cpu"]["reserved"],0)

    def test_two_meter_admission_and_release(self):
        self.reserved(claims={"cpu":45,"storage":600})
        self.assertEqual(self.capacity()["storage"]["reserved"],600)
        self.c.finalize("j1",state="CANCELLED",event_id="cancel")
        self.assertEqual(self.capacity()["storage"]["reserved"],0)
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],0)

    def test_stale_quote_after_reservation(self):
        q=self.quote(20)
        self.c.reserve(job_id="j1",attempt_id="a1",quote=q,account="acct",now=self.now)
        self.assertRejected("STALE_REVISION",lambda:self.c.reserve(
            job_id="j2",attempt_id="a2",quote=q,account="acct",now=self.now))

    def test_cross_account_bucket_excluded(self):
        self.c.register_bucket(bucket_id="alien",account="other",provider="mock",
            product="codespace",period="2026-11",unit="core-minutes",
            allowance=400,observed_at=self.now)
        q=self.quote(claims={"alien":1})
        self.assertIn(["alien","UNKNOWN_OR_CROSS_ACCOUNT"],q["issues"])

    def test_stale_provider_snapshot_fails_closed(self):
        self.c.register_bucket(bucket_id="expired",account="acct",provider="mock",
            product="model",period="2026-11",unit="requests",
            allowance=100,observed_at=self.now-100,ttl_seconds=5)
        self.assertIn(["expired","STALE"],self.quote(claims={"expired":1})["issues"])

    def test_unknown_price_fails_closed(self):
        self.c.register_bucket(bucket_id="unknown",account="acct",provider="mock",
            product="model",period="2026-11",unit="requests",
            allowance=100,price_micros=None,observed_at=self.now)
        self.assertIn(["unknown","UNKNOWN_PRICE"],self.quote(claims={"unknown":1})["issues"])

    def test_quoted_digest_is_account_scoped_and_binding(self):
        q=self.quote()
        tampered=dict(q,snapshot_digest="bad")
        self.assertRejected("STALE_SNAPSHOT",lambda:self.c.reserve(
            job_id="j1",attempt_id="a1",quote=tampered,account="acct",now=self.now))

    def test_duplicate_job_and_attempt(self):
        self.reserved()
        q=self.quote(1)
        self.assertRejected("DUPLICATE_JOB_OR_ATTEMPT",lambda:self.c.reserve(
            job_id="j1",attempt_id="a2",quote=q,account="acct",now=self.now))
        self.assertRejected("DUPLICATE_JOB_OR_ATTEMPT",lambda:self.c.reserve(
            job_id="j2",attempt_id="a1",quote=q,account="acct",now=self.now))

    def test_wrong_ack_snapshot(self):
        self.reserved()
        self.assertRejected("WRONG_SNAPSHOT",lambda:self.c.acknowledge(
            "j1",snapshot_digest="stale",expires_at=self.now+100))

    def test_wrong_and_expired_launch_token(self):
        q=self.reserved()
        a=self.c.acknowledge("j1",snapshot_digest=q["snapshot_digest"],
                             expires_at=self.now+100)
        self.assertRejected("UNAUTHORIZED",lambda:self.c.launch_prepare(
            "j1",token="wrong",now=self.now))
        self.assertRejected("EXPIRED",lambda:self.c.launch_prepare(
            "j1",token=a["token"],now=self.now+101))

    def test_crash_after_external_launch_is_recovered_without_duplication(self):
        q=self.reserved()
        a=self.c.acknowledge("j1",snapshot_digest=q["snapshot_digest"],
                             expires_at=self.now+200)
        with self.assertRaises(RuntimeError):
            run_mock(self.c,self.launcher,"j1",a["token"],now=self.now,crash_after_external=True)
        self.assertEqual(self.c.status("j1")["job"]["state"],"LAUNCH_PENDING")
        results=recover_mock(Control(self.db),MockLauncher(self.base/"mock-provider.sqlite"))
        self.assertEqual(results[0]["state"],"RUNNING")
        self.assertEqual(len(recover_mock(self.c,self.launcher)),0)
        self.assertEqual(self.c.status("j1")["job"]["external_id"],
                         self.launcher.lookup("a1"))

    def test_pending_without_provider_confirmation_not_assumed_failed(self):
        q=self.reserved()
        a=self.c.acknowledge("j1",snapshot_digest=q["snapshot_digest"],
                             expires_at=self.now+200)
        self.c.launch_prepare("j1",token=a["token"],now=self.now)
        self.assertEqual(recover_mock(self.c,self.launcher)[0]["state"],"UNKNOWN_EXTERNAL_LAUNCH")
        self.assertRejected("INVALID_STATE",lambda:self.c.finalize(
            "j1",state="CANCELLED",event_id="no-proof"))
        self.assertEqual(self.capacity()["cpu"]["reserved"],45)

    def test_duplicate_finalize_replay_does_not_charge_twice(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=30)
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="stopped")
        self.assertTrue(self.c.finalize("j1",state="COMPLETED",event_id="done")["duplicate"])
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],30)

    def test_duplicate_usage_event_no_double_count(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=20)
        self.assertTrue(self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=20)["duplicate"])
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="stopped")
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],20)

    def test_decreasing_cumulative_usage_rejected(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=20)
        self.assertRejected("NONMONOTONIC_LOCAL_OBSERVATION",lambda:self.c.observe(
            "j1",event_id="u2",bucket_id="cpu",cumulative=10))

    def test_provider_report_no_double_subtraction(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=30)
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="stopped")
        self.c.provider_report(report_id="p1",bucket_id="cpu",cumulative=50,
                               observed_at=self.now+1)
        self.assertEqual(self.capacity()["cpu"]["available"],70)
        self.assertEqual(self.c.reconcile_bucket("cpu",now=self.now)["difference"],20)

    def test_provider_lag_does_not_erase_newer_local_usage(self):
        self.started()
        self.c.observe("j1",event_id="u1",bucket_id="cpu",cumulative=30)
        self.c.finalize("j1",state="COMPLETED",event_id="done",stop_evidence="stopped")
        self.c.provider_report(report_id="p1",bucket_id="cpu",cumulative=10,
                               observed_at=self.now+1)
        self.assertEqual(self.capacity()["cpu"]["available"],90)

    def test_duplicate_and_out_of_order_provider_report(self):
        self.c.provider_report(report_id="p1",bucket_id="cpu",cumulative=80,
                               observed_at=self.now+10)
        self.assertTrue(self.c.provider_report(report_id="p1",bucket_id="cpu",
                                  cumulative=80,observed_at=self.now+10)["duplicate"])
        old=self.c.provider_report(report_id="p0",bucket_id="cpu",cumulative=20,
                                   observed_at=self.now+1)
        self.assertFalse(old["applied"])
        self.assertEqual(self.capacity()["cpu"]["available"],40)

    def test_authorization_not_reusable(self):
        q,a=self.started()
        self.assertRejected("INVALID_STATE",lambda:self.c.launch_prepare(
            "j1",token=a["token"],now=self.now))

    def test_manual_correction_append_only_does_not_grant_spend(self):
        self.started()
        self.c.manual_correction(correction_id="c1",job_id="j1",bucket_id="cpu",
            quantity=90,reason="manual review",evidence="ticket123",actor="reviewer")
        self.assertTrue(self.c.manual_correction(correction_id="c1",job_id="j1",bucket_id="cpu",
            quantity=90,reason="manual review",evidence="ticket123",actor="reviewer")["duplicate"])
        self.assertEqual(self.capacity()["cpu"]["reserved"],45)
        self.assertEqual(self.capacity()["cpu"]["local_consumed"],0)

    def test_invalid_numeric_quantities(self):
        for val in (-1,1.5,True,None,"5"):
            with self.subTest(value=val):
                with self.assertRaises(ValueError):
                    self.c.quote(claims={"cpu":val},estimate={},account="acct",now=self.now)

    def test_sqlite_restart_recovers_balances_and_events(self):
        self.reserved()
        second=Control(self.db)
        self.assertEqual(second.snapshot(now=self.now)["buckets"][0]["reserved"],45)
        self.assertTrue(second.events("j1"))

    def test_simultaneous_threads_only_one_can_claim_full_capacity(self):
        q=self.quote(120)
        def run(i):
            try:
                Control(self.db).reserve(job_id="job"+str(i),attempt_id="att"+str(i),
                    quote=q,account="acct",now=self.now)
                return True
            except Rejected:return False
        with ThreadPoolExecutor(max_workers=12) as ex:
            results=list(ex.map(run,range(12)))
        self.assertEqual(sum(results),1)

    def test_simultaneous_processes_only_one_can_claim_full_capacity(self):
        q=self.quote(120)
        context=mp.get_context("spawn")
        results=context.Queue()
        ps=[context.Process(target=worker_reserve,args=(str(self.db),"job"+str(i),
             "att"+str(i),q,results)) for i in range(4)]
        for p in ps:p.start()
        for p in ps:p.join(20)
        self.assertTrue(all(p.exitcode==0 for p in ps))
        outcomes=[results.get(timeout=2) for _ in ps]
        self.assertEqual(outcomes.count("OK"),1)

    def test_two_simultaneous_jobs_cannot_reserve_more_than_allowance(self):
        q1=self.quote(70)
        self.c.reserve(job_id="j1",attempt_id="a1",quote=q1,account="acct",now=self.now)
        q2=self.quote(60)
        self.assertIn(["cpu","INSUFFICIENT"],q2["issues"])
        self.assertEqual(self.capacity()["cpu"]["reserved"],70)

    def test_sql_injection_is_data_not_query(self):
        with self.assertRaises(ValueError):
            self.c.quote(claims={"cpu":1},estimate={},account="acct other",now=self.now)
        q=self.c.quote(claims={"cpu":1},estimate={"name":"'; DROP TABLE buckets;--"},
                       account="acct",now=self.now)
        self.assertTrue(q["eligible"])
        self.assertEqual(len(self.capacity()),2)


if __name__=="__main__":
    unittest.main()
