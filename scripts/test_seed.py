import unittest

import validate
from crcdr import parse_date
from seed_from_research import build, load_inputs

EXCLUDED = {"sixtine-temporal-congregations", "fabric-st-peter"}
SOURCE_RANK = {"inferred": 0, "secondary": 1, "official-secondary": 2, "primary": 3}

_CACHE = {}


def seeded():
    if not _CACHE:
        rb, re_, maps, vocab = load_inputs()
        bodies, events, report = build(rb, re_, maps, vocab)
        _CACHE.update(rb=rb, re=re_, maps=maps, vocab=vocab, bodies=bodies,
                      events=events, report=report)
    return _CACHE


def body(c, ident):
    return next(b for b in c["bodies"]["entries"] if b["id"] == ident)


class TestSeed(unittest.TestCase):
    def test_seed_validates(self):
        c = seeded()
        rep = validate.validate(c["bodies"], c["events"], c["vocab"])
        self.assertEqual(rep.errors, [])

    def test_seeded_dates_are_iso(self):
        c = seeded()
        seen = 0
        for b in c["bodies"]["entries"]:
            facts = [b["founded"], b["ended"]] + [
                e for lst in ("names", "kind", "section", "part_of") for e in b[lst]]
            for f in facts:
                if not f:
                    continue
                for k in ("from", "to", "date"):
                    if k in f and f[k] is not None:
                        parse_date(f[k])
                        seen += 1
            self.assertIsNotNone(b["founded"]["date"], b["id"])
            parse_date(b["founded"]["date"])
        for ev in c["events"]["entries"]:
            parse_date(ev["date"])
            if ev.get("signed") is not None:
                parse_date(ev["signed"])
        self.assertGreater(seen, 200)

    def test_exclusions(self):
        c = seeded()
        km = c["maps"]["key_map"]["entries"]
        kept = {e["research_key"] for e in km}
        held = {e["research_key"] for e in c["maps"]["founding_years"]["entries"]
                if e["status"] == "held-out"}
        dropped = {b["key"] for b in c["rb"]["bodies"]} - kept
        self.assertTrue(EXCLUDED | held | {"state-of-regulars"} <= dropped)
        ids = {b["id"] for b in c["bodies"]["entries"]}
        self.assertEqual(ids, {e["id"] for e in km})
        self.assertEqual(len(ids), len(c["bodies"]["entries"]))
        for ev in c["events"]["entries"]:
            for x in ev["before"] + ev["after"]:
                self.assertIn(x, ids, ev["id"])
            self.assertTrue(ev["before"] or ev["after"], ev["id"])

    def test_reorganization_split(self):
        c = seeded()
        from22 = [e for e in c["events"]["entries"] if e["research_id"] == "ev022"]
        self.assertGreaterEqual(len(from22), 2)
        self.assertGreaterEqual(len({e["event_type"] for e in from22}), 2)
        self.assertTrue(all(e["id"].startswith("ev022") and len(e["id"]) == 6
                            for e in from22))

    def test_sections_cut_at_regime_boundaries(self):
        froms = {s["from"] for s in body(seeded(), "cr:doctrina-fidei-1542")["section"]}
        for d in ("1588-01-22", "1908-11-03", "1918-05-19", "1968-01-01",
                  "1989-03-01", "2022-06-05"):
            self.assertIn(d, froms)

    def test_provenance_never_upgraded(self):
        c = seeded()
        km = {e["id"]: e["research_key"] for e in c["maps"]["key_map"]["entries"]}
        rb = {b["key"]: b for b in c["rb"]["bodies"]}
        for b in c["bodies"]["entries"]:
            research = rb[km[b["id"]]]["names"]
            self.assertEqual(len(b["names"]), len(research), b["id"])
            for got, src in zip(b["names"], research):
                self.assertEqual(got["name_la"], src["name_la"])
                self.assertEqual(got["verified"], src["verified"], b["id"])
                self.assertEqual(got["source_type"], src["source_type"], b["id"])
        rev = {e["id"]: e for e in c["re"]["events"]}
        for ev in c["events"]["entries"]:
            src = rev[ev["research_id"]]
            self.assertLessEqual(SOURCE_RANK[ev["source_type"]],
                                 SOURCE_RANK[src["source_type"]], ev["id"])
            if not src["verified"]:
                self.assertFalse(ev["verified"], ev["id"])

    def test_provenance_never_upgraded_other_facts(self):
        c = seeded()
        km = {e["id"]: e["research_key"] for e in c["maps"]["key_map"]["entries"]}
        rb = {b["key"]: b for b in c["rb"]["bodies"]}
        fy = {e["research_key"]: e for e in c["maps"]["founding_years"]["entries"]}
        ov = {(o["body"], o["regime"]): o for o in c["maps"]["section_overrides"]["entries"]}
        po = c["maps"]["part_of"]["entries"]
        for b in c["bodies"]["entries"]:
            key = km[b["id"]]
            r = rb[key]
            f = b["founded"]
            src = fy[key] if f["basis"] == "attested" else r["erected"]
            self.assertEqual((f["verified"], f["source_type"]),
                             (src["verified"], src["source_type"]), b["id"])
            if b["ended"]:
                self.assertEqual((b["ended"]["verified"], b["ended"]["source_type"]),
                                 (r["ended"]["verified"], r["ended"]["source_type"]), b["id"])
            for s in b["section"]:
                o = ov.get((key, s["regime"]))
                if o and s["source"] == o["source"]:
                    self.assertEqual((s["verified"], s["source_type"]),
                                     (o["verified"], o["source_type"]), b["id"])
                else:
                    self.assertEqual((s["verified"], s["source_type"]), (False, "inferred"))
            mine = [p for p in po if p["body"] == key]
            self.assertEqual(len(mine), len(b["part_of"]))
            for got, p in zip(b["part_of"], mine):
                self.assertEqual((got["verified"], got["source_type"]),
                                 (p["verified"], p["source_type"]), b["id"])
            # kind source_type rule: verified -> primary, never on an extended
            # span, and backed by a verified research entry starting there (or
            # an undated one); unverified -> at most secondary.
            for k in b["kind"]:
                if k["verified"]:
                    self.assertEqual(k["source_type"], "primary", b["id"])
                    self.assertNotIn("gap", k, b["id"])
                    self.assertTrue(any(rk["verified"] and rk["from"] in (k["from"], None)
                                        for rk in r["kind"]), b["id"])
                    if f["basis"] == "attested":
                        self.assertNotEqual(k["from"], f["date"], b["id"])
                else:
                    self.assertLessEqual(SOURCE_RANK[k["source_type"]],
                                         SOURCE_RANK["secondary"], b["id"])

    def test_extended_kind_start_is_unverified(self):
        c = seeded()
        pen = body(c, "cr:paenitentiaria-apostolica-1256")["kind"]
        self.assertEqual((pen[0]["from"], pen[0]["to"], pen[0]["verified"]),
                         ("1256", "1908-11-03", False))
        self.assertEqual(pen[0]["source_type"], "secondary")
        self.assertIn("gap", pen[0])
        self.assertEqual((pen[1]["from"], pen[1]["verified"], pen[1]["source_type"]),
                         ("1908-11-03", True, "primary"))
        vis = body(c, "cr:visitatio-apostolica-urbis-1637")["kind"]
        self.assertEqual(len(vis), 1)
        self.assertFalse(vis[0]["verified"])
        self.assertIn("gap", vis[0])

    def test_name_lookup_bounded(self):
        from crcdr import at
        c = seeded()
        for ident, current in (("cr:episcopi-1588", "Dicasterium pro Episcopis"),
                               ("cr:pontificalis-domus-1968", "Praefectura Pontificalis Domus")):
            b = body(c, ident)
            self.assertEqual(at(b["names"], "2023")["name_la"], current, ident)
            self.assertIsNone(at(b["names"], "1500"), ident)
            before = str(int(b["founded"]["date"][:4]) - 1)
            self.assertIsNone(at(b["names"], before), ident)
        ep = body(c, "cr:episcopi-1588")["names"]
        self.assertEqual(at(ep, "1700")["from"], "1588-01-22")
        self.assertEqual(at(ep, "1950")["name_la"], "Sacra Congregatio Consistorialis")
        self.assertIn("terminus ante quem", ep[1]["gap"].lower())
        self.assertIn("terminus ante quem", ep[0]["gap"].lower())
        pd = body(c, "cr:pontificalis-domus-1968")["names"]
        self.assertEqual(at(pd, "1970")["name_la"], "Apostolici Palatii Praefectura")
        self.assertEqual(at(pd, "1990")["name_la"], "Praefectura Pontificalis Domus")

    def test_no_open_or_undated_inner_names(self):
        for b in seeded()["bodies"]["entries"]:
            names = b["names"]
            for n, e in enumerate(names):
                if n > 0:
                    self.assertIsNotNone(e["from"], b["id"])
                if n + 1 < len(names):
                    self.assertIsNotNone(e["to"], b["id"])

    def test_reshaped_same_effect_keeps_direction(self):
        c = seeded()
        effects = {t["id"]: t["effect"] for t in c["vocab"]["event_types"]["entries"]}
        em = c["maps"]["event_map"]["events"]
        evs = {e["id"]: e for e in c["events"]["entries"]}
        checked = 0
        for src in c["re"]["events"]:
            if src["id"] in em or effects.get(src["event_type"]) != "same":
                continue
            if set(src["bodies_before"]) != set(src["bodies_after"]) and src["id"] in evs:
                self.assertIn("Research direction:", evs[src["id"]]["note"], src["id"])
                checked += 1
        self.assertGreaterEqual(checked, 7)
        self.assertIn("Research direction: cr:doctrina-fidei-1542 -> cr:episcopi-1588.",
                      evs["ev015"]["note"])

    def test_same_day_creation_first(self):
        evs = seeded()["events"]["entries"]
        ids = [e["id"] for e in evs]
        self.assertLess(ids.index("ev057"), ids.index("ev056"))
        dates = [e["date"] for e in evs]
        self.assertEqual(dates, sorted(dates, key=parse_date))

    def test_divine_worship_two_bodies(self):
        c = seeded()
        a = body(c, "cr:cultus-divinus-1969")
        b = body(c, "cr:cultus-divinus-1984")
        self.assertTrue(a["ended"]["date"].startswith("1975"))
        self.assertIsNot(a, b)
        self.assertNotEqual(a["founded"]["date"], b["founded"]["date"])

    def test_effective_date_governs_founding(self):
        c = seeded()
        evs = {e["id"]: e for e in c["events"]["entries"]}
        for ident, eff, signed in (
                ("cr:administratio-patrimonii-sedis-apostolicae-1968", "1968-01-01", "1967-08-15"),
                ("cr:integra-humana-progressio-fovenda-2017", "2017-01-01", "2016-08-17"),
                ("cr:communicatio-2015", "2015-06-29", "2015-06-27")):
            b = body(c, ident)
            self.assertEqual(b["founded"]["date"], eff)
            ev = evs[b["founded"]["event"]]
            self.assertEqual(ev["date"], eff)
            self.assertEqual(ev["signed"], signed)

    def test_attested_bodies_have_no_creating_event(self):
        c = seeded()
        attested = {b["id"] for b in c["bodies"]["entries"]
                    if b["founded"]["basis"] == "attested"}
        self.assertEqual(len(attested), 4)
        new = {t["id"] for t in c["vocab"]["event_types"]["entries"] if t["effect"] == "new"}
        for ev in c["events"]["entries"]:
            if ev["event_type"] in new:
                self.assertFalse(attested & (set(ev["after"]) - set(ev["before"])), ev["id"])
        for i in attested:
            self.assertIsNone(body(c, i)["founded"]["event"])

    def test_absorber_outside_phase1_becomes_suppression(self):
        ev = next(e for e in seeded()["events"]["entries"] if e["research_id"] == "ev071")
        self.assertEqual(ev["event_type"], "suppression")
        self.assertEqual(ev["after"], [])
        self.assertTrue(ev["inferred"])
        self.assertEqual(ev["clause_status"], "silent")

    def test_shapes_normalized(self):
        c = seeded()
        effects = {t["id"]: t["effect"] for t in c["vocab"]["event_types"]["entries"]}
        for ev in c["events"]["entries"]:
            eff = effects[ev["event_type"]]
            if eff == "same":
                self.assertEqual(set(ev["before"]), set(ev["after"]), ev["id"])
            if eff == "absorb":
                self.assertEqual(len(set(ev["before"]) & set(ev["after"])), 1, ev["id"])

    def test_clause_status(self):
        evs = {e["id"]: e for e in seeded()["events"]["entries"]}
        self.assertEqual(evs["ev024c"]["clause_status"], "transcribed")
        self.assertNotEqual(evs["ev024a"]["clause_status"], "transcribed")
        self.assertEqual(evs["ev027"]["clause_status"], "transcribed")
        self.assertTrue(evs["ev027"]["operative_clause"].startswith("S. Congregatio Indicis"))
        self.assertEqual(evs["ev072"]["clause_status"], "silent")
        self.assertTrue(evs["ev072"]["inferred"])
        self.assertEqual(evs["ev001"]["clause_status"], "not-transcribed")
        for e in evs.values():
            self.assertIsNone(e["mag"])


if __name__ == "__main__":
    unittest.main()
