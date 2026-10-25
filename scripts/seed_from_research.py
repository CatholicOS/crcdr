"""Seed data/bodies.json and data/events.json from the research via the curated maps.

Run from the repo root: python3 -I scripts/seed_from_research.py

Inputs: seed/research/{bodies,events}.json and seed/*.json (key_map, kind_map,
event_map, clauses, part_of, section_overrides, founding_years).
Outputs: data/bodies.json, data/events.json, seed/seed-report.md.

Integrity rules: no date or fact is invented and no provenance is upgraded.
Where the research has a gap that breaks a validator rule, the fact carries a
`gap` note saying what is missing, so the validator reports a warning.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import crcdr  # noqa: E402
import validate  # noqa: E402

SOURCE_RANK = {"inferred": 0, "secondary": 1, "official-secondary": 2, "primary": 3}
MAP_NAMES = ("key_map", "kind_map", "event_map", "clauses", "part_of",
             "section_overrides", "founding_years")
DERIVED_NOTE = "derived from kind and regime"
LETTERS = "abcdefghijklmnopqrstuvwxyz"


class SeedError(Exception):
    """An inconsistency in the inputs that the seeder must not paper over."""


def _read(*parts):
    with open(os.path.join(crcdr.ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def load_inputs():
    """(research_bodies, research_events, maps, vocab) from the repository."""
    rb = _read("seed", "research", "bodies.json")
    re_ = _read("seed", "research", "events.json")
    maps = {n: _read("seed", n + ".json") for n in MAP_NAMES}
    return rb, re_, maps, validate.load_vocab()


# --- small helpers ------------------------------------------------------

def _d(s):
    return crcdr.parse_date(s)


def _iso(s):
    try:
        _d(s)
        return True
    except ValueError:
        return False


def _precision(s):
    return {4: "year", 7: "month", 10: "day"}[len(s)]


def _join(*parts):
    out = [p.strip() for p in parts if p and p.strip()]
    return " ".join(out) if out else None


def _dedupe(xs):
    return list(dict.fromkeys(xs))


def _lt(a, b):
    """a < b with None meaning +infinity."""
    if a is None:
        return False
    if b is None:
        return True
    return _d(a) < _d(b)


def _later(a, b):
    return b if _lt(a, b) else a


def _earlier(a, b):
    return a if _lt(a, b) else b


class _Ctx:
    def __init__(self, rb, re_, maps, vocab):
        self.rb = rb["bodies"]
        self.re = re_["events"]
        self.maps = maps
        self.vocab = vocab
        self.km = {e["research_key"]: e for e in maps["key_map"]["entries"]}
        self.kept = set(self.km)
        self.fy = {e["research_key"]: e for e in maps["founding_years"]["entries"]
                   if e["status"] == "dated"}
        self.effects = {t["id"]: t["effect"] for t in vocab["event_types"]["entries"]}
        self.report = {k: [] for k in (
            "dropped_bodies", "dropped_events", "normalized", "date_changes",
            "gaps", "map_choices", "clauses", "renames_without_event", "lineage")}

    def cid(self, key):
        return self.km[key]["id"]

    def gap(self, where, text):
        self.report["gaps"].append(f"`{where}`: {text}")
        return text


# --- events ---------------------------------------------------------------

def _clause_targets(ctx):
    """research id -> seeded id that carries its operative clause."""
    clauses = ctx.maps["clauses"]
    notes = clauses.get("_notes", {})
    em = ctx.maps["event_map"]["events"]
    out = {}
    for rid in clauses:
        if rid == "_notes":
            continue
        if rid not in em:
            out[rid] = rid
            continue
        ids = [rid + LETTERS[n] for n in range(len(em[rid]))]
        named = [t for t in re.findall(r"ev\d{3}[a-z]", notes.get(rid, "")) if t in ids]
        out[rid] = named[0] if named else ids[0]
    return out


def _check_provenance(eid, m, src):
    st = m.get("source_type", src["source_type"])
    ver = m.get("verified", src["verified"])
    if SOURCE_RANK[st] > SOURCE_RANK[src["source_type"]] or (ver and not src["verified"]):
        raise SeedError(f"{eid}: event_map would upgrade provenance")
    return st, ver


def _seed_events(ctx):
    em = ctx.maps["event_map"]["events"]
    em_notes = ctx.maps["event_map"].get("notes", {})
    rep = ctx.report
    out = []
    for src in ctx.re:
        rid = src["id"]
        if rid in em and not em[rid]:
            rep["dropped_events"].append(
                f"`{rid}` ({src['event_type']}): event_map gives no structural effect. "
                + em_notes.get(rid, ""))
            continue
        mapped = rid in em
        entries = em[rid] if mapped else [None]
        for n, m in enumerate(entries):
            eid = rid + LETTERS[n] if mapped else rid
            if mapped:
                assert m is not None
                etype, before, after = m["event_type"], list(m["before"]), list(m["after"])
                inferred = bool(m.get("inferred"))
                st, ver = _check_provenance(eid, m, src)
                note = _join(src.get("note"), m.get("note"))
            else:
                etype = src["event_type"]
                before, after = list(src["bodies_before"]), list(src["bodies_after"])
                inferred = False
                st, ver = src["source_type"], src["verified"]
                note = src.get("note")
            if src["source_type"] == "inferred":
                inferred = True
            stripped = [x for x in before + after if x not in ctx.kept]
            b = _dedupe(x for x in before if x in ctx.kept)
            a = _dedupe(x for x in after if x in ctx.kept)
            eff = ctx.effects.get(etype)
            if eff is None:
                raise SeedError(f"{eid}: event type {etype!r} not in the vocabulary")
            if not mapped:
                etype, b, a, inferred, note = _normalize(
                    ctx, eid, etype, eff, before, after, b, a, inferred, note)
            if not b and not a:
                rep["dropped_events"].append(
                    f"`{eid}` ({etype}): every body is outside phase 1 ({', '.join(stripped)}).")
                continue
            if stripped:
                rep["normalized"].append(
                    f"`{eid}`: removed bodies outside phase 1 from before/after: "
                    f"{', '.join(sorted(set(stripped)))}.")
                if etype == "re-foundation" and not b:
                    note = _join(note, "Seeding: the predecessor ("
                                 + ", ".join(sorted(set(stripped)))
                                 + ") is held out of phase 1, so before is empty.")
            out.append({
                "id": eid, "date": src["date"], "date_precision": src["date_precision"],
                "signed": None, "act": src["act"], "mag": None, "event_type": etype,
                "before": [ctx.cid(x) for x in b], "after": [ctx.cid(x) for x in a],
                "operative_clause": None, "clause_status": None, "inferred": inferred,
                "source": src["source"], "source_type": st, "verified": ver,
                "note": note, "research_id": rid,
            })
    _assign_clauses(ctx, out)
    return _order(ctx, out)


def _order(ctx, events):
    """Chronological (stable). Within a day, a creating event moves before the
    first same-day event that involves a body it creates."""
    events = sorted(events, key=lambda e: _d(e["date"]))
    out = []
    for ev in events:
        made = set()
        if ctx.effects[ev["event_type"]] == "new":
            made = set(ev["after"]) - set(ev["before"])
        at = next((n for n, o in enumerate(out) if o["date"] == ev["date"]
                   and made & (set(o["before"]) | set(o["after"]))), None)
        if at is None:
            out.append(ev)
        else:
            out.insert(at, ev)
            ctx.report["normalized"].append(
                f"`{ev['id']}` (creates {', '.join(sorted(made))}) ordered before "
                f"`{out[at + 1]['id']}` on the same day {ev['date']}.")
    return out


def _normalize(ctx, eid, etype, eff, raw_before, raw_after, b, a, inferred, note):
    """Put a research event in the validator's shape for its effect (shape only)."""
    rep = ctx.report["normalized"]
    if eff == "absorb":
        # research shape: before = [absorbed...], after = [absorber]
        if len(raw_after) != 1:
            raise SeedError(f"{eid}: absorption with {len(raw_after)} absorbers")
        absorber = raw_after[0]
        if absorber not in ctx.kept and b:
            rep.append(f"`{eid}`: absorption into `{absorber}` (outside phase 1) "
                       f"converted to a suppression of {', '.join(b)}, `inferred: true`.")
            note = _join(note, f"Seeding: the absorbing body ({absorber}) is outside "
                         "phase 1, so this absorption is recorded as the end "
                         "(suppression) of the absorbed body; the absorption itself "
                         "is not represented. Inferred: the act does not suppress "
                         "the body in these terms.")
            return "suppression", b, [], True, note
        if a and a[0] not in b:
            rep.append(f"`{eid}`: absorption reshaped: absorber `{a[0]}` added to before "
                       "(research lists it in after only).")
            b = b + a
        return etype, b, a, inferred, note
    if eff == "same" and set(b) != set(a):
        union = _dedupe(b + a)
        rep.append(f"`{eid}`: {etype} reshaped: before and after both set to "
                   f"{', '.join(union)} (research: {', '.join(b)} -> {', '.join(a)}).")
        note = _join(note, "Research direction: " + ", ".join(ctx.cid(x) for x in b)
                     + " -> " + ", ".join(ctx.cid(x) for x in a) + ".")
        return etype, union, union, inferred, note
    if eff == "end" and a:
        raise SeedError(f"{eid}: suppression with non-empty after; map it in event_map")
    return etype, b, a, inferred, note


