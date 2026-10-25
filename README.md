# CRCDR

The home of the **Common Roman Curia Data Repository**, curated by the **Catholic Engineering Task Force** of the [Catholic Digital Commons Foundation](https://github.com/CatholicOS).

## What is CRCDR?

The Common Roman Curia Data Repository (CRCDR) provides canonical identifiers (`cr:`) for the bodies of the Roman Curia and the institutions connected with the Holy See, together with each body's dated names, kinds and places in the Curia, and the events (foundation, rename, merger, split, suppression, …) that changed them.

It does for curial bodies what CRPDR does for popes and COECDR for councils: it enumerates a closed set and gives each member an identifier that never changes.

## Why?

Magisterial and curial documents are issued by bodies of the Roman Curia: *Fiducia Supplicans* by the Dicastery for the Doctrine of the Faith (2023), *Donum Veritatis* by the Congregation for the Doctrine of the Faith (1990). Today nothing identifies those issuers stably. Curial bodies are renamed, merged, split, suppressed and re-founded, so an identifier built on today's name misattributes every earlier document and has no answer for bodies that were merged away.

CRCDR gives each body one identifier, and records enough history that for any (name, date) pair the registry says which body is meant. It tracks [CatholicOS/cdcf-uri-scheme#20](https://github.com/CatholicOS/cdcf-uri-scheme/issues/20) and unblocks curial issuers in the URI scheme ([#16](https://github.com/CatholicOS/cdcf-uri-scheme/issues/16)) and in CMDDR.

## The identifier scheme (draft)

```
cr:<latin-slug>-<founding-year>
```

The long form is `curia-romana:`; the short form is canonical. The slug follows the Latin name in the nominative, with the generic kind words (*Dicasterium*, *Congregatio*, *Sacra*, …) and the governing *pro*/*de* dropped. The year is the year the founding act took effect, always present, because two different bodies have borne the same name. The key is minted once, from the name in use when it is minted; later renames go only into the dated `names` list. As a regex: `^cr:[a-z]+(?:-[a-z]+)*-\d{4}$`.

Examples, taken from the data:

| Body | Identifier |
|---|---|
| Inquisition → Holy Office → CDF → DDF | `cr:doctrina-fidei-1542` |
| Congregation for Divine Worship, 1969–1975 | `cr:cultus-divinus-1969` |
| Congregation for Divine Worship, created 1984 | `cr:cultus-divinus-1984` |
| Apostolic Penitentiary | `cr:paenitentiaria-apostolica-1256` |
| Index of Forbidden Books (ended 1917) | `cr:index-1571` |

The identity rules (what keeps an identifier, what mints a new one) and the full data model are in [docs/schema-proposal.md](docs/schema-proposal.md). **All IDs are drafts pending committee review.**

## Scope

Every body that, at any time since Sixtus V's *Immensa Aeterni Dei* (1588), has belonged to the Roman Curia, together with the Pontifical Academies and the institutions connected with the Holy See; bodies founded earlier that existed in 1588, such as the Holy Office (1542), are included.

**Phase 1 (this release)** covers **64 bodies** and **126 events**. Held out of phase 1:

- **9 bodies whose founding year could not be secured** (no year is guessed): the Apostolic Camera, the Secretariat of State, the Apostolic Briefs, the Briefs to Princes, the Apostolic Chancery, the Apostolic Datary, the Signatura Gratiae, the Ceremonial and the Papal Almonry. The evidence and next source for each is in [`seed/founding_years.json`](seed/founding_years.json).
- **`state-of-regulars`**, because the research record conflates two bodies (1652 and 1847).
- **Two out-of-scope records:** `sixtine-temporal-congregations` (one record standing for six bodies; phase 2) and `fabric-st-peter` (an institution connected with the Holy See; phase 2).

The Pontifical Academies, the institutions connected with the Holy See and Sixtus V's Papal States congregations are phase 2.

## Two dated fields: `kind` and `section`

- **`kind`** is what the act calls the body (`congregation`, `council`, `pontifical-council`, `secretariat`, `commission`, `committee`, `dicastery`, `tribunal`, `office`, `prefecture`, `academy`, `institution`). The Latin term governs; English translations vary.
- **`section`** is where the governing constitution of the period places the body, grouped by regime (`pre-1588`, `immensa-1588`, `sapienti-consilio-1908`, `cic-1917`, `reu-1968`, `pastor-bonus-1989`, `praedicate-evangelium-2022`). Each section value declares whether it is `in_curia`.

Both are dated intervals (`from` inclusive, `to` exclusive), so a body can change kind or section without changing identifier.

## Authority is not recorded here

Whether a body's documents bind, and how much, belongs to CMDDR, where authority attaches to the act, not to the issuer. CRCDR records what a body was and where it sat, and nothing more. It does not list the documents a body issued, and does not infer teaching weight from `kind`.

## Repository contents

- [`data/bodies.json`](data/bodies.json): the bodies, with dated names, kinds, sections and part-of relations, each fact carrying `verified`, `source_type` and a source.
- [`data/events.json`](data/events.json): the events that changed them, each tied to its act, with the operative clause where transcribed.
- [`data/kinds.json`](data/kinds.json), [`data/sections.json`](data/sections.json), [`data/event_types.json`](data/event_types.json): the controlled vocabularies.
- [`data/identifiers.json`](data/identifiers.json): generated; ids, aliases, predecessor/successor links and `mag:` references.
- [`registry/bodies.md`](registry/bodies.md) and [`registry/lineages.md`](registry/lineages.md): the human-readable registry and per-lineage tables. Generated, never hand-edited.
- [`docs/schema-proposal.md`](docs/schema-proposal.md): identity rules, data model, open questions and the Latinist review list.
- [`docs/curia-history-report.md`](docs/curia-history-report.md): the research report behind the seed.
- [`seed/`](seed/): the research files and the curated maps (keys, events, kinds, founding years) used to seed the data.
- [`scripts/`](scripts/): `crcdr.py` (shared helpers), `validate.py`, `generate_registry.py`, `seed_from_research.py` and their tests. Python 3, standard library only; run every script from the repository root with `python3 -I`.

```sh
python3 -I -m unittest discover -s scripts -v
python3 -I scripts/validate.py
python3 -I scripts/generate_registry.py
```

## Sources and verification

**The *Annuario Pontificio* is the authority for the content of this registry, and it has not been consulted**: it is not published online. The seed comes from the research in [`docs/curia-history-report.md`](docs/curia-history-report.md), with founding years researched separately. Every fact carries `verified` and `source_type` (`primary`, `official-secondary`, `secondary` or `inferred`), and seeding never upgrades either. Facts marked `verified: false` are marked † in the registry. Medieval years from secondary sources (Penitentiary 1256, Rota 1323, Revision of Councils 1849) in particular need checking.

The validator reports **errors** (inconsistencies; must be zero) and **warnings** (documented research gaps, each carrying a `gap` note, or operative clauses not yet transcribed). The warnings are documented gaps, not defects, and are listed in [`registry/bodies.md`](registry/bodies.md).

Corrections against the *Annuario* and against the acts themselves are the most useful contribution this repository can receive.

## License

- [`data/identifiers.json`](data/identifiers.json) is licensed under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). See [`LICENSE-CC0`](LICENSE-CC0).
- The rest of the data, the registry and the documentation are licensed under the [Creative Commons Attribution-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd/4.0/) (CC BY-ND 4.0). See [`LICENSE`](LICENSE).
- The source code in [`scripts/`](scripts/) is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [`scripts/LICENSE`](scripts/LICENSE).
