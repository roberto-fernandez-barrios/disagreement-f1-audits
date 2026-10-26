"""Interface boundary tests complement, rather than repeat, the exact core tests."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.audit_pair import audit


class LabelLimitedAudit(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((Path(__file__).resolve().parents[1] /
                                   "examples/ten_items.json").read_text())

    def test_paper_example_and_no_hidden_labels(self):
        before = copy.deepcopy(self.payload)
        r = audit(self.payload)
        self.assertEqual([x["exact"] for x in r["paired_interval"]], ["-2/35", "1/5"])
        self.assertEqual(r["observed_labels"], 3)
        self.assertEqual(r["action"], "query_agreements")
        self.assertIsNone(r["chosen_model"])
        self.assertEqual(self.payload, before)

    def test_tolerance_does_not_require_equivalence(self):
        r = audit(self.payload, "0.06")
        self.assertEqual(r["chosen_model"], "q")
        self.assertEqual(r["minimum_worst_case_regret"]["exact"], "2/35")
        self.assertGreater(r["paired_interval"][1]["decimal"], 0.06)

    def test_revealed_agreements_update_the_feasible_set(self):
        self.payload["labels"][3:6] = [1, 1, 1]
        r = audit(self.payload, "0")
        self.assertEqual(r["chosen_model"], "c")
        self.assertEqual(r["observed_labels"], 6)
        self.assertEqual([x["exact"] for x in r["paired_interval"]], ["-2/35", "-2/35"])

    def test_zero_prevalence_and_deterministic_tie(self):
        r = audit({"q": [0], "c": [0], "labels": [None], "prevalence": 0}, "0")
        self.assertTrue(r["strict_winner_or_exact_tie_identified"])
        self.assertEqual(r["chosen_model"], "q")
        r = audit({"q": [1], "c": [1], "labels": [None], "prevalence": 1}, "0")
        self.assertEqual(r["paired_interval"][0]["exact"], "0")

    def test_missing_disagreement_is_rejected(self):
        self.payload["labels"][0] = None
        with self.assertRaisesRegex(ValueError, "every disagreement"):
            audit(self.payload)

    def test_incompatible_prevalence_is_rejected(self):
        self.payload["prevalence"] = 0
        with self.assertRaisesRegex(ValueError, "No admissible"):
            audit(self.payload)

    def test_malformed_inputs(self):
        for name, value in [("q", [2]*10), ("labels", [False]*10),
                            ("prevalence", 0.4), ("prevalence", True), ("c", [])]:
            with self.subTest(name=name, value=value):
                p = copy.deepcopy(self.payload); p[name] = value
                with self.assertRaises(ValueError): audit(p)
        for eps in ["nan", "inf", "-0.01", "1/0"]:
            with self.subTest(epsilon=eps):
                with self.assertRaises(ValueError): audit(self.payload, eps)


if __name__ == "__main__":
    unittest.main()
