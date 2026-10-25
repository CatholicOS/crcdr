import unittest
from datetime import date

import crcdr
from crcdr import at, fold, in_interval, load, parse_date, regime_at

KINDS = ["congregation", "council", "pontifical-council", "secretariat", "commission",
         "committee", "dicastery", "tribunal", "office", "prefecture", "academy", "institution"]
EVENTS = {"rename": "same", "rename-competence": "same", "kind-change": "same",
          "competence-transfer": "same", "revival": "same", "attachment": "same",
          "foundation": "new", "merger": "new", "split": "new", "re-foundation": "new",
          "absorption": "absorb", "suppression": "end"}
REGIMES = [("pre-1588", None), ("immensa-1588", "1588-01-22"),
           ("sapienti-consilio-1908", "1908-11-03"), ("cic-1917", "1918-05-19"),
           ("reu-1968", "1968-01-01"), ("pastor-bonus-1989", "1989-03-01"),
           ("praedicate-evangelium-2022", "2022-06-05")]


class T(unittest.TestCase):
    def test_parse_date_partial(self):
        self.assertEqual(parse_date("1588"), date(1588, 1, 1))
        self.assertEqual(parse_date("1908-11"), date(1908, 11, 1))
        self.assertEqual(parse_date("1908-11-03"), date(1908, 11, 3))

    def test_parse_date_rejects_prose(self):
        for s in ("medieval", "late 14th c.", "1588-13-01"):
            with self.assertRaises(ValueError):
                parse_date(s)

    def test_patterns_reject_newline_and_non_ascii_digits(self):
        for s in ("1588\n", "1588-01-22\n", "\u0661\u0665\u0688\u0668", "15\u0668\u0668"):
            with self.assertRaises(ValueError, msg=repr(s)):
                parse_date(s)
        self.assertTrue(crcdr.ID_RE.match("cr:index-1571"))
        for s in ("cr:index-1571\n", "cr:index-15\u0667\u0661", "cr:index-\uff11\uff15\uff17\uff11"):
            self.assertIsNone(crcdr.ID_RE.match(s), repr(s))

    def test_in_interval(self):
        self.assertTrue(in_interval("1900", None, "1901"))
        self.assertFalse(in_interval("1901", None, "1901"))
        self.assertTrue(in_interval("2100", "1901", None))

    def test_name_at_rename_day(self):
        names = [{"name_la": "A", "from": "1542-07-21", "to": "1965-12-07"},
                 {"name_la": "B", "from": "1965-12-07", "to": None}]
        self.assertEqual(at(names, "1965-12-06")["name_la"], "A")
        self.assertEqual(at(names, "1965-12-07")["name_la"], "B")
        self.assertIsNone(at(names, "1500"))

    def test_regime_at(self):
        s = load("sections")
        self.assertEqual(regime_at(s, "1600-01-01"), "immensa-1588")
        self.assertEqual(regime_at(s, "1500"), "pre-1588")
        self.assertEqual(regime_at(s, "2022-06-05"), "praedicate-evangelium-2022")
        self.assertEqual(regime_at(s, "2022-06-04"), "pastor-bonus-1989")

    def test_vocabularies(self):
        self.assertEqual([e["id"] for e in load("kinds")["entries"]], KINDS)
        self.assertEqual({e["id"]: e["effect"] for e in load("event_types")["entries"]}, EVENTS)
        rs = load("sections")["regimes"]
        self.assertEqual([(r["id"], r["effective"]) for r in rs], REGIMES)
        for r in rs:
            nl = [s for s in r["sections"] if s["id"] == "not-listed"]
            self.assertEqual(len(nl), 1)
            self.assertIsNone(nl[0]["in_curia"])
            for s in r["sections"]:
                if s["id"] != "not-listed":
                    self.assertIsInstance(s["in_curia"], bool)

    def test_id_re(self):
        self.assertTrue(crcdr.ID_RE.match("cr:doctrina-fidei-1542"))
        for bad in ("cr:doctrina-fidei", "cr:Doctrina-fidei-1542", "cr:cultu-divino-69"):
            self.assertFalse(crcdr.ID_RE.match(bad))

    def test_fold_ligatures(self):
        self.assertEqual(fold("Pœnitentiaria"), "poenitentiaria")
        self.assertEqual(fold("Cæremonialis"), "caeremonialis")
        self.assertEqual(fold("Rotæ Românæ"), "rotae romanae")

    def test_section_kinds(self):
        kinds = {e["id"] for e in load("kinds")["entries"]}
        for r in load("sections")["regimes"]:
            seen = set()
            for s in r["sections"]:
                if s["id"] == "not-listed":
                    continue
                self.assertIsInstance(s["kinds"], list)
                for k in s["kinds"]:
                    self.assertIn(k, kinds)
                    self.assertNotIn(k, seen, r["id"])
                    seen.add(k)


if __name__ == "__main__":
    unittest.main()
