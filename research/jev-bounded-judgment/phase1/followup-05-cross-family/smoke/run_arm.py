#!/usr/bin/env python3
"""Run one agent-routed general-model arm over the frozen corpus.

Chunks the 64 cases so that a single free-model failure costs 16 cases rather
than the whole arm, and so a run can resume after an interruption.

Discipline carried from Phase 1:
  - the corpus is read-only; its sha256 is asserted before and after
  - N=1 per case. A case is asked once. There is no second opinion.
  - TRANSPORT failures (no text block, non-zero exit, unparsable stream) may be
    retried up to --attempts times, and EVERY attempt is recorded.
  - VALIDATION failures (wrong count, missing ids, duplicates, or an answer the
    frozen parser rejects) are NOT retried. Those are the arm's behaviour, not
    the transport's, and retrying them would launder a result.
  - no prompt, band, or scorer code is altered by this script.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FOLLOWUP = os.path.dirname(HERE)
PHASE1 = os.path.dirname(FOLLOWUP)
sys.path.insert(0, HERE)

import build_tasks  # noqa: E402
import extract_validate as ev  # noqa: E402

EXPECTED_SHA = "7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c"


def corpus_sha():
    import hashlib
    return hashlib.sha256(
        open(os.path.join(PHASE1, "cases.ndjson"), "rb").read()).hexdigest()


def run_chunk(model_id, tag, chunk_idx, ids, outdir, attempts, prompt_tmpl):
    """Dispatch one chunk. Returns (rows, attempt_log)."""
    tasks_path = os.path.join(outdir, f"tasks-{tag}-{chunk_idx:02d}.json")
    ans_path = os.path.join(outdir, f"answers-{tag}-{chunk_idx:02d}.ndjson")
    import io
    import contextlib
    argv = sys.argv
    sys.argv = ["build_tasks.py", "--model-id", model_id,
                "--case-ids", ",".join(ids), "--out", tasks_path]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = build_tasks.main()
    finally:
        sys.argv = argv
    if rc != 0:
        return None, [{"chunk": chunk_idx, "attempt": 0, "stage": "build_tasks",
                       "error": f"exit {rc}", "stdout": buf.getvalue()[-300:]}]

    prompt = prompt_tmpl.format(tasks_file=os.path.relpath(tasks_path, FOLLOWUP),
                                n_cases=len(ids))
    events = os.path.join(outdir, f"events-{tag}-{chunk_idx:02d}.jsonl")
    log = []
    for attempt in range(1, attempts + 1):
        t0 = time.time()
        with open(events, "w", encoding="utf-8") as fh:
            proc = subprocess.run(
                ["opencode", "run", "--model", model_id, "--format", "json",
                 prompt],
                stdout=fh, stderr=subprocess.PIPE, timeout=1800,
                cwd=FOLLOWUP)
        wall = time.time() - t0
        entry = {"chunk": chunk_idx, "attempt": attempt,
                 "exit": proc.returncode, "wall_s": round(wall, 2),
                 "events_bytes": os.path.getsize(events)}
        text = ev.final_text(events)
        if proc.returncode != 0 or text is None:
            entry["stage"] = "transport"
            entry["error"] = (proc.stderr.decode("utf-8", "replace")[-400:]
                              or f"exit {proc.returncode}, no text block")
            log.append(entry)
            if attempt >= attempts:
                return None, log
            continue
        rows, bad = ev.parse_ndjson(text)
        want = set(ids)
        got = [r["case_id"] for r in rows]
        if len(rows) != len(ids) or set(got) != want or len(set(got)) != len(got):
            entry["stage"] = "validation"
            entry["error"] = (f"count={len(rows)} expected={len(ids)} "
                              f"missing={sorted(want - set(got))} "
                              f"unexpected={sorted(set(got) - want)} "
                              f"unparsable_lines={len(bad)}")
            log.append(entry)
            return None, log  # NOT retried: this is the arm's behaviour
        entry["stage"] = "ok"
        entry["n_rows"] = len(rows)
        log.append(entry)
        with open(ans_path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        return rows, log
    return None, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--chunk-size", type=int, default=16)
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--outdir", default=os.path.join(FOLLOWUP, "out"))
    ap.add_argument("--prompt", default=os.path.join(HERE, "PROMPT.md"))
    args = ap.parse_args()

    sha = corpus_sha()
    if sha != EXPECTED_SHA:
        print(f"FATAL: corpus sha mismatch\n  got      {sha}\n"
              f"  expected {EXPECTED_SHA}", file=sys.stderr)
        return 4
    os.makedirs(args.outdir, exist_ok=True)
    prompt_tmpl = open(args.prompt, encoding="utf-8").read()
    all_cases = [json.loads(l) for l in
                 open(os.path.join(PHASE1, "cases.ndjson"), encoding="utf-8")
                 if l.strip()]
    ids = [c["id"] for c in all_cases]
    chunks = [ids[i:i + args.chunk_size]
              for i in range(0, len(ids), args.chunk_size)]

    print(f"arm={args.tag} model={args.model_id} cases={len(ids)} "
          f"chunks={len(chunks)} attempts<={args.attempts}")

    collected, log = {}, []
    for n, chunk in enumerate(chunks):
        rows, clog = run_chunk(args.model_id, args.tag, n, chunk,
                               args.outdir, args.attempts, prompt_tmpl)
        log.extend(clog)
        if rows:
            collected.update({r["case_id"]: r for r in rows})
        got = len(collected)
        print(f"  chunk {n:02d} [{len(rows) if rows else 0}/{len(chunk)}] "
              f"cumulative={got}/{len(ids)}", flush=True)

    if corpus_sha() != EXPECTED_SHA:
        print("FATAL: corpus changed during the run", file=sys.stderr)
        return 4

    answers_path = os.path.join(args.outdir, f"answers-{args.tag}.ndjson")
    with open(answers_path, "w", encoding="utf-8") as fh:
        for cid in ids:
            if cid in collected:
                fh.write(json.dumps(collected[cid], ensure_ascii=False) + "\n")
    log_path = os.path.join(args.outdir, f"runlog-{args.tag}.json")
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump({"arm": args.tag, "model_id": args.model_id,
                   "corpus_sha256": sha, "n_cases": len(ids),
                   "n_chunks": len(chunks), "chunk_size": args.chunk_size,
                   "attempts_allowed": args.attempts,
                   "n_collected": len(collected),
                   "missing_case_ids": sorted(set(ids) - set(collected)),
                   "attempts": log}, fh, indent=1)
    print(f"arm={args.tag} collected={len(collected)}/{len(ids)} "
          f"-> {answers_path}")
    return 0 if len(collected) == len(ids) else 5


if __name__ == "__main__":
    raise SystemExit(main())