def _assign_clauses(ctx, events):
    clauses = ctx.maps["clauses"]
    notes = clauses.get("_notes", {})
    by_id = {e["id"]: e for e in events}
    for rid, target in _clause_targets(ctx).items():
        ev = by_id.get(target)
        if ev is None:
            ctx.report["clauses"].append(f"clause for `{rid}` not used: `{target}` is not seeded.")
            continue
        ev["operative_clause"] = clauses[rid]
        if rid in notes:
            ev["note"] = _join(ev["note"], "Clause: " + notes[rid])
        ctx.report["clauses"].append(f"`{rid}` -> `{target}`")
    for ev in events:
        if ev["operative_clause"]:
            ev["clause_status"] = "transcribed"
        elif ev["inferred"]:
            ev["clause_status"] = "silent"
        else:
            ev["clause_status"] = "not-transcribed"


def _lifecycle(ctx, events):
    """body id -> creating events, body id -> ending events."""
    creates, ends = {}, {}
    for ev in events:
        eff = ctx.effects[ev["event_type"]]
        b, a = set(ev["before"]), set(ev["after"])
        if eff == "new":
            for x in a - b:
                creates.setdefault(x, []).append(ev)
            for x in b - a:
                ends.setdefault(x, []).append(ev)
        elif eff in ("absorb", "end"):
            for x in b - a:
                ends.setdefault(x, []).append(ev)
    return creates, ends


