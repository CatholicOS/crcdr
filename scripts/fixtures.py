"""Minimal valid fixture shared by the validator tests (and Task 7's tests)."""
import copy

_PROV = {"verified": True, "source_type": "primary", "source": "test"}


_CHAIN = [
    ("immensa-1588", "congregation", "1588-01-22", "1908-11-03"),
    ("sapienti-consilio-1908", "congregation", "1908-11-03", "1918-05-19"),
    ("cic-1917", "congregation", "1918-05-19", "1968-01-01"),
    ("reu-1968", "congregation", "1968-01-01", "1989-03-01"),
    ("pastor-bonus-1989", "congregation", "1989-03-01", "2022-06-05"),
    ("praedicate-evangelium-2022", "dicastery", "2022-06-05", None),
]


def _fixture():
    bodies = {"entries": [{
        "id": "cr:doctrina-fidei-1542",
        "founded": {"date": "1542-07-21", "precision": "day", "basis": "act",
                    "act": "Licet ab initio", "event": "ev001", **_PROV},
        "ended": None,
        "names": [
            {"name_la": "Sancta Romana et Universalis Inquisitio", "name_it": None,
             "name_en": "Holy Office", "from": "1542-07-21", "to": "1908-11-03",
             "act": "Licet ab initio", **_PROV},
            {"name_la": "Sacra Congregatio Sancti Officii", "name_it": None,
             "name_en": "Holy Office", "from": "1908-11-03", "to": None,
             "act": "Sapienti consilio", **_PROV},
        ],
        "kind": [{"kind": "congregation", "from": "1542-07-21", "to": None, **_PROV}],
        "section": [
            {"regime": "pre-1588", "section": "not-listed", "in_curia": True,
             "from": "1542-07-21", "to": "1588-01-22", **_PROV},
            *[{"regime": r, "section": sec, "from": f, "to": t, **_PROV}
              for r, sec, f, t in _CHAIN],
        ],
        "part_of": [],
        "aliases": [],
        "note": None,
    }]}
    events = {"entries": [
        {"id": "ev001", "date": "1542-07-21", "date_precision": "day", "signed": None,
         "act": "Licet ab initio", "mag": None, "event_type": "foundation",
         "before": [], "after": ["cr:doctrina-fidei-1542"],
         "operative_clause": None, "clause_status": "transcribed", "inferred": False,
         **_PROV, "note": None},
        {"id": "ev002", "date": "1908-11-03", "date_precision": "day", "signed": None,
         "act": "Sapienti consilio", "mag": None, "event_type": "rename",
         "before": ["cr:doctrina-fidei-1542"], "after": ["cr:doctrina-fidei-1542"],
         "operative_clause": "Sancta Romana et Universalis Inquisitio ... ",
         "clause_status": "transcribed", "inferred": False, **_PROV, "note": None},
    ]}
    return bodies, events


def make_fixture():
    """A fresh (bodies_doc, events_doc) deep copy of the minimal valid fixture."""
    return copy.deepcopy(_fixture())
