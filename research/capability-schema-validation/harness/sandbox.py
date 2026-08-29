"""Sandbox — preselected surface gate.

Checks op_id ∈ allowed set before any runtime validation.
Only exact stable ID matches are dispatched; no fuzzy matching (Test D4).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMAS = HERE.parent / "capabilities" / "authoritative" / "schemas.json"


class Sandbox:
    """Preselected capability surface gate.

    The sandbox is the first boundary: it enforces that only the small
    preselected capability set is invokable, regardless of what exists
    in the authoritative registry. The authoritative registry may contain
    additional capabilities not in the sandbox — those must be rejected
    here (Test D1).
    """

    def __init__(self, allowed_op_ids: Optional[Set[str]] = None, schemas_path: Optional[Path] = None):
        if allowed_op_ids is not None:
            self.allowed: Set[str] = set(allowed_op_ids)
        else:
            # Default: all ops from authoritative schemas are allowed.
            # Tests that need a restricted surface pass an explicit subset.
            path = schemas_path or DEFAULT_SCHEMAS
            data = json.loads(path.read_text())
            self.allowed = {c["op_id"] for c in data["capabilities"]}

    def check(self, op_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Return (allowed, error_dict). Exact match only."""
        if op_id in self.allowed:
            return True, None
        # UnknownOperation at sandbox boundary
        return False, {
            "code": "UnknownOperation",
            "op_id": op_id,
            "hint": "op_id not in preselected sandbox surface; no fuzzy matching",
            "boundary": "sandbox",
        }

    def allowed_list(self) -> List[str]:
        return sorted(self.allowed)