# --- bodies ---------------------------------------------------------------

def _founded(ctx, rbody, creates):
    key, ident = rbody["key"], ctx.cid(rbody["key"])
    km = ctx.km[key]
    made = creates.get(ident, [])
    if len(made) > 1:
        raise SeedError(f"{ident}: created by several events {[e['id'] for e in made]}")
    if key in ctx.fy:
        fy = ctx.fy[key]
        if made:
            raise SeedError(f"{ident}: attested founding but created by {made[0]['id']}")
        return {"date": fy["date"], "precision": fy["precision"], "basis": "attested",
                "act": fy["act_or_attestation"], "event": None, "verified": fy["verified"],
                "source_type": fy["source_type"], "source": fy["source"], "note": fy["note"]}
    er = rbody["erected"]
    date = km.get("founded_date") or er["date"]
    if not date or not _iso(date):
        raise SeedError(f"{ident}: no founding date")
    f = {"date": date, "precision": _precision(date), "basis": "act", "act": er["act"],
         "event": made[0]["id"] if made else None, "verified": er["verified"],
         "source_type": er["source_type"], "source": er["act"], "note": er.get("note")}
    if km.get("founded_date") and km["founded_date"] != er["date"]:
        f["note"] = _join(f["note"], f"The research erected.date {er['date']} is the date "
                          "the act was signed; founded.date is the date it took effect "
                          "(design §5 rule 9; seed/key_map.json founded_date).")
        if made:
            ev = made[0]
            if ev["date"] != date:
                ctx.report["date_changes"].append(
                    f"`{ev['id']}`: date {ev['date']} -> {date} (effective date per the "
                    f"research, key_map founded_date for `{ident}`); signed = {er['date']}.")
                ev["date"], ev["date_precision"] = date, _precision(date)
            ev["signed"] = er["date"]
    if not made:
        f["gap"] = ctx.gap(f"{ident}.founded", "The research records no founding event "
                           f"for this body (erected: {er['date']}, '{er['act']}'), so "
                           "founded.event is null.")
    elif made[0]["date"] != date:
        f["gap"] = ctx.gap(
            f"{ident}.founded",
            f"The research dates the erection {date} but the creating event "
            f"{made[0]['id']} ({made[0]['act']}) is dated {made[0]['date']}. "
            "A single event cannot carry both dates and the research does not "
            "say which governs both bodies; neither date was changed.")
    return f


