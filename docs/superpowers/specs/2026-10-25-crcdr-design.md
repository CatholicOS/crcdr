# CRCDR — Common Roman Curia Data Repository: design

Status: draft for review · 2026-10-25 · tracks [CatholicOS/cdcf-uri-scheme#20](https://github.com/CatholicOS/cdcf-uri-scheme/issues/20)

## 1. Intent

Magisterial and curial documents are issued by bodies of the Roman Curia: *Fiducia Supplicans* by the DDF (2023), *Donum Veritatis* by the CDF (1990). Today nothing identifies those issuers stably:

- the URI scheme has `cdcf:institution/dicastery/ddf`, which is named after the body's current name;
- CMDDR has no curial issuers at all.

Curial bodies are renamed, merged, split, suppressed and re-founded. An identifier built on today's name misattributes every earlier document, and it has no answer for bodies that were merged away.

CRCDR is a new CDCF common data repository (c\*dr). It does for curial bodies what CRPDR does for popes and COECDR for councils: it enumerates a closed set and gives each member a canonical identifier that never changes. It also records each body's dated names, kinds and positions in the Curia, and the events that changed them, so that a name on a document dated D resolves to the right body.

**Why now:** it unblocks curial issuers in CMDDR and in the URI scheme ([#16](https://github.com/CatholicOS/cdcf-uri-scheme/issues/16), [#20](https://github.com/CatholicOS/cdcf-uri-scheme/issues/20)), and it lets `cdcf:institution/` be retired ([#13](https://github.com/CatholicOS/cdcf-uri-scheme/issues/13)).

**Success:** every curial body that has existed since 1588 has exactly one `cr:` identifier, and for any (name, date) pair the registry says which body is meant. Every fact is marked verified or unverified, with its source. A Latin-literate reviewer can check any identity decision against the operative clause of the act behind it.

## 2. Goals, non-goals, anti-goals

**Goals**
- A closed, enumerable set of curial bodies, each with a stable `cr:` identifier.
- A dated history for each body: names (Latin, plus Italian and English where known), `kind`, `section`, part-of relations.
- An event log of every change (foundation, rename, absorption, merger, split, suppression, …), each tied to its act.
- Validation that keeps the data internally consistent.
- Conventions consistent with the sibling registries (CESIDR, CRPDR, COECDR).

**Non-goals**
- **Authority.** Whether a body's documents bind, and how much, belongs to CMDDR, where authority attaches to the act (genre plus per-passage assessment), not to the issuer. CRCDR records what a body was and where it sat, nothing more.
- **Documents.** CRCDR does not list what a body issued. Documents are CMDDR's.
- **Office holders** (prefects, presidents). These may be added later, but are not part of this design.
- **Bodies outside the Curia and its connected institutions:** episcopal conferences, nunciatures, diocesan curias.

**Anti-goals: what would make this a failure even if it works**
- An identifier that changes because a body was renamed. That is the defect CRCDR exists to fix.
- One body split into two identifiers, or two bodies merged into one, because of a name or a label and not the act's operative clause. Examples: CDF and DDF as two issuers; the two Congregations for Divine Worship as one.
- An identity decision that rests on an inference without being flagged as one.
- Asserting authority or teaching weight from a body's `kind`.

## 3. Scope

The set is every body that, at any time since Sixtus V's *Immensa Aeterni Dei* (1588), has belonged to the Roman Curia, together with the Pontifical Academies and the institutions connected with the Holy See. It includes bodies founded before 1588 that existed then, such as the Holy Office (1542).

- **Curial bodies:** congregations, pontifical councils, secretariats, commissions and committees, dicasteries, tribunals (e.g. the Apostolic Penitentiary), offices (e.g. the Secretariat of State, the Datary, the Apostolic Camera) and prefectures.
- **Academies:** the Pontifical Academy of Sciences, the Pontifical Academy for Life, and the others.
- **Institutions connected with the Holy See:** the Vatican Apostolic Library and Archive, the Fabric of St Peter, and so on.
- **Sixtus V's six congregations for governing the Papal States:** in scope, since they were curial bodies in 1588, but in phase 2 (§10).

The prefix names the registry, not a claim about each member. Whether a body was inside the Curia at a given date is recorded by `section` (§6.3).

## 4. Identifier

```
cr:<latin-slug>-<founding-year>
```

Long form `curia-romana:`; the short form is canonical ([#13](https://github.com/CatholicOS/cdcf-uri-scheme/issues/13) point 5). Examples:

| Body | Identifier |
|---|---|
| Inquisition → Holy Office → CDF → DDF | `cr:doctrina-fidei-1542` |
| Congregation for Divine Worship, 1969–1975 | `cr:cultus-divinus-1969` |
| Congregation for Divine Worship, created 1984 | `cr:cultus-divinus-1984` |
| Apostolic Penitentiary | `cr:paenitentiaria-apostolica-<year>` |
| Index (ended 1917) | `cr:index-<year>` |

### Rules

1. **Latin.** The slug follows the Latin name, because the founding and reforming acts are in Latin and the English names are variable translations. This follows CDOCTDR and CRMEDR: the slug follows the authoritative source.
2. **Minted once, from the name in use when the key is minted:** the current name for a living body, the last name for one that has ended. Later renames go only into the dated `names` list (§6.1). Before the first stable release, a key may still be corrected, with a changelog entry. After it, keys are frozen.
3. **The distinguishing noun phrase, in the nominative.** Drop the generic kind words (*Dicasterium*, *Congregatio*, *Sacra*, *Suprema*, *Pontificium Consilium*, *Secretariatus*, *Commissio*, *Tribunal*, *Officium*, *Praefectura*, *Pontificia Academia*) and the governing preposition (*pro*, *de*). Normalize the rest to the nominative, as CDOCTDR does (`cultus-divinus`, not `cultu-divino`). Keep the connective *et*. If dropping the kind word would leave nothing distinctive, keep it (`secretaria-status`, `paenitentiaria-apostolica`). ASCII-fold, lower-case, hyphenate.
4. **Founding year, always** — the same reasoning as CMDDR's unconditional year. Two different bodies have borne the same name (`cultus-divinus-1969` and `-1984`), and a year added only on collision would force keys to change. The founding year is the year the founding act took effect. For a body with no founding act (the Penitentiary, the Secretariat of State, the Camera), it is the **earliest securely attested year**, flagged `founded.basis: "attested"`. If earlier evidence turns up after keys are frozen, the key keeps its year and only `founded` is corrected.
5. **Grammar** (to be added to the URI scheme's Appendix D under #20; this registry cites it and keeps no copy):
   ```abnf
   cr-key     = latin-slug HYPHEN year
   latin-slug = 1*ALPHA *(HYPHEN 1*ALPHA)   ; no digits, so the year split is unambiguous
   year       = 4DIGIT
   ```

## 5. Identity rules

These rules were tested against the research (`docs/curia-history-report.md`, hard cases H1–H20).

1. **Continuity follows the act's operative clause, never its preamble or a label.** For example, *Alloquentes proxime* (1917) speaks of unity in its preamble, but its operative clause says the Index "iam nunc non erit". That is an absorption (H4).
2. **The body keeps its identifier through:**
   - a rename;
   - a rename with new competence (*Integrae servandae*, 1965: name and *ordo* together, H1; Council → Clergy, 1967, H2);
   - a change of kind or section (the Secretariat of State and the Almonry, H13);
   - a transfer of competence;
   - a revival that the act presents as such (Rota, 1908: "rursus in exercitium revocamus", H10).
3. **Absorption:** the absorbing body keeps its identifier, and the absorbed body ends (H4, H5).
4. **Merger:** a new identifier, and every predecessor ends. Example: Evangelization, 2022.
5. **Split:** a new identifier for each new body. The original continues only if the act keeps it. Example: Rites in 1969 ends, and two new bodies begin.
6. **Re-foundation:** a new identifier, linked to its predecessor as successor, whether the succession is explicit (Family, 1981: "succedit eique sufficitur", H17) or by imitation only (*Recognito*, 1984, H15). Where an act "institutes" rather than "restores" (Signatura, 1908: "restituimus, seu melius instituimus", H10), it is a re-foundation.
7. **Same name, different body:** different identifiers. Name lookup is always by (name, date) (H6, H18).
8. **Silent acts.** When a closed-list constitution omits a body (Bishops-and-Regulars in 1908, the Datary in 1967, H9), the default is **suppression by omission**, dated to the constitution's effective date and flagged `inferred: true`. Any other reading of a silent act is also flagged `inferred: true`, with a note.
9. **Effective date governs.** `from`/`to` dates are the dates the act took effect; the signing date is recorded separately. A document dated between signing and effect was issued by the old body (H14).
10. **Not identity:**
    - a personal union (a shared president, H19);
    - a part-of placement (Minors within the DDF, Migrants under Bishops, H16), which is a dated relation (§6.4).

## 6. Data model

All dates are ISO 8601, written at the precision known: `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. For comparison, a partial date counts as its first day. Every interval is **`from` inclusive, `to` exclusive**, with `to: null` meaning it is still open. The date a rename takes effect therefore belongs to the new name. Each dated fact carries `verified` (bool), `source_type` (`primary` | `official-secondary` | `secondary` | `inferred`), a source URL or citation, and an optional `note`. The research files (§9) already use this convention.

### 6.1 `data/bodies.json`

One entry per body:

| Field | Content |
|---|---|
| `id` | `cr:` key |
| `founded` | `{ date, precision: day\|month\|year\|century, basis: act\|attested, act, event }` |
| `ended` | same shape, or `null` |
| `names[]` | dated: `name_la` (required), `name_it`, `name_en`, `from`, `to`, `act` |
| `kind[]` | dated `kind` values (§6.3) |
| `section[]` | dated `{ regime, section }` pairs (§6.3) |
| `part_of[]` | dated `{ body, relation, from, to }` (§6.4) |
| `aliases` | other names used in sources (e.g. "Propaganda Fide"), for lookup |
| `note` | free text |

Predecessors and successors are not stored on bodies. They are derived from events (§6.2) and written into the generated registry.

### 6.2 `data/events.json`

One entry per change, in chronological order:

| Field | Content |
|---|---|
| `id` | stable event id |
| `date` | effective date, with `date_precision` |
| `signed` | signing date, if it differs |
| `act` | citation (author, form, incipit, date, AAS reference) |
| `mag` | the CMDDR `mag:` id when CMDDR registers the act; otherwise `null` |
| `event_type` | §6.3 |
| `before[]`, `after[]` | body ids |
| `operative_clause` | the quoted Latin clause that decides identity, or `null` |
| `clause_status` | `transcribed` (clause quoted) · `not-transcribed` (the act states it, but the clause has not yet been copied in; the research quotes clauses for only about 10 events) · `silent` (the act does not state it; the event must then be `inferred: true`) |
| `inferred` | bool |
| provenance | `source`, `source_type`, `verified`, `note` |

### 6.3 Vocabularies

Each vocabulary is its own file, like CESIDR's `tradition.json`.

- **`data/kinds.json`: what the act calls the body.**
  - Values: `congregation`, `council` (a *Consilium* that was not yet pontifical, e.g. *Consilium de Laicis*, 1967), `pontifical-council`, `secretariat`, `commission`, `committee`, `dicastery`, `tribunal`, `office`, `prefecture`, `academy`, `institution`.
  - Each value has a Latin term and its English equivalents. The Latin term governs; the English is a translation that varies (H3: *Consilium* translated as "Commission").
- **`data/sections.json`: where the governing constitution of the period places the body.**
  - Grouped by **regime**: `pre-1588` (no constitution; its only value is `not-listed`, and it covers the Holy Office from 1542 and the Index from 1571), `immensa-1588`, `sapienti-consilio-1908`, `cic-1917`, `reu-1968`, `pastor-bonus-1989`, `praedicate-evangelium-2022`.
  - Each regime has an effective date and its own divisions, taken from that constitution's own structure. For *Praedicate Evangelium* these are: Secretariat of State, dicasteries, bodies of justice, economic bodies, offices, advocates, institutions connected with the Holy See.
  - Each section value declares `in_curia: true | false`.
  - A body the constitution does not place takes `not-listed`. Its dated `section` entry then carries its own `in_curia` value with a source. Example: *Immensa* omits the Penitentiary, the Rota and the Camera, which were nonetheless in the Curia.
  - The regime in force at a date is the latest whose effective date is on or before it.
- **`data/event_types.json`:**
  - Values: `foundation`, `rename`, `rename-competence`, `kind-change`, `competence-transfer`, `absorption`, `merger`, `split`, `re-foundation`, `revival`, `suppression`, `attachment`.
  - Each value declares its identity effect: same id, new id, or ends.
  - The research's `merger-or-rename`, `reorganization`, `codification` and `regulation` are resolved into these types at seeding, and the resolution is flagged `inferred` where the act is silent.

### 6.4 Part-of relations

`part_of[]` records a dated placement of one body within or under another. The relation is one of:
- `within`: Minors within the DDF, 2022;
- `subject-to`: Migrants under Bishops, 1970;
- `section-of`: the Council for Public Affairs as 2nd Section of the Secretariat of State, 1989;
- `complement-of`: Health and Laity, 1985.

A placement never changes identity.

## 7. Validation (`scripts/validate.py`)

The validator reports two levels:
- **Errors:** inconsistencies. These must be zero for a build to pass.
- **Warnings:** documented gaps. A fact or interval that breaks a rule below because the research could not find it (an end date never located, names that don't cover the whole lifespan, the undated 1999 rename) carries a `gap` note explaining what is missing. It is then reported as a warning, not an error. The generated registry lists every warning, so the gaps stay visible.

Rules:

1. Every `id` matches the grammar, is unique, and ends in the year of `founded.date`.
2. Every dated list (`names`, `kind`, `section`, `part_of`) is ordered and non-overlapping, and lies within `founded`…`ended`. `names` covers the whole lifespan; any gap must carry a note.
3. Every `section` value exists in the regime in force on its `from` date.
4. Every event references existing bodies, and its `before`/`after` sets are consistent with its type's identity effect:
   - a rename has `before == after`;
   - a merger or split creates bodies whose `founded.event` is this event;
   - an absorption keeps the absorbing body in both sets and ends the absorbed one.
5. Every body's `founded.event` and `ended.event` resolve to events of a matching type and date.
6. Every vocabulary value is a member of its vocabulary file.
7. Every non-`foundation` event has a `clause_status`:
   - `transcribed` requires `operative_clause`;
   - `silent` requires `inferred: true`;
   - `not-transcribed` is a warning, and transcribing these clauses is phase 2 work.

## 8. Outputs and licensing

- **`registry/bodies.md`**: generated, never hand-edited, as in the siblings. Bodies are grouped by current section, then by historical regime. Unverified facts are visibly marked.
- **Per-lineage tables:** wanted (they are the most-asked question), but the format is left to the builder.
- **`data/identifiers.json`**: generated. It holds ids, aliases, predecessor/successor links and `mag:` act references, and is licensed **CC0 1.0** (`LICENSE-CC0`).
- Everything else in `data/`, `registry/` and `docs/` is licensed **CC BY-ND 4.0** (`LICENSE`), following the proposal open in every sibling registry (e.g. CatholicOS/crpdr#2). `scripts/` is licensed **Apache 2.0** (`scripts/LICENSE`).

## 9. Seeding from the research

The research is in the session scratchpad `curia/`, to be copied into the repository:
- `bodies.json`: 76 bodies with provisional keys;
- `events.json`: 121 events, 82 of them checked against the act;
- `report.md` → `docs/curia-history-report.md`;
- `build_curia.py`.

Seeding steps:
1. Map each provisional key to a `cr:` key under §4. Record the mapping, and note any key whose Latin name could not be confirmed from an act.
2. Resolve the research's ad-hoc event types into §6.3.
3. Split the research's `kind` and `curia_status` text into dated `kind` and `section` entries.
4. Carry over every `verified` / `source_type` flag unchanged. Seeding must not upgrade a fact's verification.
5. Run `validate.py` until it passes. Where a failure reflects a real gap in the research, record it in the report instead of inventing data.

## 10. Phases

- **Phase 1 (this build):**
  - the repository, schema, vocabularies, validator and generator;
  - **Founding-year research for the 13 bodies the research leaves undated:** Secretariat of State, Penitentiary, Rota, Camera, Datary, Chancery, Apostolic Briefs, Briefs to Princes, Signatura Gratiae, Ceremonial, Almonry, Revision of Councils, Apostolic Visitation. For each, find the earliest securely attested year, preferring primary acts and naming the source, and record it with `founded.basis: "attested"` and the matching `source_type`. A body whose year cannot be secured to a specific year is held out of phase 1 and listed in the report; it does not get a guessed year. (Decided by the project owner, 2026-10-25.)
  - the researched bodies and events, seeded and validating with zero errors. The research records `sixtine-temporal-congregations` (one record standing for six bodies, which is the anti-goal) and `fabric-st-peter` (an institution connected with the Holy See) are left out of phase 1, and so are the events that only they take part in. That leaves 74 bodies;
  - README and `docs/schema-proposal.md` with the open questions (§12).
- **Phase 2:**
  - the Pontifical Academies and the institutions connected with the Holy See;
  - Sixtus V's Papal States congregations, traced one by one;
  - transcription of every `not-transcribed` operative clause from the acts;
  - verification of the facts before 1908 against the *Bullarium Romanum* and Del Re, *La Curia Romana*;
  - the Latin names of the 2022 dicasteries;
  - a check of AAS 2025–26.
- **Phase 3:** a review against the *Annuario Pontificio*, which is the authority and is not online.

## 11. Decided, and left to the builder

**Decided** (by the project owner in discussion, 2026-10-25):
- the name CRCDR;
- the prefix `cr:` / `curia-romana:`;
- the wide scope, including tribunals, offices and academies;
- Latin keys with the founding year;
- the two dated fields `kind` and `section`;
- no authority recorded in this registry;
- the split licensing.

**Editor's calls in this document**, open to the owner's correction:
- nominative normalization and kind-word stripping (§4 rule 3);
- the earliest attested year for bodies with no founding act (§4 rule 4);
- suppression by omission as the default for silent acts (§5 rule 8);
- Sixtus V's Papal States congregations in scope but in phase 2;
- the vocabularies in §6.3.

**Editor's calls made after the builder check** (2026-10-25):
- `clause_status` instead of requiring a clause for every event;
- errors vs warnings, with `gap` notes;
- the `pre-1588` regime and the per-entry `in_curia` value for `not-listed`;
- dropping the two research records from phase 1.

**Where the work lands:**
- A new **public** GitHub repository, `CatholicOS/crcdr`, with default branch `main`, like the siblings.
- The first commit on `main` holds this design document. The phase 1 build happens on a feature branch and goes in through a pull request.
- Adding the `cr-key` grammar to the URI scheme's Appendix D, and retiring `cdcf:institution/dicastery/`, is a **separate** cdcf-uri-scheme PR under #20 and is not part of this build.

**Left to the builder:**
- the generator's layout and the per-lineage table format;
- the scripts' structure (Python 3, standard library only, like the siblings);
- CI wiring;
- README prose.

## 12. Open questions for the committee (recorded in `docs/schema-proposal.md`)

1. Lineage depth: does Consecrated Life go back to Regulars (1586), or start in 1908 (H8)? The *Annuario*'s own historical notes should decide.
2. *Seminaria clericorum* (1915): a rename of Studies, or a new body absorbing it (H11)?
3. The 2022 mergers, which *Praedicate Evangelium* never states article by article (H5).
4. Whether CMDDR's `issuerType` gains `dicastery`, or a generic `curial-body` that defers to CRCDR's dated `kind`.
5. The Latin wording of each key, which needs a Latinist's review before any key is frozen.

## 13. Sign-off

Draft pending TAG review (§6.3 of the URI scheme). A canonist or historian of the Curia, and a Latinist for the keys, should review it before anything is frozen.
