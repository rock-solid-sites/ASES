#!/usr/bin/env python3
"""Experimental offline ASES policy publisher. Does not change active instructions."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from string import Template

RULE_ID = re.compile(r"^[a-z][a-z0-9_.-]*$")


class PolicyError(ValueError):
    pass


def _unique_object(pairs):
    """Duplicate JSON fields make policy identity and overrides ambiguous."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError("duplicate JSON object field: " + key)
        result[key] = value
    return result


def _parse_json(data):
    return json.loads(data, object_pairs_hook=_unique_object)


def _load(path):
    return _parse_json(Path(path).read_text(encoding="utf-8"))


def _rule_id(rule):
    value = rule.get("id")
    if not isinstance(value, str) or RULE_ID.fullmatch(value) is None:
        raise PolicyError("invalid rule id")
    return value


def _rule_map(source):
    rules = source.get("rules")
    if not isinstance(rules, list):
        raise PolicyError("source rules must be a list")
    found = {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise PolicyError("invalid source rule")
        rid = _rule_id(rule)
        if rid in found:
            raise PolicyError("duplicate source rule: " + rid)
        if not isinstance(rule.get("text"), str) or not rule["text"].strip():
            raise PolicyError("empty source rule: " + rid)
        found[rid] = rule["text"]
    return found


def _parameterize(text, params):
    if not isinstance(params, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in params.items()
    ):
        raise PolicyError("parameters must map strings to strings")
    required = set()
    for match in Template.pattern.finditer(text):
        if match.group("invalid") is not None:
            raise PolicyError("invalid template placeholder")
        name = match.group("named") or match.group("braced")
        if name is not None:
            required.add(name)
    if set(params) != required:
        raise PolicyError("parameter keys differ from placeholders")
    try:
        return Template(text).substitute(params)
    except (KeyError, ValueError) as e:
        raise PolicyError("unresolved template placeholder") from e


def render(source_bytes, source, consumer):
    if source.get("schema") != "ases-policy-source-v1":
        raise PolicyError("invalid source schema")
    if consumer.get("schema") != "ases-policy-consumer-v1":
        raise PolicyError("invalid consumer schema")
    wanted = consumer.get("source_sha256")
    actual = hashlib.sha256(source_bytes).hexdigest()
    if not isinstance(wanted, str) or wanted != actual:
        raise PolicyError("upstream source revision differs from pinned hash")
    rules = _rule_map(source)
    imports = consumer.get("imports")
    extensions = consumer.get("extensions", [])
    if not isinstance(imports, list) or not isinstance(extensions, list):
        raise PolicyError("imports and extensions must be lists")
    selected, effective = set(), []
    for item in imports:
        if not isinstance(item, dict):
            raise PolicyError("invalid import")
        rid = _rule_id(item)
        if rid in selected:
            raise PolicyError("duplicate imported rule: " + rid)
        if rid not in rules:
            raise PolicyError("unknown upstream rule: " + rid)
        selected.add(rid)
        mode = item.get("mode")
        upstream = rules[rid]
        if mode == "verbatim":
            if set(item) != {"id", "mode"}:
                raise PolicyError("unexpected verbatim fields")
            text = upstream
        elif mode == "parameterized":
            if set(item) != {"id", "mode", "params"}:
                raise PolicyError("unexpected parameterized fields")
            text = _parameterize(upstream, item["params"])
        elif mode == "override":
            if set(item) != {"id", "mode", "text"}:
                raise PolicyError("unexpected override fields")
            text = item["text"]
        else:
            raise PolicyError("unsupported import mode")
        if not isinstance(text, str) or not text.strip():
            raise PolicyError("empty effective rule: " + rid)
        effective.append((rid, text))
    for item in extensions:
        if not isinstance(item, dict):
            raise PolicyError("invalid extension")
        rid = _rule_id(item)
        if rid in selected:
            raise PolicyError("local rule collides with imported rule: " + rid)
        if rid in rules:
            raise PolicyError("local extension must not shadow upstream rule: " + rid)
        selected.add(rid)
        if set(item) != {"id", "text"} or not isinstance(item["text"], str) or not item["text"].strip():
            raise PolicyError("invalid local extension")
        effective.append((rid, item["text"]))
    blocks = ["# Generated effective agent instructions", "",
              "<!-- experimental; sha256-of-approved-upstream: " + actual + " -->", ""]
    for rid, text in effective:
        blocks.extend(("## " + rid, "", text, ""))
    return "\n".join(blocks).rstrip() + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--update", action="store_true")
    args = p.parse_args()
    try:
        source_bytes = args.source.read_bytes()
        rendered = render(source_bytes, _parse_json(source_bytes),
                          _load(args.manifest))
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
                raise PolicyError("effective output is stale or missing")
            print("POLICY_OK")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print("POLICY_UPDATED")
    except (PolicyError, OSError, json.JSONDecodeError) as e:
        p.exit(1, "POLICY_ERROR: " + str(e) + "\n")


if __name__ == "__main__":
    main()
