#!/usr/bin/env python3
"""Placeholder latency aggregator — reads logs/*.jsonl and prints p50/p95. Filled after live run."""
import json, pathlib, statistics
LOG_DIR = pathlib.Path(__file__).resolve().parent / "logs"
logs = list(LOG_DIR.glob("*.jsonl"))
if not logs:
    print("no logs yet — this is measurement scaffolding (placeholders). After live run, JSONL logs will be under measurements/logs/")
else:
    import math
    lat=[]
    for f in logs:
        for line in f.read_text().splitlines():
            if not line.strip(): continue
            j=json.loads(line)
            if "latency_ms" in j and j["latency_ms"] is not None:
                lat.append(j["latency_ms"])
    if lat:
        lat.sort()
        def p95(arr): return arr[int(0.95*len(arr))] if arr else None
        print(f"n={len(lat)} p50={statistics.median(lat)} p95={p95(lat)} mean={statistics.mean(lat):.1f}")
    else:
        print("logs present but no latency_ms fields")
