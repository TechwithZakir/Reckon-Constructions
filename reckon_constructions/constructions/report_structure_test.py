import json
import re
import unittest
from pathlib import Path


REPORT_ROOT = Path(__file__).parent / "report"


def _scrub(value):
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


class ReportStructureTest(unittest.TestCase):
    def test_standard_report_paths_match_frappe_module_names(self):
        report_files = sorted(REPORT_ROOT.glob("*/*.json"))
        self.assertGreaterEqual(len(report_files), 8)
        for report_file in report_files:
            definition = json.loads(report_file.read_text(encoding="utf-8"))
            slug = _scrub(definition["name"])
            self.assertEqual(report_file.parent.name, slug)
            self.assertTrue((report_file.parent / f"{slug}.py").exists())
            self.assertEqual(definition["report_type"], "Script Report")


if __name__ == "__main__":
    unittest.main()
