"""Prevent dependency and installer trust from regressing after CA distrust."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CaTrustTests(unittest.TestCase):
    def test_local_installer_enforces_remediated_trust(self):
        self.assertIn('required-version = ">=0.13.4"', (ROOT / "pyproject.toml").read_text())

    def test_workflows_use_remediated_uv(self):
        workflows = list((ROOT / ".github" / "workflows").glob("*.yaml"))
        self.assertTrue(workflows)
        for workflow in workflows:
            text = workflow.read_text()
            if "astral-sh/setup-uv@" in text:
                self.assertNotIn('version: "0.6.9"', text, workflow.name)
                self.assertIn('version: "0.13.4"', text, workflow.name)


if __name__ == "__main__":
    unittest.main()
