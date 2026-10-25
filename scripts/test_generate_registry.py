import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fixtures  # noqa: E402
import generate_registry as g  # noqa: E402
import validate  # noqa: E402

TODAY = "2026-10-25"


def _body(ident, name, year):
    b = copy.deepcopy(fixtures.make_fixture()[0]["entries"][0])
    b["id"] = ident
    b["names"] = [dict(b["names"][1], name_la=name, name_en=None, aliases=None,
                       **{"from": f"{year}-01-01", "to": None})]
    b["aliases"] = []
    b["founded"]["date"] = f"{year}-01-01"
    return b


def _merger_fixture():
    bodies, events = fixtures.make_fixture()
    bodies["entries"][0]["aliases"] = ["Sanctum Officium"]
    a, b = _body("cr:alpha-1600", "Alpha", 1600), _body("cr:beta-1610", "Beta", 1610)
    c = _body("cr:gamma-1700", "Gamma", 1700)
    bodies["entries"] += [a, b, c]
    events["entries"].append({
        "id": "ev900", "date": "1700-01-01", "event_type": "merger",
        "before": ["cr:alpha-1600", "cr:beta-1610"], "after": ["cr:gamma-1700"]})
    return bodies, events


class GeneratorTests(unittest.TestCase):
    def test_identifiers_cc0_and_complete(self):
        bodies, events = _merger_fixture()
        doc = g.identifiers(bodies, events)
        self.assertEqual(doc["license"], "CC0-1.0")
        self.assertEqual([e["id"] for e in doc["entries"]],
                         sorted(b["id"] for b in bodies["entries"]))
        e = {x["id"]: x for x in doc["entries"]}["cr:doctrina-fidei-1542"]
        self.assertEqual(e["aliases"], [
            "Sancta Romana et Universalis Inquisitio", "Holy Office",
            "Sacra Congregatio Sancti Officii", "Sanctum Officium"])
        self.assertIsNone(e["founding_act_mag"])

    def test_lineage_derived_from_events(self):
        bodies, events = _merger_fixture()
        e = {x["id"]: x for x in g.identifiers(bodies, events)["entries"]}
        self.assertEqual(e["cr:alpha-1600"]["successors"], ["cr:gamma-1700"])
        self.assertEqual(e["cr:beta-1610"]["successors"], ["cr:gamma-1700"])
        self.assertEqual(e["cr:gamma-1700"]["predecessors"],
                         ["cr:alpha-1600", "cr:beta-1610"])
        self.assertEqual(e["cr:doctrina-fidei-1542"]["predecessors"], [])
        self.assertEqual(e["cr:doctrina-fidei-1542"]["successors"], [])

    def test_unverified_marked(self):
        bodies, events = fixtures.make_fixture()
        bodies["entries"][0]["names"][1]["verified"] = False
        out = g.render_bodies(bodies, events, validate.load_vocab(), today=TODAY)
        self.assertIn("Sacra Congregatio Sancti Officii †", out)
        self.assertIn("unverified", out.lower())

    def test_gap_facts_marked_and_listed(self):
        bodies, events = fixtures.make_fixture()
        b = bodies["entries"][0]
        b["names"][1]["gap"] = "rename date not located"
        b["founded"]["gap"] = "act not read"
        out = g.render_bodies(bodies, events, validate.load_vocab(), today=TODAY)
        head, gaps = out.split("## Known gaps")
        self.assertIn(f"Sacra Congregatio Sancti Officii {g.GAP_MARK}", head)
        self.assertIn(f"1542-07-21 {g.GAP_MARK}", head)
        legend = head.split("## Living bodies")[0]
        self.assertIn(g.GAP_MARK, legend)
        self.assertIn("rename date not located", gaps)
        self.assertIn("act not read", gaps)

    def test_warnings_listed(self):
        bodies, events = fixtures.make_fixture()
        events["entries"][1]["clause_status"] = "not-transcribed"
        rep = validate.validate(bodies, events, validate.load_vocab())
        self.assertTrue(rep.warnings)
        out = g.render_bodies(bodies, events, validate.load_vocab(), today=TODAY)
        gaps = out.split("## Known gaps")[1]
        for w in rep.warnings:
            self.assertIn(w, gaps)

    def test_refuses_on_errors(self):
        bodies, events = fixtures.make_fixture()
        bodies["entries"][0]["id"] = "bad id"
        with tempfile.TemporaryDirectory() as d:
            err = io.StringIO()
            with mock.patch.object(g, "OUT_DIR", d), \
                    mock.patch.object(g, "load_data", return_value=(bodies, events)), \
                    redirect_stderr(err):
                rc = g.main()
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.getvalue().lower())
            self.assertEqual(os.listdir(d), [])

    def test_lineages_trace_back(self):
        bodies, events = _merger_fixture()
        out = g.render_lineages(bodies, events)
        self.assertIn("cr:gamma-1700", out)
        self.assertIn("ev900", out)
        self.assertIn("cr:alpha-1600", out.split("cr:gamma-1700", 1)[1])


if __name__ == "__main__":
    unittest.main()
