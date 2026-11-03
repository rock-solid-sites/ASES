#!/usr/bin/env python3
"""Validate ASES compute credit registry; no network access or account actions."""
import json
import sys
from pathlib import Path

def validate(data):
    errors = []
    if data.get("schema_version") != "1.1.0":
        errors.append("unexpected schema version")
    providers = data.get("providers", [])
    promotions = data.get("promotions", [])
    offerings = data.get("compute_offerings", [])
    def unique(items, group):
        ids = [x.get("id") for x in items]
        if any(not isinstance(i, str) or not i for i in ids):
            errors.append(f"{group}: missing IDs")
        if len(ids) != len(set(ids)):
            errors.append(f"{group}: duplicate IDs")
        return set(ids)
    provider_ids = unique(providers, "providers")
    unique(promotions, "promotions")
    unique(offerings, "compute_offerings")
    for group, entries in (("promotions", promotions), ("compute_offerings", offerings)):
        for x in entries:
            if x.get("provider_id") not in provider_ids:
                errors.append(f"{group}/{x.get('id')}: missing provider")
    for x in promotions:
        if x.get("advertised_value") is not None and x["advertised_value"] < 0:
            errors.append(f"promotions/{x['id']}: negative advertised value")
        if x.get("evidence_level") is None:
            errors.append(f"promotions/{x['id']}: missing evidence")
        if x.get("status") == "verified" and not x.get("source_urls"):
            errors.append(f"promotions/{x['id']}: verified without source")
    for x in offerings:
        if x.get("ram_gb", 0) < 4:
            errors.append(f"compute_offerings/{x['id']}: below minimum RAM")
        if x.get("hourly_usd") is not None and x["hourly_usd"] < 0:
            errors.append(f"compute_offerings/{x['id']}: negative hourly cost")
    for x in data.get("account_inventory", {}).get("entries", []):
        if x.get("provider_id") not in provider_ids:
            errors.append("account_inventory: unknown provider")
    return errors

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("registry.json")
    errors = validate(json.loads(path.read_text(encoding="utf-8")))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Registry valid")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
