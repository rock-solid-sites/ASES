#!/usr/bin/env python3
"""Focused RED/GREEN structural checks for validate-investigation-note.py.

Run: python scripts/test_validate_investigation_note.py
Requires PyYAML. Deliberately uses only stdlib unittest beyond that dependency.
"""
import importlib.util
from pathlib import Path
import unittest

script = Path(__file__).with_name("validate-investigation-note.py")
spec = importlib.util.spec_from_file_location("investigation_note_validator", script)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

STATE = """```yaml
kind: state
original_goal: Restore service
acceptance: Verify user-facing behavior
```"""
PLANNED = """```yaml
kind: experiment
id: E1
question: Is the dependency reachable?
prediction: A healthy upstream responds
decision_value: Distinguishes upstream failure
status: planned
```"""
COMPLETED = """```yaml
kind: experiment
id: E1
question: Is the dependency reachable?
prediction: A healthy upstream responds
decision_value: Distinguishes upstream failure
status: completed
outcome: success
observation: HTTP 200
implication: Upstream reachable
next_action: Examine local authorization
```"""
INTERRUPTED = """```yaml
kind: experiment
id: E1
question: Is the dependency reachable?
prediction: A healthy upstream responds
decision_value: Distinguishes upstream failure
status: interrupted
observation: Test runner exited early
```"""


class ValidatorTests(unittest.TestCase):
    def test_valid_state_only(self):
        self.assertEqual(validator.validate(STATE), [])

    def test_valid_planned(self):
        self.assertEqual(validator.validate(STATE + "\n" + PLANNED), [])

    def test_valid_completed(self):
        self.assertEqual(validator.validate(STATE + "\n" + COMPLETED), [])

    def test_valid_interrupted(self):
        self.assertEqual(validator.validate(STATE + "\n" + INTERRUPTED), [])

    def test_missing_goal(self):
        errors = validator.validate(STATE.replace("original_goal:", "omitted_goal:"))
        self.assertIn("original_goal", ";".join(errors))

    def test_duplicate_id(self):
        errors = validator.validate(STATE + "\n" + PLANNED + "\n" + PLANNED)
        self.assertIn("duplicate experiment id", errors)

    def test_invalid_status(self):
        errors = validator.validate(STATE + "\n" + PLANNED.replace("status: planned", "status: unknown"))
        self.assertIn(".status:", ";".join(errors))

    def test_invalid_yaml(self):
        errors = validator.validate(STATE + "\n" + PLANNED.replace("id: E1", "id: [unclosed"))
        self.assertIn("YAML block", ";".join(errors))

    def test_wrong_status_type_reports_error_not_exception(self):
        errors = validator.validate(STATE + "\n" + PLANNED.replace("status: planned", "status: [planned]"))
        self.assertIn(".status:", ";".join(errors))

    def test_wrong_outcome_type_reports_error_not_exception(self):
        errors = validator.validate(STATE + "\n" + COMPLETED.replace("outcome: success", "outcome: [success]"))
        self.assertIn(".outcome:", ";".join(errors))


if __name__ == "__main__":
    unittest.main()