def _ended(ctx, rbody, ends):
    ident, en = ctx.cid(rbody["key"]), rbody["ended"]
    stop = ends.get(ident, [])
    if not en:
        if stop:
            raise SeedError(f"{ident}: research says alive but {stop[0]['id']} ends it")
        return None
    if len(stop) > 1:
        raise SeedError(f"{ident}: ended by several events {[e['id'] for e in stop]}")
    e = {"date": en["date"], "precision": _precision(en["date"]), "basis": "act",
         "act": en["act"], "event": stop[0]["id"] if stop else None,
         "verified": en["verified"], "source_type": en["source_type"], "source": en["act"],
         "note": _join(f"How: {en['how']}." if en.get("how") else None, en.get("note"))}
    if not stop:
        e["gap"] = ctx.gap(f"{ident}.ended", "The research records no event that ends this "
                           f"body (ended: {en['date']}, '{en['act']}'), so ended.event is null.")
    elif stop[0]["date"] != en["date"]:
        e["gap"] = ctx.gap(f"{ident}.ended", f"The research dates the end {en['date']} but "
                           f"the ending event {stop[0]['id']} is dated {stop[0]['date']}.")
    return e


def _align_from(ctx, ident, lst, n, entry, lo):
    """Align a partial `from` that falls before founding within the same period."""
    f = entry["from"]
    if f is None or not _iso(f) or not _lt(f, lo):
        return
    if lo.startswith(f) and len(f) < len(lo):
        entry["from"] = lo
        entry["note"] = _join(entry.get("note"), f"Seeding: research 'from' {f} is the same "
                              f"period as founded.date {lo}; aligned to it.")
        ctx.report["normalized"].append(f"`{ident}.{lst}[{n}]`: from {f} aligned to {lo}.")


def _regime_by_act(ctx, text):
    """Earliest regime whose constitution's incipit appears in `text` (case-insensitive)."""
    best = None
    for r in ctx.vocab["sections"]["regimes"]:
        m = re.search(r"Const\. Apost\. ([^,]+),", r.get("act") or "")
        if m and text and m.group(1).lower() in text.lower():
            if best is None or _lt(r["effective"], best["effective"]):
                best = r
    return best


def _names(ctx, rbody, founded, events_by_body):
    ident, lo = ctx.cid(rbody["key"]), founded["date"]
    out, all_gaps, terminus, sub_from, sub_to = [], [], set(), set(), set()
    names = rbody["names"]
    for n, src in enumerate(names):
        e = {"name_la": src["name_la"], "name_it": src.get("name_it"),
             "name_en": src.get("name_en"), "from": src["from"], "to": src["to"],
             "act": src.get("act"), "verified": src["verified"],
             "source_type": src["source_type"], "source": src.get("act_source_url"),
             "note": src.get("note")}
        gaps = []
        all_gaps.append(gaps)
        if e["from"] is None or not _iso(e["from"]):
            if n == 0:
                gaps.append(f"The research gives no date for this name ('from': "
                            f"{json.dumps(src['from'])}); 'from' is set to founded.date {lo}.")
                e["from"] = lo
                sub_from.add(n)
            else:
                # R19: bound the unknown rename by the research's terminus ante quem,
                # the act in which the research attests the new name in use.
                reg = _regime_by_act(ctx, src.get("act"))
                prev = out[n - 1]
                if reg is None or prev["to"] is not None or not _lt(prev["from"],
                                                                   reg["effective"]):
                    raise SeedError(f"{ident}: names[{n}] undated and no terminus ante quem")
                tq = reg["effective"]
                e["from"] = prev["to"] = tq
                terminus.add(n)
                sub_to.add(n - 1)
                gaps.append(
                    f"Terminus ante quem, NOT the rename date: the research does not date "
                    f"this rename ('from': {json.dumps(src['from'])}) but attests the name "
                    f"in {reg['act']} (in force {tq}); 'from' is set to that date. "
                    + (f"Research note: '{src['note']}'" if src.get("note") else ""))
                all_gaps[n - 1].append(
                    f"'to' {tq} is a terminus ante quem (the next name is attested in "
                    f"{reg['act']}, in force {tq}), NOT the date of the rename, which "
                    "the research does not give.")
                ctx.report["normalized"].append(
                    f"`{ident}.names[{n - 1}..{n}]`: undated rename bounded by terminus "
                    f"ante quem {tq} ({reg['id']}).")
        if e["to"] is not None and not _iso(e["to"]):
            raise SeedError(f"{ident}: names[{n}].to {e['to']!r} is not ISO")
        _align_from(ctx, ident, "names", n, e, lo)
        if n > 0 and e["from"] is not None and n not in terminus:
            day = [ev for ev in events_by_body.get(ident, []) if ev["date"] == e["from"]]
            if not any(ev["event_type"].startswith("rename") and ident in ev["before"]
                       and ident in ev["after"] for ev in day):
                other = ", ".join(f"{ev['id']} ({ev['event_type']})" for ev in day)
                text = ("No rename event in the research records this change of name"
                        + (f"; the research records {other} on the same date." if other
                           else "; no event of any type on this date.")
                        + " No event was invented.")
                ctx.report["renames_without_event"].append(
                    f"`{ident}` names[{n}] from {e['from']} ('{e['name_la']}'): {text}")
                gaps.append(text)
        out.append(e)
    for n, (e, gaps) in enumerate(zip(out, all_gaps)):
        if e["to"] is None and n + 1 < len(out):
            raise SeedError(f"{ident}: names[{n}] open although a later name follows")
        if gaps:
            e["gap"] = " ".join(gaps)
    out = _unverify_substituted_names(ctx, ident, founded, names, out, sub_from, sub_to)
    for n, e in enumerate(out):
        if e.get("gap"):
            ctx.gap(f"{ident}.names[{n}]", e["gap"])
    return out


