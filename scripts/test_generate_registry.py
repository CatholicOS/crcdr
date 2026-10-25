import copy
import inspect
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import crcdr  # noqa: E402
import fixtures  # noqa: E402
import generate_registry as g  # noqa: E402
import validate  # noqa: E402

TODAY = "2026-10-25"


def ambiguous(doc):
    """(name, id, id) for every name that matches two ids on some date."""
    seen, out = {}, []
    for e in doc["entries"]:
        for n in e["names"] + e["aliases"]:
            lo = crcdr.parse_date(n["from"])
            hi = crcdr.parse_date(n["to"]) if n["to"] else None
            for other, olo, ohi in seen.get(n["name"].casefold(), []):
                if other != e["id"] and (ohi is None or lo < ohi) and (hi is None or olo < hi):
                    out.append((n["name"], other, e["id"]))
            seen.setdefault(n["name"].casefold(), []).append((e["id"], lo, hi))
    return out


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
    bodies["entries"][0]["aliases"] = [{"name": "Sanctum Officium", "lang": "la"}]
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
        self.assertIn("(name, date)", doc["$comment"])
        self.assertEqual([e["id"] for e in doc["entries"]],
                         sorted(b["id"] for b in bodies["entries"]))
        e = {x["id"]: x for x in doc["entries"]}["cr:doctrina-fidei-1542"]
        self.assertEqual(e["names"], [
            {"name": "Sancta Romana et Universalis Inquisitio", "lang": "la",
             "from": "1542-07-21", "to": "1908-11-03"},
            {"name": "Holy Office", "lang": "en", "from": "1542-07-21", "to": None},
            {"name": "Sacra Congregatio Sancti Officii", "lang": "la",
             "from": "1908-11-03", "to": None}])
        self.assertEqual(e["aliases"], [
            {"name": "Sanctum Officium", "lang": "la", "from": "1542-07-21", "to": None}])
        self.assertIsNone(e["founding_act_mag"])

    def test_name_aliases_dated_by_their_name(self):
        bodies, events = fixtures.make_fixture()
        bodies["entries"][0]["names"][0]["aliases"] = [{"name": "Suprema", "lang": "la"}]
        e = g.identifiers(bodies, events)["entries"][0]
        self.assertEqual(e["aliases"], [
            {"name": "Suprema", "lang": "la", "from": "1542-07-21", "to": "1908-11-03"}])

    def test_name_date_lookup_unambiguous(self):
        bodies, events = crcdr.load("bodies"), crcdr.load("events")
        self.assertEqual(ambiguous(g.identifiers(bodies, events)), [])
        with open(g.IDS_PATH, encoding="utf-8") as f:
            self.assertEqual(ambiguous(json.load(f)), [])
        # the check itself catches an overlap
        bodies, events = _merger_fixture()
        for x in bodies["entries"]:
            if x["id"] == "cr:beta-1610":
                x["names"][0]["name_la"] = "Alpha"
        self.assertEqual(len(ambiguous(g.identifiers(bodies, events))), 1)

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
                    mock.patch.object(g, "IDS_PATH", os.path.join(d, "identifiers.json")), \
                    mock.patch.object(g, "load_data", return_value=(bodies, events)), \
                    redirect_stderr(err):
                rc = g.main([])
            self.assertNotEqual(rc, 0)
            self.assertIn("error", err.getvalue().lower())
            self.assertEqual(os.listdir(d), [])

    def _run_main(self, argv):
        bodies, events = fixtures.make_fixture()
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(g, "OUT_DIR", d), \
                    mock.patch.object(g, "IDS_PATH", os.path.join(d, "identifiers.json")), \
                    mock.patch.object(g, "load_data", return_value=(bodies, events)), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = g.main(argv)
            out = {}
            for n in sorted(os.listdir(d)):
                with open(os.path.join(d, n), encoding="utf-8") as f:
                    out[n] = f.read()
            return rc, out

    def test_as_of_defaults_to_latest_data_date(self):
        bodies, events = fixtures.make_fixture()
        vocab = validate.load_vocab()
        latest = g.latest_date(bodies, events, vocab["sections"], vocab["kinds"],
                               vocab["event_types"])
        self.assertEqual(latest, "2022-06-05")
        self.assertEqual(g.latest_date({"a": ["1900", {"b": "1950-03"}, "note 1999"]}),
                         "1950-03")
        rc, out = self._run_main([])
        self.assertEqual(rc, 0)
        self.assertIn("Current as of 2022-06-05.", out["bodies.md"])
        self.assertEqual(self._run_main([])[1], out)  # deterministic
        self.assertNotIn("today()", inspect.getsource(g))

    def test_as_of_option(self):
        rc, out = self._run_main(["--as-of", "1950-01-01"])
        self.assertEqual(rc, 0)
        self.assertIn("Current as of 1950-01-01.", out["bodies.md"])
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                g.main(["--as-of", "1950/01/01"])

    def test_lineage_rows_marked(self):
        bodies, events = _merger_fixture()
        ev = events["entries"][-1]
        ev.update(inferred=True, verified=False, act="Actum")
        out = g.render_lineages(bodies, events, TODAY)
        legend = out.split("\n## ")[0]
        for m in (g.MARK, g.INF_MARK, g.GAP_MARK):
            self.assertIn(m, legend)
        row = next(x for x in out.splitlines() if "ev900" in x)
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[0], f"1700-01-01 {g.MARK}")
        self.assertEqual(cells[1], f"ev900 {g.INF_MARK}")
        self.assertEqual(cells[3], f"Actum {g.MARK}")
        self.assertTrue(cells[4].endswith(g.MARK) and cells[5].endswith(g.MARK), cells)
        # a verified, non-inferred event carries no marker
        plain = next(x for x in out.splitlines() if "| ev002 |" in x or "ev001" in x)
        self.assertNotIn(g.MARK, plain)
        self.assertNotIn(g.INF_MARK, plain)

    def test_founded_cell_marks_inferred_event(self):
        bodies, events = fixtures.make_fixture()
        events["entries"][0]["inferred"] = True
        out = g.render_bodies(bodies, events, validate.load_vocab(), today=TODAY)
        self.assertIn(f"1542-07-21 {g.INF_MARK} (Licet ab initio)", out)
        self.assertIn(g.INF_MARK, out.split("## Living bodies")[0])

    def test_lineages_trace_back(self):
        bodies, events = _merger_fixture()
        out = g.render_lineages(bodies, events, TODAY)
        self.assertIn("cr:gamma-1700", out)
        self.assertIn("ev900", out)
        self.assertIn("cr:alpha-1600", out.split("cr:gamma-1700", 1)[1])


if __name__ == "__main__":
    unittest.main()
