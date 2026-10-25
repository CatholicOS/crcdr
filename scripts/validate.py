"""CRCDR validator: design section 7, rules 1-7. Errors vs documented-gap warnings."""
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import crcdr  # noqa: E402

SOURCE_TYPES = {"primary", "official-secondary", "secondary", "inferred"}
RELATIONS = {"within", "subject-to", "section-of", "complement-of"}
CLAUSE_STATUSES = {"transcribed", "not-transcribed", "silent"}
FAR_FUTURE = crcdr.parse_date("9999-12-31")


@dataclass
class Report:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def add(self, rule, ident, msg, gap=False):
        text = f"[R{rule}] {ident}: {msg}"
        (self.warnings if gap else self.errors).append(text)


def load_vocab():
    return {"kinds": crcdr.load("kinds"), "sections": crcdr.load("sections"),
            "event_types": crcdr.load("event_types")}


def _gap(entry):
    return bool(entry.get("gap"))


def _d(s):
    return crcdr.parse_date(s)


def _end(s):
    return FAR_FUTURE if s is None else _d(s)


def _index(bodies):
    return {b.get("id"): b for b in bodies.get("entries", [])}


# --- R1 ---------------------------------------------------------------

def _r1(bodies, rep):
    seen = set()
    for b in bodies.get("entries", []):
        i = b.get("id")
        if i in seen:
            rep.add(1, i, "duplicate id")
        seen.add(i)
        if not isinstance(i, str) or not crcdr.ID_RE.match(i):
            rep.add(1, i, "id does not match the grammar")
            continue
        try:
            year = _d(b["founded"]["date"]).year
        except (KeyError, TypeError, ValueError):
            rep.add(1, i, "founded.date missing or invalid")
            continue
        if int(i[-4:]) != year:
            rep.add(1, i, f"id year {i[-4:]} differs from founded year {year}")


# --- R2 ---------------------------------------------------------------

def _r2(bodies, rep):
    for b in bodies.get("entries", []):
        i = b.get("id")
        try:
            lo = _d(b["founded"]["date"])
            ended = b.get("ended")
            hi = _end(ended["date"] if ended else None)
        except (KeyError, TypeError, ValueError):
            continue  # reported by R1
        for lst in ("names", "kind", "section", "part_of"):
            _check_list(rep, i, b, lst, lo, hi)


def _check_list(rep, i, b, lst, lo, hi):
    items = b.get(lst) or []
    parsed = []
    for n, e in enumerate(items):
        try:
            parsed.append((_d(e["from"]), _end(e.get("to")), e))
        except (KeyError, TypeError, ValueError):
            rep.add(2, i, f"{lst}[{n}] has a missing or invalid date", _gap(e))
            parsed.append(None)
    ok = [p for p in parsed if p]
    alive = b.get("ended") is None
    for n, (f, t, e) in enumerate(ok):
        label = f"{lst}[{n}]"
        if f < lo:
            rep.add(2, i, f"{label} starts before founding", _gap(e))
        if t > hi and not (alive and t == FAR_FUTURE):
            rep.add(2, i, f"{label} extends past end", _gap(e))
        if t <= f:
            rep.add(2, i, f"{label} is empty or reversed", _gap(e))
    for n in range(1, len(ok)):
        pf, pt, pe = ok[n - 1]
        f, t, e = ok[n]
        label = f"{lst}[{n}]"
        if f < pf:
            rep.add(2, i, f"{label} out of order", _gap(e))
        elif f < pt:
            rep.add(2, i, f"{label} overlaps {lst}[{n - 1}]", _gap(e) or _gap(pe))
        elif lst == "names" and f > pt:
            rep.add(2, i, f"names do not cover lifespan between [{n - 1}] and [{n}]",
                    _gap(e) or _gap(pe))
    if lst == "names":
        if not ok:
            rep.add(2, i, "names is empty")
            return
        f, _t, e = ok[0]
        if f > lo:
            rep.add(2, i, "names[0] starts after founding", _gap(e))
        f, t, e = ok[-1]
        if t < hi:
            rep.add(2, i, "last name ends before the end of the lifespan", _gap(e))


# --- R3 ---------------------------------------------------------------