def _unverify_substituted_names(ctx, ident, founded, research, out, sub_from, sub_to):
    """R20 for names: a span whose `from` or `to` the seeder substituted is never verified.

    A substituted start (the research gives no date, so `from` = founded.date) is
    split off at the effective date of the constitution the name's act cites, if
    that falls inside the entry: before it the span is unverified, from it on the
    research's own verification stands. If the act names no such constitution, the
    whole entry is unverified. A substituted end (a terminus ante quem) cannot be
    split, because the rename date is unknown, so the whole entry is unverified.
    Unverified spans take source_type at most secondary (and at most founded's)."""
    cap = min(founded["source_type"], "secondary", key=SOURCE_RANK.__getitem__)
    res = []
    for n, e in enumerate(out):
        if n not in sub_from and n not in sub_to:
            res.append(e)
            continue
        st = min(e["source_type"], cap, key=SOURCE_RANK.__getitem__)
        down = {"verified": False, "source_type": st}
        reg = _regime_by_act(ctx, research[n].get("act")) if n in sub_from else None
        cov = reg["effective"] if reg else None
        if n not in sub_to and cov and _lt(e["from"], cov) and _lt(cov, e["to"]):
            res.append(dict(e, to=cov, **down, gap=_join(
                e.get("gap"), f"The name's act ('{research[n].get('act')}') attests it only "
                f"from {cov} ({reg['act']}); the span before that is unverified.")))
            rest = {k: v for k, v in e.items() if k != "gap"}
            rest["from"] = cov
            res.append(rest)
            ctx.report["normalized"].append(
                f"`{ident}` names[{n}] '{e['name_la']}': undated research entry split at "
                f"{cov}; {e['from']}-{cov} unverified/{st}, from {cov} as in the research.")
            continue
        if (e["verified"], e["source_type"]) != (False, st):
            why = ("its end is a terminus ante quem, not the rename date" if n in sub_to
                   else "its start was substituted and the research cites no act attesting the name "
                   "from that date")
            e = dict(e, **down, gap=_join(e.get("gap"), f"Unverified because {why} "
                     f"(research: verified {str(e['verified']).lower()}, "
                     f"{e['source_type']})."))
            ctx.report["normalized"].append(
                f"`{ident}` names[{n}] '{e['name_la']}': substituted bound; whole entry "
                f"unverified/{st}.")
        res.append(e)
    return res


def _kind_source_type(rbody, verified, frm):
    """Research kind entries carry `verified` but no source_type.

    verified true means checked against the act's text (research _meta), i.e.
    primary. For an unverified entry, take the source_type of the research
    name in force at its start, never above secondary (unverified)."""
    if verified:
        return "primary"
    name = None
    if frm is not None and _iso(frm):
        name = crcdr.at([n for n in rbody["names"] if n["from"] is None or _iso(n["from"])],
                        frm)
    st = name["source_type"] if name else "secondary"
    return st if SOURCE_RANK[st] <= SOURCE_RANK["secondary"] else "secondary"


