"""Shared helpers for CRCDR: dates, intervals, vocabularies."""
import datetime
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ID_RE = re.compile(r"^cr:[a-z]+(?:-[a-z]+)*-\d{4}$")

_DATE_RE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


def parse_date(s):
    """Parse YYYY, YYYY-MM or YYYY-MM-DD; a partial date is its first day."""
    m = _DATE_RE.match(s) if isinstance(s, str) else None
    if not m:
        raise ValueError(f"invalid date: {s!r}")
    y, mo, d = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)
    return datetime.date(y, mo, d)


def in_interval(d, frm, to):
    """True if frm <= d < to; None bounds are open."""
    x = parse_date(d)
    if frm is not None and x < parse_date(frm):
        return False
    if to is not None and x >= parse_date(to):
        return False
    return True


def at(dated, d):
    """The entry of `dated` in force at d, or None."""
    for e in dated:
        if in_interval(d, e.get("from"), e.get("to")):
            return e
    return None


def load(name):
    with open(os.path.join(ROOT, "data", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def regime_at(sections, d):
    """Id of the regime in force at d (latest effective date <= d)."""
    best, best_date = None, None
    for r in sections["regimes"]:
        if r["effective"] is None:
            if best is None:
                best = r["id"]
            continue
        e = parse_date(r["effective"])
        if e <= parse_date(d) and (best_date is None or e > best_date):
            best, best_date = r["id"], e
    return best


_LIGATURES = {"æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE"}


def fold(s):
    """ASCII-fold (ligatures expanded, diacritics dropped) and lower-case."""
    for k, v in _LIGATURES.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()