def _r3(bodies, vocab, rep):
    sec = vocab["sections"]
    regimes = {r["id"]: r for r in sec["regimes"]}
    for b in bodies.get("entries", []):
        i = b.get("id")
        for n, e in enumerate(b.get("section") or []):
            label = f"section[{n}]"
            g = _gap(e)
            try:
                frm = e["from"]
                want = crcdr.regime_at(sec, frm)
                nxt = [_d(r["effective"]) for r in sec["regimes"]
                       if r["effective"] and _d(r["effective"]) > _d(frm)]
                to = _end(e.get("to"))
            except (KeyError, TypeError, ValueError):
                continue  # reported by R2
            if e.get("regime") not in regimes:
                continue  # reported by R6
            if e["regime"] != want:
                rep.add(3, i, f"{label} regime {e['regime']} but {want} is in force on {frm}", g)
                continue
            if e.get("section") not in {s["id"] for s in regimes[want]["sections"]}:
                rep.add(3, i, f"{label} section {e.get('section')!r} not in regime {want}", g)
            if nxt and to > min(nxt):
                rep.add(3, i, f"{label} extends past the next regime's effective date", g)
            if e.get("section") == "not-listed":
                if "in_curia" not in e:
                    rep.add(3, i, f"{label} not-listed entry lacks in_curia", g)
                elif e["in_curia"] is None:
                    rep.add(3, i, f"{label} in_curia is null", g) if g else \
                        rep.add(3, i, f"{label} in_curia is null without a gap note")
                elif not isinstance(e["in_curia"], bool):
                    rep.add(3, i, f"{label} in_curia must be true/false", g)


# --- R4 ---------------------------------------------------------------

def _r4(bodies, events, vocab, rep):
    idx = _index(bodies)
    effects = {t["id"]: t["effect"] for t in vocab["event_types"]["entries"]}
    seen = set()
    known = {e.get("id") for e in events.get("entries", [])}
    _links_to = lambda fact, eid: _links(fact, eid, known)  # noqa: E731
    for ev in events.get("entries", []):
        i = ev.get("id")
        if i in seen:
            rep.add(4, i, "duplicate event id")
        seen.add(i)
        before, after = ev.get("before") or [], ev.get("after") or []
        unknown = [x for x in list(before) + list(after) if x not in idx]
        for x in dict.fromkeys(unknown):
            rep.add(4, i, f"references unknown body {x}")
        if unknown:
            continue
        eff = effects.get(ev.get("event_type"))
        sb, sa = set(before), set(after)
        if eff == "same":
            if not sb or sb != sa:
                rep.add(4, i, f"{ev['event_type']} needs identical, non-empty before and after")
        elif eff == "new":
            for x in sorted(sa - sb):
                if _links_to(idx[x].get("founded"), i) is False:
                    rep.add(4, i, f"{x} is created but its founded.event is not {i}")
            if ev["event_type"] in ("merger", "split"):
                for x in sorted(sb - sa):
                    if _links_to(idx[x].get("ended"), i) is False:
                        rep.add(4, i, f"{x} is merged/split away but its ended.event is not {i}")
        elif eff == "absorb":
            both = sb & sa
            if len(both) != 1:
                rep.add(4, i, "absorption needs exactly one body in both before and after")
                continue
            for x in sorted(sb - sa):
                ended = idx[x].get("ended")
                if ended is None:
                    rep.add(4, i, f"absorbed body {x} has no ended")
                elif _links_to(ended, i) is False:
                    rep.add(4, i, f"absorbed body {x} has ended.event other than {i}")
        elif eff == "end":
            if sa:
                rep.add(4, i, "suppression must have empty after")
            for x in sorted(sb):
                if _links_to(idx[x].get("ended"), i) is False:
                    rep.add(4, i, f"{x} is suppressed but its ended.event is not {i}")


def _links(fact, event_id, known):
    """True/False if fact names an event; None when R5 owns the problem."""
    if not fact:
        return False if fact is None else None
    ev = fact.get("event")
    if ev is None:
        return None if fact.get("basis") == "attested" else False
    if ev not in known:
        return None
    return ev == event_id


# --- R5 ---------------------------------------------------------------

def _r5(bodies, events, vocab, rep):
    evs = {e.get("id"): e for e in events.get("entries", [])}
    effects = {t["id"]: t["effect"] for t in vocab["event_types"]["entries"]}
    for b in bodies.get("entries", []):
        i = b.get("id")
        f = b.get("founded") or {}
        if f.get("event") is None and f.get("basis") == "attested":
            pass
        else:
            problems = _event_problems(evs, effects, f, i, "new", True)
            if problems:
                rep.add(5, i, "founded.event " + "; ".join(problems), _gap(f))
        e = b.get("ended")
        if e:
            problems = _event_problems(evs, effects, e, i, None, False)
            if problems:
                rep.add(5, i, "ended.event " + "; ".join(problems), _gap(e))