def _substitute_kind_start(ctx, ident, founded, items):
    """R20: a kind with no research start is extended back to founded.date only unverified.

    The extended span is never verified and its source_type is at most the
    founded fact's (and at most secondary). If the kind's basis names a
    constitution, the research's verification is kept from that act's effective
    date on; otherwise the whole extended entry is unverified."""
    lo = founded["date"]
    cap = min(founded["source_type"], "secondary", key=SOURCE_RANK.__getitem__)
    out = []
    for e in items:
        if e["from"] is not None:
            out.append(e)
            continue
        reg = _regime_by_act(ctx, e["source"])
        cov = reg["effective"] if reg else None
        st = min(e["source_type"], cap, key=SOURCE_RANK.__getitem__)
        if cov and _lt(lo, cov) and _lt(cov, e["to"]):
            out.append(dict(e, **{
                "from": lo, "to": cov, "verified": False, "source_type": st,
                "gap": (f"The research gives no start date for this kind; its basis "
                        f"('{e['source']}') covers it only from {cov} ({reg['act']}). "
                        f"Extended back to founded.date {lo} unverified.")}))
            out.append(dict(e, **{"from": cov}))
            ctx.report["normalized"].append(
                f"`{ident}` kind '{e['kind']}': undated research entry split at {cov}; "
                f"{lo}-{cov} unverified/{st}, from {cov} as in the research.")
        else:
            out.append(dict(e, **{
                "from": lo, "verified": False, "source_type": st,
                "gap": (f"The research gives no start date for this kind and its basis "
                        f"('{e['source']}') does not cover the body from founded.date {lo}; "
                        "'from' is set to founded.date and the entry is unverified.")}))
            ctx.report["normalized"].append(
                f"`{ident}` kind '{e['kind']}': undated research entry extended to {lo}, "
                f"unverified/{st}.")
    return out


def _kinds(ctx, rbody, founded, ended):
    km = ctx.maps["kind_map"]
    key, ident, lo = rbody["key"], ctx.cid(rbody["key"]), founded["date"]
    research = rbody["kind"]
    items = []
    if key in km["by_body"]:
        dated = km["by_body"][key]
        last_to = research[-1]["to"]
        for n, it in enumerate(dated):
            to = dated[n + 1]["from"] if n + 1 < len(dated) else last_to
            src = next((r for r in research if r["from"] == it["from"]), None)
            same = src is not None and km["by_string"].get(src["kind"]) == it["kind"]
            if same:
                assert src is not None
                ver, st = src["verified"], _kind_source_type(rbody, src["verified"], it["from"])
                source, note = src["basis"], it.get("note")
            else:
                ver, st = False, "inferred"
                source = src["basis"] if src else "seed/kind_map.json by_body"
                note = _join(it.get("note"), "Seeding: kind set by seed/kind_map.json "
                             "by_body (editorial), so source_type inferred, verified false.")
                ctx.report["map_choices"].append(
                    f"`{ident}` kind {it['kind']} from {it['from']}: by_body editorial "
                    f"(research '{it['research_kind']}') -> inferred/false.")
            items.append({"kind": it["kind"], "from": it["from"], "to": to,
                          "verified": ver, "source_type": st, "source": source, "note": note})
    else:
        for r in research:
            if r["kind"] not in km["by_string"]:
                raise SeedError(f"{ident}: kind string {r['kind']!r} not in kind_map")
            items.append({"kind": km["by_string"][r["kind"]], "from": r["from"], "to": r["to"],
                          "verified": r["verified"],
                          "source_type": _kind_source_type(rbody, r["verified"], r["from"]),
                          "source": r["basis"],
                          "note": (f"Research kind: '{r['kind']}'."
                                   if r["kind"] != km["by_string"][r["kind"]] else None)})
    items = _substitute_kind_start(ctx, ident, founded, items)
    for n, e in enumerate(items):
        if "gap" in e:
            ctx.gap(f"{ident}.kind[{n}]", e["gap"])
        _align_from(ctx, ident, "kind", n, e, lo)
        hi = ended["date"] if ended else None
        if e["to"] is None and hi is not None:
            raise SeedError(f"{ident}: kind[{n}] open but the body ended")
    return items


