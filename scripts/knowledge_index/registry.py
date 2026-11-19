"""Stable, explicitly registered source identities for the research prototype.

A registry change is reviewed source metadata. No opportunistic rename inference,
automatic registry mutation, or cross-repository lookup is allowed.
"""
import json
from pathlib import Path

class RegistryError(ValueError):
    pass

def read_registry(root):
    path = Path(root) / "scripts/knowledge_index/identities.json"
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("version") != 1 or not isinstance(doc.get("entries"), list):
        raise RegistryError("invalid registry version/entries")
    by_path, identities = {}, set()
    for entry in doc["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise RegistryError("invalid registry identity")
        if entry["id"] in identities:
            raise RegistryError(f"duplicate stable identity: {entry['id']}")
        identities.add(entry["id"])
        aliases = entry.get("aliases", [])
        if not isinstance(aliases, list):
            raise RegistryError(f"aliases must be a list: {entry['id']}")
        candidates = [entry.get("path")] + aliases
        if not candidates or any(not isinstance(x, str) or not x or
           Path(x).is_absolute() or ".." in Path(x).parts or "\\" in x for x in candidates):
            raise RegistryError(f"invalid path for identity {entry['id']}")
        for alias in candidates:
            if alias in by_path:
                raise RegistryError(f"duplicate registered path/alias: {alias}")
            by_path[alias] = {"id": entry["id"], "path": entry["path"],
                              "aliases": list(aliases)}
    return by_path