def _event_problems(evs, effects, fact, body, need_effect, in_after):
    name = fact.get("event")
    ev = evs.get(name)
    if ev is None:
        return [f"{name!r} does not resolve to an event"]
    out = []
    if need_effect and effects.get(ev.get("event_type")) != need_effect:
        out.append(f"{name} is a {ev.get('event_type')}, not a creating event")
    b, a = ev.get("before") or [], ev.get("after") or []
    if in_after and body not in a:
        out.append(f"{name} does not list the body in after")
    if not in_after and not (body in b and body not in a):
        out.append(f"{name} does not end the body (in before, not in after)")
    try:
        if _d(ev["date"]) != _d(fact["date"]):
            out.append(f"date {fact.get('date')} differs from event date {ev['date']}")
    except (KeyError, TypeError, ValueError):
        out.append("date missing or invalid")
    return out


# --- R6 ---------------------------------------------------------------

def _r6(bodies, events, vocab, rep):
    kinds = {k["id"] for k in vocab["kinds"]["entries"]}
    regimes = {r["id"] for r in vocab["sections"]["regimes"]}
    etypes = {t["id"] for t in vocab["event_types"]["entries"]}
    ids = set(_index(bodies))
    for b in bodies.get("entries", []):
        i = b.get("id")
        for k in b.get("kind") or []:
            if k.get("kind") not in kinds:
                rep.add(6, i, f"unknown kind {k.get('kind')!r}", _gap(k))
        for s in b.get("section") or []:
            if s.get("regime") not in regimes:
                rep.add(6, i, f"unknown regime {s.get('regime')!r}", _gap(s))
        for p in b.get("part_of") or []:
            if p.get("relation") not in RELATIONS:
                rep.add(6, i, f"unknown part_of relation {p.get('relation')!r}", _gap(p))
            if p.get("body") not in ids:
                rep.add(6, i, f"part_of references unknown body {p.get('body')!r}", _gap(p))
        facts = [b.get("founded"), b.get("ended")] + [
            e for lst in ("names", "kind", "section", "part_of") for e in b.get(lst) or []]
        for fct in facts:
            if fct and "source_type" in fct and fct["source_type"] not in SOURCE_TYPES:
                rep.add(6, i, f"unknown source_type {fct['source_type']!r}", _gap(fct))
    for ev in events.get("entries", []):
        i = ev.get("id")
        if ev.get("event_type") not in etypes:
            rep.add(6, i, f"unknown event_type {ev.get('event_type')!r}")
        if ev.get("source_type") not in SOURCE_TYPES:
            rep.add(6, i, f"unknown source_type {ev.get('source_type')!r}")
        if "clause_status" in ev and ev["clause_status"] not in CLAUSE_STATUSES:
            rep.add(6, i, f"unknown clause_status {ev['clause_status']!r}")


# --- R7 ---------------------------------------------------------------

def _r7(events, rep):
    for ev in events.get("entries", []):
        i = ev.get("id")
        if ev.get("event_type") == "foundation":
            continue
        cs = ev.get("clause_status")
        if cs is None:
            rep.add(7, i, "missing clause_status")
        elif cs == "transcribed" and not ev.get("operative_clause"):
            rep.add(7, i, "clause_status transcribed but operative_clause is empty")
        elif cs == "silent" and ev.get("inferred") is not True:
            rep.add(7, i, "clause_status silent requires inferred: true")
        elif cs == "not-transcribed":
            rep.add(7, i, "operative clause not yet transcribed", gap=True)


def validate(bodies, events, vocab):
    rep = Report()
    _r1(bodies, rep)
    _r2(bodies, rep)
    _r3(bodies, vocab, rep)
    _r4(bodies, events, vocab, rep)
    _r5(bodies, events, vocab, rep)
    _r6(bodies, events, vocab, rep)
    _r7(events, rep)
    return rep


def main():
    paths = [os.path.join(crcdr.ROOT, "data", n) for n in ("bodies.json", "events.json")]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print("validate: no data to validate yet; missing: " + ", ".join(missing))
        return 2
    import json
    with open(paths[0], encoding="utf-8") as f:
        bodies = json.load(f)
    with open(paths[1], encoding="utf-8") as f:
        events = json.load(f)
    rep = validate(bodies, events, load_vocab())
    for w in rep.warnings:
        print("WARNING " + w)
    for e in rep.errors:
        print("ERROR " + e)
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