def _sections(ctx, rbody, ident, founded, ended, kinds):
    sec = ctx.vocab["sections"]
    regimes = {r["id"]: r for r in sec["regimes"]}
    eff_dates = [r["effective"] for r in sec["regimes"] if r["effective"]]
    overrides = {(o["body"], o["regime"]): o
                 for o in ctx.maps["section_overrides"]["entries"]}
    lo, hi = founded["date"], (ended["date"] if ended else None)
    pieces = []
    for k in kinds:
        f, t = _later(k["from"], lo), _earlier(k["to"], hi)
        if not _lt(f, t):
            continue
        bounds = [f] + [d for d in eff_dates if _lt(f, d) and _lt(d, t)] + [t]
        for a, b in zip(bounds, bounds[1:]):
            pieces.append(_section_entry(ctx, rbody, ident, regimes, overrides, k["kind"], a, b))
    merged = []
    for p in pieces:
        q = merged[-1] if merged else None
        if q and q["to"] == p["from"] and all(
                q.get(x) == p.get(x) for x in ("regime", "section", "in_curia", "source",
                                               "source_type", "verified", "note", "gap")):
            q["to"] = p["to"]
        else:
            merged.append(p)
    for n, p in enumerate(merged):
        if "gap" in p:
            ctx.gap(f"{ident}.section[{n}]", p["gap"])
    return merged


def _section_entry(ctx, rbody, ident, regimes, overrides, kind, frm, to):
    rid = crcdr.regime_at(ctx.vocab["sections"], frm)
    reg = regimes[rid]
    o = overrides.get((rbody["key"], rid))
    if o:
        e = {"regime": rid, "section": o["section"], "from": frm, "to": to,
             "source": o["source"], "source_type": o["source_type"],
             "verified": o["verified"], "note": o.get("note")}
        if o["section"] == "not-listed":
            e["in_curia"] = o["in_curia"]
            if o["in_curia"] is None:
                e["gap"] = (f"Not listed by the constitution of {rid}, and in_curia is "
                            "not established by the research. Research curia_status "
                            f"(free text, not parsed): '{rbody['curia_status']}'")
        return e
    hit = [s for s in reg["sections"] if kind in s["kinds"]]
    e = {"regime": rid, "section": hit[0]["id"] if hit else "not-listed", "from": frm,
         "to": to, "source": f"data/sections.json ({rid}) and this body's kind '{kind}'",
         "source_type": "inferred", "verified": False, "note": DERIVED_NOTE}
    if not hit:
        e["in_curia"] = None
        e["gap"] = (f"Kind '{kind}' has no section in {rid} and no override places the body, "
                    "so in_curia is unknown. Research curia_status (free text, not "
                    f"parsed): '{rbody['curia_status']}'")
    return e


def _part_of(ctx, key):
    out = []
    for p in ctx.maps["part_of"]["entries"]:
        if p["body"] != key:
            continue
        e = {"body": ctx.cid(p["target"]), "relation": p["relation"], "from": p["from"],
             "to": p["to"], "source": p["source"], "source_type": p["source_type"],
             "verified": p["verified"], "note": p.get("note")}
        out.append(e)
    return out


def _body_note(rbody):
    parts = [rbody.get("notes")]
    cc = rbody.get("competence_changes") or []
    if cc:
        parts.append("Competence changes (research): " + "; ".join(
            f"{c.get('date')}: {c.get('change')} ({c.get('act')})" for c in cc) + ".")
    return _join(*parts)


# --- lineage comparison ------------------------------------------------------

def _lineage(ctx, events):
    derived = set()
    for ev in events:
        eff = ctx.effects[ev["event_type"]]
        b, a = set(ev["before"]), set(ev["after"])
        if eff == "new":
            for p in b - a:
                for s in a - b:
                    derived.add((p, s))
        elif eff == "absorb":
            for p in b - a:
                for s in b & a:
                    derived.add((p, s))
    research, outside = set(), []
    for rbody in ctx.rb:
        for lst, flip in (("predecessors", True), ("successors", False)):
            for link in rbody.get(lst) or []:
                pair = (link["key"], rbody["key"]) if flip else (rbody["key"], link["key"])
                if not all(x in ctx.kept for x in pair):
                    outside.append(f"{pair[0]} -> {pair[1]} ({link.get('event')})")
                    continue
                research.add((ctx.cid(pair[0]), ctx.cid(pair[1])))
    rep = ctx.report["lineage"]
    rep.append(f"Derived links: {len(derived)}; research links between phase-1 bodies: "
               f"{len(research)}.")
    for p, s in sorted(research - derived):
        rep.append(f"In the research, not derived from events: `{p}` -> `{s}`")
    for p, s in sorted(derived - research):
        rep.append(f"Derived from events, not in the research: `{p}` -> `{s}`")
    for x in sorted(set(outside)):
        rep.append(f"Research link involving a body outside phase 1 (not compared): {x}")


