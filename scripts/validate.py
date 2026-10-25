"""CRCDR validator: design section 7, rules 1-7, plus R0 (every documented gap) and
R8 (dated fact without a source). Errors vs documented-gap warnings."""
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
    gap_paths: set = field(default_factory=set)

    def add(self, rule, ident, msg, gap=False, path=None):
        """Record a finding. `gap` true makes it a warning; `path` names the fact
        whose `gap` note made it one, so R0 does not report that gap twice."""
        text = f"[R{rule}] {ident}: {msg}"
        (self.warnings if gap else self.errors).append(text)
        if gap and path is not None:
            self.gap_paths.add((ident, path))


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
    ok = []
    for n, e in enumerate(items):
        try:
            ok.append((_d(e["from"]), _end(e.get("to")), e, f"{lst}[{n}]"))
        except (KeyError, TypeError, ValueError):
            rep.add(2, i, f"{lst}[{n}] has a missing or invalid date", _gap(e), f"{lst}[{n}]")
    alive = b.get("ended") is None

    def add(msg, *cands):
        """Warn (with the gap-carrying fact's path) if any candidate has a gap."""
        hit = next(((e, p) for e, p in cands if _gap(e)), None)
        rep.add(2, i, msg, hit is not None, hit[1] if hit else None)

    for f, t, e, label in ok:
        if f < lo:
            add(f"{label} starts before founding", (e, label))
        if t > hi and not (alive and t == FAR_FUTURE):
            add(f"{label} extends past end", (e, label))
        if t <= f:
            add(f"{label} is empty or reversed", (e, label))
    for n in range(1, len(ok)):
        pf, pt, pe, plabel = ok[n - 1]
        f, t, e, label = ok[n]
        if f < pf:
            add(f"{label} out of order", (e, label))
        elif f < pt:
            add(f"{label} overlaps {plabel}", (e, label), (pe, plabel))
        elif lst == "names" and f > pt:
            add(f"names do not cover lifespan between {plabel} and {label}",
                (e, label), (pe, plabel))
    if lst == "names":
        if not ok:
            rep.add(2, i, "names is empty")
            return
        f, _t, e, label = ok[0]
        if f > lo:
            add(f"{label} starts after founding", (e, label))
        f, t, e, label = ok[-1]
        if t < hi:
            add("last name ends before the end of the lifespan", (e, label))


# --- R3 ---------------------------------------------------------------

def _r3(bodies, vocab, rep):
    sec = vocab["sections"]
    regimes = {r["id"]: r for r in sec["regimes"]}
    for b in bodies.get("entries", []):
        i = b.get("id")
        for n, e in enumerate(b.get("section") or []):
            label = f"section[{n}]"
            g = _gap(e)
            add = lambda rule, msg, gap: rep.add(rule, i, msg, gap, label)  # noqa: E731
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
                add(3, f"{label} regime {e['regime']} but {want} is in force on {frm}", g)
                continue
            if e.get("section") not in {s["id"] for s in regimes[want]["sections"]}:
                add(3, f"{label} section {e.get('section')!r} not in regime {want}", g)
            if nxt and to > min(nxt):
                add(3, f"{label} extends past the next regime's effective date", g)
            if e.get("section") == "not-listed":
                if "in_curia" not in e:
                    rep.add(3, i, f"{label} not-listed entry lacks in_curia")
                elif e["in_curia"] is None:
                    msg = f"{label} in_curia is null" + ("" if g else " without a gap note")
                    add(3, msg, g)
                elif not isinstance(e["in_curia"], bool):
                    add(3, f"{label} in_curia must be true/false", g)


# --- R4 ---------------------------------------------------------------

def _r4(bodies, events, vocab, rep):
    idx = _index(bodies)
    effects = {t["id"]: t["effect"] for t in vocab["event_types"]["entries"]}
    seen = set()
    known = {e.get("id") for e in events.get("entries", [])}
    _links_to = lambda fact, eid, created=False: _links(fact, eid, known, created)  # noqa: E731
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
                if _links_to(idx[x].get("founded"), i, created=True) is False:
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


def _links(fact, event_id, known, created=False):
    """True/False if fact names an event; None when R5 owns the problem."""
    if not fact:
        return False if fact is None else None
    ev = fact.get("event")
    if ev is None:
        # attested-null is exempt only when no event claims to create the body
        return None if fact.get("basis") == "attested" and not created else False
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
                rep.add(5, i, "founded.event " + "; ".join(problems), _gap(f), "founded")
        e = b.get("ended")
        if e:
            problems = _event_problems(evs, effects, e, i, None, False)
            if problems:
                rep.add(5, i, "ended.event " + "; ".join(problems), _gap(e), "ended")


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
        for n, k in enumerate(b.get("kind") or []):
            if k.get("kind") not in kinds:
                rep.add(6, i, f"unknown kind {k.get('kind')!r}", _gap(k), f"kind[{n}]")
        for n, s in enumerate(b.get("section") or []):
            if s.get("regime") not in regimes:
                rep.add(6, i, f"unknown regime {s.get('regime')!r}", _gap(s), f"section[{n}]")
        for n, p in enumerate(b.get("part_of") or []):
            path = f"part_of[{n}]"
            if p.get("relation") not in RELATIONS:
                rep.add(6, i, f"unknown part_of relation {p.get('relation')!r}", _gap(p), path)
            if p.get("body") not in ids:
                rep.add(6, i, f"part_of references unknown body {p.get('body')!r}", _gap(p), path)
        for path, fct in _facts(b):
            if path and "source_type" in fct and fct["source_type"] not in SOURCE_TYPES:
                rep.add(6, i, f"unknown source_type {fct['source_type']!r}", _gap(fct), path)
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


# --- R0 / R8 -------------------------------------------------------------

def _facts(b):
    """(path, fact) for a body itself (path "") and each of its dated facts."""
    out = [("", b)]
    for k in ("founded", "ended"):
        if b.get(k):
            out.append((k, b[k]))
    for lst in ("names", "kind", "section", "part_of"):
        out.extend((f"{lst}[{n}]", e) for n, e in enumerate(b.get(lst) or []) if e)
    return out


def _r0(bodies, events, rep):
    """Every fact with a `gap` note is a warning, quoting the gap, unless another
    rule already reported that fact's gap as a warning."""
    found = [(b.get("id"), path, f) for b in bodies.get("entries", []) for path, f in _facts(b)]
    found += [(ev.get("id"), "", ev) for ev in events.get("entries", [])]
    for ident, path, f in found:
        if _gap(f) and (ident, path) not in rep.gap_paths:
            where = f"{path}: " if path else ""
            rep.add(0, ident, f"{where}documented gap: {f['gap']}", True, path)


def _r8(bodies, events, rep):
    """A dated fact with no source is a warning (no source is ever invented)."""
    found = [(b.get("id"), path, f) for b in bodies.get("entries", []) for path, f in _facts(b)
             if path]
    found += [(ev.get("id"), "", ev) for ev in events.get("entries", [])]
    for ident, path, f in found:
        dated = f.get("date") is not None or f.get("from") is not None
        if dated and not f.get("source"):
            where = f"{path}: " if path else ""
            rep.add(8, ident, f"{where}dated fact has no source", True)


def validate(bodies, events, vocab):
    rep = Report()
    _r1(bodies, rep)
    _r2(bodies, rep)
    _r3(bodies, vocab, rep)
    _r4(bodies, events, vocab, rep)
    _r5(bodies, events, vocab, rep)
    _r6(bodies, events, vocab, rep)
    _r7(events, rep)
    _r8(bodies, events, rep)
    _r0(bodies, events, rep)
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
