import json
import os
import unittest

from crcdr import ID_RE, ROOT, at, load, parse_date

EXCLUDED = {"sixtine-temporal-congregations", "fabric-st-peter"}
RELATIONS = {"within", "subject-to", "section-of", "complement-of"}
SOURCE_TYPES = {"primary", "official-secondary", "secondary", "inferred"}


def _load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _research_bodies():
    return {b["key"]: b for b in _load("seed", "research", "bodies.json")["bodies"]}


def _research_events():
    return {e["id"]: e for e in _load("seed", "research", "events.json")["events"]}


def _founding_years():
    return {e["research_key"]: e for e in _load("seed", "founding_years.json")["entries"]}


def _held_out():
    return {k for k, e in _founding_years().items() if e["status"] == "held-out"}


def _intervals(items):
    """by_body items as intervals: each runs to the next item's `from`."""
    dated = [it for it in items if it["from"] is not None]
    return [dict(it, to=(dated[n + 1]["from"] if n + 1 < len(dated) else None))
            for n, it in enumerate(dated)]


def _key_map():
    return {e["research_key"]: e for e in _load("seed", "key_map.json")["entries"]}


class SeedMaps(unittest.TestCase):
    def test_key_map_complete_and_valid(self):
        bodies = _research_bodies()
        fy = _founding_years()
        entries = _load("seed", "key_map.json")["entries"]
        keys = [e["research_key"] for e in entries]
        self.assertEqual(len(keys), len(set(keys)), "duplicate research_key")
        expected = set(bodies) - EXCLUDED - _held_out()
        self.assertEqual(set(keys), expected)
        ids = [e["id"] for e in entries]
        self.assertEqual(len(ids), len(set(ids)), "duplicate id")
        for e in entries:
            k = e["research_key"]
            self.assertRegex(e["id"], ID_RE, k)
            b = bodies[k]
            erected = (b.get("erected") or {}).get("date")
            try:
                founded = parse_date(erected)
            except ValueError:
                self.assertEqual(fy[k]["status"], "dated", k)
                founded = parse_date(fy[k]["date"])
            if "founded_date" in e:
                # erected.date is the signing date; the research's own first
                # name entry carries the effective date (design §4 rule 4).
                eff = parse_date(e["founded_date"])
                self.assertGreater(eff, founded, k)
                self.assertEqual(e["founded_date"], b["names"][0]["from"], k)
                founded = eff
            self.assertEqual(int(e["id"][-4:]), founded.year, k)
            # minted from the name in use when minting: the last name entry
            last = b["names"][-1]["name_la"]
            self.assertIn(e["minted_from_la"], last, k)
            self.assertTrue(e["rule_note"].strip(), k)
        for want in ("cr:doctrina-fidei-1542", "cr:cultus-divinus-1969",
                     "cr:cultus-divinus-1984"):
            self.assertIn(want, ids)

    def test_kind_map_covers_research(self):
        kinds = {k["id"] for k in load("kinds")["entries"]}
        km = _load("seed", "kind_map.json")
        for v in km["by_string"].values():
            self.assertIn(v, kinds)
        for key, items in km["by_body"].items():
            for it in items:
                self.assertIn(it["kind"], kinds, key)
        for k, b in _research_bodies().items():
            override = km["by_body"].get(k)
            for entry in b["kind"]:
                if override is None:
                    self.assertIn(entry["kind"], km["by_string"], f"{k}: {entry['kind']}")
                    continue
                if entry["from"] is None:
                    match = [it for it in override if it["from"] is None]
                    self.assertEqual(len(match), 1, k)
                else:
                    match = at(_intervals(override), entry["from"])
                    self.assertIsNotNone(match, f"{k}: {entry['from']}")
            if override is not None:
                self.assertEqual(override[0]["from"], b["kind"][0]["from"], k)

    def test_event_map_covers_nonvocab_types(self):
        vocab = {t["id"] for t in load("event_types")["entries"]}
        research = _research_events()
        bodies = set(_research_bodies())
        em = _load("seed", "event_map.json")["events"]
        for i, ev in research.items():
            if ev["event_type"] not in vocab:
                self.assertIn(i, em, i)
        for i, items in em.items():
            self.assertIn(i, research, i)
            self.assertIsInstance(items, list, i)
            for it in items:
                self.assertIn(it["event_type"], vocab, i)
                self.assertIsInstance(it["inferred"], bool, i)
                self.assertTrue(it["note"].strip(), i)
                for x in it["before"] + it["after"]:
                    self.assertIn(x, bodies, i)
        self.assertEqual([it["event_type"] for it in em["ev026"]], ["rename"])
        self.assertTrue(em["ev026"][0]["inferred"])
        self.assertEqual(em["ev120"], [])
        self.assertGreaterEqual(len({it["event_type"] for it in em["ev022"]}), 2)

    def test_clauses_verbatim(self):
        research = _research_events()
        corpus = json.dumps(_load("seed", "research", "events.json"), ensure_ascii=False)
        corpus += json.dumps(_load("seed", "research", "bodies.json"), ensure_ascii=False)
        with open(os.path.join(ROOT, "docs", "curia-history-report.md"), encoding="utf-8") as f:
            corpus += f.read()
        for i, clause in _load("seed", "clauses.json").items():
            self.assertIn(i, research, i)
            self.assertTrue(clause.strip(), i)
            self.assertTrue(clause in corpus, f"{i}: clause not quoted verbatim in the research")

    def test_part_of_targets_exist(self):
        km = _key_map()
        for p in _load("seed", "part_of.json")["entries"]:
            self.assertIn(p["body"], km)
            self.assertIn(p["target"], km)
            self.assertNotEqual(p["body"], p["target"])
            self.assertIn(p["relation"], RELATIONS)
            self.assertIn(p["source_type"], SOURCE_TYPES)
            self.assertIsInstance(p["verified"], bool)
            self.assertTrue(p["source"].strip())
            parse_date(p["from"])
            if p["to"] is not None:
                self.assertLess(parse_date(p["from"]), parse_date(p["to"]))

    def test_section_overrides_valid(self):
        km = _key_map()
        regimes = {r["id"]: r for r in load("sections")["regimes"]}
        seen = set()
        for o in _load("seed", "section_overrides.json")["entries"]:
            self.assertIn(o["body"], km)
            self.assertIn(o["regime"], regimes)
            sections = {s["id"]: s for s in regimes[o["regime"]]["sections"]}
            self.assertIn(o["section"], sections, o["body"])
            self.assertNotIn((o["body"], o["regime"]), seen, o["body"])
            seen.add((o["body"], o["regime"]))
            self.assertIn(o["in_curia"], (True, False, None), o["body"])
            if o["section"] != "not-listed":
                self.assertEqual(o["in_curia"], sections[o["section"]]["in_curia"], o["body"])
            self.assertIn(o["source_type"], SOURCE_TYPES)
            self.assertIsInstance(o["verified"], bool)
            self.assertTrue(o["source"].strip())
            self.assertTrue(o["note"].strip())


if __name__ == "__main__":
    unittest.main()
