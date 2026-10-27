import unittest

import fixtures
import validate

VOCAB = validate.load_vocab()
ID = "cr:doctrina-fidei-1542"


def run(mutate=None):
    b, e = fixtures.make_fixture()
    if mutate:
        mutate(b["entries"][0], b["entries"][0], e["entries"], b)
    return validate.validate(b, e, VOCAB)


def counts(r):
    return len(r.errors), len(r.warnings)


class ValidateTests(unittest.TestCase):
    def test_valid_fixture_clean(self):
        r = run()
        self.assertEqual((r.errors, r.warnings), ([], []))

    def test_id_year_mismatch(self):
        def m(body, _b, ev, doc):
            body["id"] = "cr:doctrina-fidei-1543"
            for x in ev:
                x["before"] = [body["id"] for _ in x["before"]]
                x["after"] = [body["id"] for _ in x["after"]]
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertTrue(r.errors[0].startswith("[R1] cr:doctrina-fidei-1543:"))

    def test_duplicate_id(self):
        def m(body, _b, ev, doc):
            import copy
            doc["entries"].append(copy.deepcopy(body))
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)

    def test_overlapping_names(self):
        def m(body, *_):
            body["names"][1]["from"] = "1900-01-01"
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)

        def g(body, *_):
            m(body)
            body["names"][1]["gap"] = "undated rename"
        r = run(g)
        self.assertEqual(counts(r), (0, 1), (r.errors, r.warnings))

    def test_name_outside_lifespan(self):
        def m(body, *_):
            body["names"][0]["from"] = "1500-01-01"
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)

    def test_names_gap_and_end(self):
        def m(body, *_):
            body["names"][0]["to"] = "1900-01-01"
        self.assertEqual(counts(run(m)), (1, 0))

        def n(body, *_):
            body["names"][1]["to"] = "2000-01-01"
        self.assertEqual(counts(run(n)), (1, 0))  # ended is null

    def test_section_not_in_regime(self):
        def m(body, *_):
            body["section"] = [{"regime": "immensa-1588", "section": "pontifical-council",
                                "from": "1700-01-01", "to": "1800-01-01",
                                "verified": True, "source_type": "primary", "source": "t"}]
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertIn("[R3]", r.errors[0])

    def test_section_regime_mismatch_and_overrun(self):
        def m(body, *_):
            body["section"][0]["regime"] = "immensa-1588"
        self.assertEqual(counts(run(m)), (1, 0))

        def n(body, *_):
            body["section"] = [dict(body["section"][1], to="1950-01-01")]
        self.assertEqual(counts(run(n)), (1, 0))

    def test_not_listed_requires_in_curia(self):
        def m(body, *_):
            del body["section"][0]["in_curia"]
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)

        def n(body, *_):
            body["section"][0]["in_curia"] = None
        self.assertEqual(counts(run(n)), (1, 0))

        def g(body, *_):
            n(body)
            body["section"][0]["gap"] = "unknown"
        self.assertEqual(counts(run(g)), (0, 1))

    def test_missing_in_curia_with_gap_still_error(self):
        def m(body, *_):
            del body["section"][0]["in_curia"]
            body["section"][0]["gap"] = "unknown"
        r = run(m)
        # the error stands; the gap is still surfaced once, by R0
        self.assertEqual(counts(r), (1, 1))
        self.assertTrue(r.warnings[0].startswith("[R0]"), r.warnings)

    def test_r0_every_gap_reported(self):
        def m(body, _b, ev, doc):
            body["names"][0]["gap"] = "rename date not located"
            body["kind"][0]["gap"] = "kind basis unread"
            body["founded"]["gap"] = "act not read"
            body["section"][1]["gap"] = "placement inferred"
            ev[1]["gap"] = "clause not found"
            body["gap"] = "identity open"
        r = run(m)
        self.assertEqual(r.errors, [])
        r0 = [w for w in r.warnings if w.startswith("[R0]")]
        self.assertEqual(len(r0), 6, r.warnings)
        for text in ("rename date not located", "kind basis unread", "act not read",
                     "placement inferred", "clause not found", "identity open"):
            self.assertTrue(any(text in w for w in r0), text)
        self.assertTrue(any(w.startswith(f"[R0] {ID}: names[0]") for w in r0), r0)
        self.assertTrue(any(w.startswith("[R0] ev002") for w in r0), r0)

    def test_r0_no_duplicate_when_rule_already_warns(self):
        def m(body, *_):
            body["names"][1]["from"] = "1900-01-01"
            body["names"][1]["gap"] = "undated rename"
        r = run(m)
        self.assertEqual(counts(r), (0, 1), r.warnings)
        self.assertTrue(r.warnings[0].startswith("[R2]"))

        def n(body, *_):
            body["names"][1]["from"] = "1900-01-01"
            body["names"][0]["gap"] = "end not located"
        r = run(n)
        self.assertEqual(counts(r), (0, 1), r.warnings)

        def o(body, *_):
            body["section"][0]["in_curia"] = None
            body["section"][0]["gap"] = "unknown"
        r = run(o)
        self.assertEqual(counts(r), (0, 1), r.warnings)
        self.assertTrue(r.warnings[0].startswith("[R3]"))

    def test_attested_null_but_created_by_event(self):
        def m(body, *_):
            body["founded"]["event"] = None
            body["founded"]["basis"] = "attested"
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertIn("[R4] ev001", r.errors[0])

    def test_rename_before_equals_after(self):
        def m(body, _b, ev, doc):
            ev[1]["after"] = []
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)

    def test_merger_creates_new_body(self):
        def m(body, _b, ev, doc):
            ev[0]["event_type"] = "merger"
            ev[0]["clause_status"] = "transcribed"
            ev[0]["operative_clause"] = "x"
            body["founded"]["event"] = "ev002"
            ev[1]["event_type"] = "foundation"
            ev[1]["before"] = []
            ev[1]["date"] = "1542-07-21"
        # founded.event ev002 is a foundation w/ matching date, but merger ev001 lists body in after
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertIn("[R4] ev001", r.errors[0])

    def test_absorption_keeps_absorber(self):
        import copy

        def base(body, ev, doc):
            other = copy.deepcopy(body)
            other["id"] = "cr:alia-congregatio-1542"
            other["founded"]["event"] = "ev003"
            other["names"] = [dict(n) for n in body["names"]]
            other["names"][0]["to"] = "1908-11-03"
            other["names"][1]["to"] = "1950-01-01"
            other["names"][1]["from"] = "1908-11-03"
            other["kind"][0]["to"] = "1950-01-01"
            other["section"] = []
            other["ended"] = {"date": "1950-01-01", "precision": "day", "basis": "act",
                              "act": "x", "event": "ev004", "verified": True,
                              "source_type": "primary", "source": "t"}
            doc["entries"].append(other)
            ev.append({"id": "ev003", "date": "1542-07-21", "date_precision": "day",
                       "signed": None, "act": "x", "mag": None, "event_type": "foundation",
                       "before": [], "after": [other["id"]], "operative_clause": None,
                       "clause_status": "transcribed", "inferred": False,
                       "verified": True, "source_type": "primary", "source": "t", "note": None})
            ev.append({"id": "ev004", "date": "1950-01-01", "date_precision": "day",
                       "signed": None, "act": "x", "mag": None, "event_type": "absorption",
                       "before": [body["id"], other["id"]], "after": [body["id"]],
                       "operative_clause": "x", "clause_status": "transcribed",
                       "inferred": False, "verified": True, "source_type": "primary",
                       "source": "t", "note": None})
            return other

        b, e = fixtures.make_fixture()
        base(b["entries"][0], e["entries"], b)
        r = validate.validate(b, e, VOCAB)
        self.assertEqual((r.errors, r.warnings), ([], []))

        b, e = fixtures.make_fixture()
        base(b["entries"][0], e["entries"], b)
        e["entries"][-1]["after"] = []
        r = validate.validate(b, e, VOCAB)
        self.assertEqual(counts(r), (1, 0), r.errors)

        b, e = fixtures.make_fixture()
        other = base(b["entries"][0], e["entries"], b)
        other["ended"] = None
        other["names"][1]["to"] = None
        other["kind"][0]["to"] = None
        r = validate.validate(b, e, VOCAB)
        self.assertEqual(counts(r), (1, 0), r.errors)

    def test_unknown_body_in_event(self):
        def m(body, _b, ev, doc):
            ev[1]["before"] = ev[1]["before"] + ["cr:nulla-1500"]
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertIn("cr:nulla-1500", r.errors[0])

    def test_founded_event_resolves(self):
        def missing(body, *_):
            body["founded"]["event"] = "ev999"
        self.assertEqual(counts(run(missing)), (1, 0))

        def wrong_type(body, *_):
            body["founded"]["event"] = "ev002"
        r = run(wrong_type)
        self.assertEqual(len([x for x in r.errors if x.startswith("[R5]")]), 1)

        def wrong_date(body, _b, ev, doc):
            ev[0]["date"] = "1542-07-22"
        self.assertEqual(counts(run(wrong_date)), (1, 0))

        def attested(body, _b, ev, doc):
            body["founded"]["event"] = None
            body["founded"]["basis"] = "attested"
            ev[0]["after"] = []
            ev[0]["event_type"] = "foundation"
        # event ev001 now has empty after; only the attested exemption is under test
        r = run(attested)
        self.assertEqual([x for x in r.errors if x.startswith("[R5]")], [])

    def test_clause_status(self):
        def a(body, _b, ev, doc):
            ev[1]["operative_clause"] = None
        self.assertEqual(counts(run(a)), (1, 0))

        def b_(body, _b, ev, doc):
            ev[1]["clause_status"] = "silent"
            ev[1]["operative_clause"] = None
        self.assertEqual(counts(run(b_)), (1, 0))

        def c(body, _b, ev, doc):
            ev[1]["clause_status"] = "not-transcribed"
        self.assertEqual(counts(run(c)), (0, 1))

        def d(body, _b, ev, doc):
            del ev[1]["clause_status"]
        self.assertEqual(counts(run(d)), (1, 0))

    def test_r8_dated_fact_without_source(self):
        def m(body, _b, ev, doc):
            body["names"][0]["source"] = None
            del body["kind"][0]["source"]
            ev[1]["source"] = ""
        r = run(m)
        self.assertEqual(r.errors, [])
        self.assertEqual(sorted(r.warnings), [
            f"[R8] {ID}: kind[0]: dated fact has no source",
            f"[R8] {ID}: names[0]: dated fact has no source",
            "[R8] ev002: dated fact has no source"])

    def test_bad_vocab_value(self):
        def m(body, *_):
            body["kind"][0]["kind"] = "bureau"
        r = run(m)
        self.assertEqual(counts(r), (1, 0), r.errors)
        self.assertIn("[R6]", r.errors[0])


if __name__ == "__main__":
    unittest.main()
