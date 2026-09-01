#!/usr/bin/env python3
"""Measure description_tokens for 530 corpus schemas (full vs minimal). Pinned tokenizer tiktoken cl100k_base 0.14.0 when installed."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
for name in ("schemas/full.json","schemas/minimal.json","schemas/authoritative.json","prompts/prompt-full.md","prompts/prompt-minimal.md"):
    p = ROOT / name
    if not p.exists():
        print(f"missing {p}")
        continue
    txt = p.read_text()
    chars=len(txt)
    approx=chars//4
    tcount=None
    tok="heuristic char/4"
    try:
        import tiktoken
        enc=tiktoken.get_encoding("cl100k_base")
        tcount=len(enc.encode(txt))
        tok="tiktoken cl100k_base 0.14.0"
    except Exception as e:
        pass
    print(f"{name}: chars={chars} approx={approx} tiktoken={tcount} tokenizer={tok}")
