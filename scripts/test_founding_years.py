import json
import os
import unittest

from crcdr import ROOT, parse_date


def _load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _undated_keys():
    keys = []
    for b in _load("seed", "research", "bodies.json")["bodies"]:
        d = (b.get("erected") or {}).get("date")
        try:
            parse_date(d)
        except ValueError:
            keys.append(b["key"])
    return keys


class FoundingYears(unittest.TestCase):
    def test_all_thirteen_resolved(self):
        undated = _undated_keys()
        self.assertEqual(len(undated), 13)
        entries = _load("seed", "founding_years.json")["entries"]
        got = [e["research_key"] for e in entries]
        for k in undated:
            self.assertEqual(got.count(k), 1, k)
        self.assertEqual(sorted(got), sorted(undated))
        for e in entries:
            k = e["research_key"]
            self.assertIn(e["status"], ("dated", "held-out"), k)
            self.assertIn(e["source_type"], ("primary", "secondary"), k)
            self.assertIsInstance(e["verified"], bool, k)
            if e["status"] == "dated":
                parse_date(e["date"])
                self.assertIn(e["precision"], ("year", "month", "day"), k)
                self.assertTrue(e["source"].strip(), k)
                self.assertTrue(e["act_or_attestation"].strip(), k)
                self.assertIn(e["basis"], ("attested", "act"), k)
                if e["basis"] == "act":
                    self.assertTrue(e["verified"], k)
            else:
                self.assertIsNone(e["date"], k)
                self.assertTrue(e["note"].strip(), k)


if __name__ == "__main__":
    unittest.main()