# --- build ----------------------------------------------------------------------

def build(research_bodies, research_events, maps, vocab):
    """Return (bodies_doc, events_doc, report_lines)."""
    ctx = _Ctx(research_bodies, research_events, maps, vocab)
    for rbody in ctx.rb:
        if rbody["key"] not in ctx.kept:
            ctx.report["dropped_bodies"].append(rbody["key"])
    events = _seed_events(ctx)
    creates, ends = _lifecycle(ctx, events)
    by_body = {}
    for ev in events:
        for x in set(ev["before"]) | set(ev["after"]):
            by_body.setdefault(x, []).append(ev)
    bodies = []
    for rbody in ctx.rb:
        key = rbody["key"]
        if key not in ctx.kept:
            continue
        ident = ctx.cid(key)
        founded = _founded(ctx, rbody, creates)
        ended = _ended(ctx, rbody, ends)
        kinds = _kinds(ctx, rbody, founded, ended)
        bodies.append({
            "id": ident, "founded": founded, "ended": ended,
            "names": _names(ctx, rbody, founded, by_body),
            "kind": kinds,
            "section": _sections(ctx, rbody, ident, founded, ended, kinds),
            "part_of": _part_of(ctx, key),
            "aliases": [], "note": _body_note(rbody),
        })
    _lineage(ctx, events)
    bodies_doc = {"entries": bodies}
    events_doc = {"entries": events}
    return bodies_doc, events_doc, _report(ctx, bodies, events, vocab, bodies_doc, events_doc)


def _report(ctx, bodies, events, vocab, bodies_doc, events_doc):
    rep = validate.validate(bodies_doc, events_doc, vocab)
    r = ctx.report
    lines = ["# Seed report", "",
             "Generated by `scripts/seed_from_research.py` from `seed/research/` and the "
             "curated maps in `seed/`. Do not edit by hand.", "",
             "## Counts", "",
             f"- Research bodies: {len(ctx.rb)}; seeded: {len(bodies)}; dropped: "
             f"{len(r['dropped_bodies'])}.",
             f"- Research events: {len(ctx.re)}; seeded events: {len(events)} "
             f"(from {len({e['research_id'] for e in events})} research events).",
             f"- clause_status: " + ", ".join(
                 f"{s} {sum(1 for e in events if e['clause_status'] == s)}"
                 for s in ("transcribed", "not-transcribed", "silent")) + ".",
             f"- Gap notes added: {len(r['gaps'])}.",
             f"- Validator: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s).", ""]

    def section(title, items, intro=None):
        lines.extend([f"## {title}", ""])
        if intro:
            lines.extend([intro, ""])
        lines.extend(f"- {x}" for x in items) if items else lines.append("- (none)")
        lines.append("")

    section("Dropped bodies", [f"`{k}`" for k in r["dropped_bodies"]],
            "Research bodies with no entry in `seed/key_map.json` (phase-1 exclusions and "
            "held-out bodies). Their ids are removed from every event.")
    section("Dropped events", r["dropped_events"])
    section("Normalizations and conversions", r["normalized"],
            "Shape changes only: same-effect types get identical before/after; an "
            "absorption lists the absorber in both. No meaning is changed except where "
            "stated (and flagged `inferred`).")
    section("Date changes", r["date_changes"])
    section("Gap notes added", r["gaps"])
    section("Editorial kind choices", r["map_choices"])
    section("Operative clauses", r["clauses"])
    section("Renames with no event in the research", r["renames_without_event"],
            "Dated name changes that no rename event records. The name entry carries a "
            "`gap` note; no event was invented.")
    section("Predecessor/successor links: events vs the research", r["lineage"],
            "Links derived from events (merger/split/re-foundation: before -> new bodies; "
            "absorption: absorbed -> absorber) compared with the research's own "
            "`predecessors`/`successors`, which are not carried into `data/`.")
    section("Validator warnings", rep.warnings)
    if rep.errors:
        section("Validator errors", rep.errors)
    return lines


def _dump(path, doc):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    bodies, events, report = build(*load_inputs())
    _dump(os.path.join(crcdr.ROOT, "data", "bodies.json"), bodies)
    _dump(os.path.join(crcdr.ROOT, "data", "events.json"), events)
    with open(os.path.join(crcdr.ROOT, "seed", "seed-report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report).rstrip() + "\n")
    print(f"seeded {len(bodies['entries'])} bodies, {len(events['entries'])} events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
