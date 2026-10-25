# CRCDR schema proposal (draft for committee review)

**All IDs are drafts pending committee review.** This is a draft for review by the Technical Advisory Group (**needs TAG review**: it decides how curial bodies are modelled). A canonist or historian of the Curia, and a Latinist for the keys, should review it before anything is frozen.

## Identifier scheme

```
cr:<latin-slug>-<founding-year>
```

Long form `curia-romana:`; the short form is canonical (see [CatholicOS/cdcf-uri-scheme#20](https://github.com/CatholicOS/cdcf-uri-scheme/issues/20)). The grammar is to be added to the URI scheme's Appendix D under #20; this registry cites it and keeps no copy.

```abnf
cr-key     = latin-slug HYPHEN year
latin-slug = 1*lower *(HYPHEN 1*lower)   ; no digits, so the year split is unambiguous
lower      = %x61-7A                     ; a-z only (RFC 5234 ALPHA also admits A-Z)
year       = 4DIGIT
HYPHEN     = %x2D                        ; "-"
```

Rules for forming a key:

1. **Latin.** The slug follows the Latin name, because the founding and reforming acts are in Latin and the English names are variable translations.
2. **Minted once, from the name in use when the key is minted:** the current name for a living body, the last name for one that has ended. Later renames go only into the dated `names` list. Before the first stable release a key may still be corrected, with a changelog entry; after it, keys are frozen.
3. **The distinguishing noun phrase, in the nominative.** Drop the generic kind words (*Dicasterium*, *Congregatio*, *Sacra*, *Suprema*, *Pontificium Consilium*, *Secretariatus*, *Commissio*, *Tribunal*, *Officium*, *Praefectura*, *Pontificia Academia*) and the governing preposition (*pro*, *de*). Keep the connective *et*. If dropping the kind word would leave nothing distinctive, keep it. ASCII-fold, lower-case, hyphenate.
4. **Founding year, always.** The year the founding act took effect. For a body with no founding act, the earliest securely attested year, flagged `founded.basis: "attested"`.

Examples: `cr:doctrina-fidei-1542`, `cr:cultus-divinus-1969`, `cr:cultus-divinus-1984`, `cr:paenitentiaria-apostolica-1256`, `cr:index-1571`.

## Identity rules

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
    - a part-of placement (Minors within the DDF, Migrants under Bishops, H16), which is a dated relation (see Data model).

## Data model

All dates are ISO 8601 at the precision known (`YYYY`, `YYYY-MM`, `YYYY-MM-DD`); a partial date compares as its first day. Every interval is `from` inclusive, `to` exclusive, with `to: null` meaning still open. Each dated fact carries `verified` (bool), `source_type` (`primary` | `official-secondary` | `secondary` | `inferred`), a `source`, an optional `note`, and an optional `gap` (a documented research gap, which turns a validation error into a warning). Seeding never upgrades `verified` or `source_type`; where the seeder substitutes a bound the research did not give (a start set to the founding date, an end that is only a terminus ante quem), that span is recorded `verified: false`, at most `secondary`, with a `gap`.

- **`data/bodies.json`**: `{"entries": [...]}`, one entry per body:
  - `id`;
  - `founded` (`date`, `precision`, `basis` `act`|`attested`, `act`, `event`, provenance) and `ended` (same shape, or `null`);
  - dated `names[]`: `name_la` (the Latin name, or `null` where no Latin name is attested; never reconstructed), `name_it`, `name_en`, `aliases` (`[{name, lang: "la"|"en"}]`, other attested forms of this name, such as spelling variants), `from`, `to`, `act`, provenance. Editorial text in the research's names (variants, remarks) is moved out by `seed/name_fixes.json`: variants to `aliases`, remarks to `note`;
  - dated `kind[]`;
  - dated `section[]` (`regime`, `section`; a `not-listed` entry also carries `in_curia`: `true`, `false`, or `null` with a `gap` when the research does not establish it);
  - dated `part_of[]` (`body`, `relation`, `from`, `to`);
  - `aliases` (body-level `[{name, lang}]`, dated by the body's lifespan); `note`.

  Predecessors and successors are derived from events, not stored on bodies.
- **`data/events.json`**: `{"entries": [...]}`, one entry per change, chronologically: `id`, `date` (effective date) and `date_precision`, `signed`, `act`, `mag` (the CMDDR `mag:` id, or `null`), `event_type`, `before[]`, `after[]`, `operative_clause`, `clause_status` (`transcribed` | `not-transcribed` | `silent`; `silent` requires `inferred: true`), `inferred`, provenance, and `research_id` (the research event it was seeded from; one research event may yield several, suffixed `a`, `b`, …). An event of a same-identity type (`rename`, `competence-transfer`, …) has `before == after`; for a transfer between two bodies both are listed in both sets, and the direction (from which body to which) is given in the `note`.
- **`data/identifiers.json`** (generated, CC0): `{"$comment", "license", "entries": [...]}`; each entry has `id`, `names` (`[{name, lang, from, to}]`, one per name and language, dated from the body's names), `aliases` (the same shape, for the other attested forms), `predecessors`, `successors` and `founding_act_mag`. Lookup is by (name, date): a string denotes an id only within its interval, and no (name, date) pair matches two ids (the Congregation for Divine Worship of 1969 and of 1984 share their names but not their dates).
- **Vocabularies:** `data/kinds.json` (what the act calls the body), `data/sections.json` (where the governing constitution places it, by regime, each value declaring `in_curia`), `data/event_types.json` (`foundation`, `rename`, `rename-competence`, `kind-change`, `competence-transfer`, `absorption`, `merger`, `split`, `re-foundation`, `revival`, `suppression`, `attachment`, each declaring its identity effect).
- **Part-of relations** (`within`, `subject-to`, `section-of`, `complement-of`) are dated placements and never change identity.
- **Validation** (`scripts/validate.py`): rules R1–R7 of design §7, plus R0 (every fact carrying a `gap` is a warning quoting it, unless another rule already reported that gap) and R8 (a dated fact with no `source` is a warning; no source is invented). The generated registry lists every warning under "Known gaps", and marks facts † (`verified: false`), ‡ (`gap`) and ⁱ (event `inferred: true`).
- **Authority is not recorded.** It belongs to CMDDR.

## Open questions for the committee (design section 12)

1. Lineage depth: does Consecrated Life go back to Regulars (1586), or start in 1908 (H8)? The *Annuario*'s own historical notes should decide.
2. *Seminaria clericorum* (1915): a rename of Studies, or a new body absorbing it (H11)?
3. The 2022 mergers, which *Praedicate Evangelium* never states article by article (H5).
4. Whether CMDDR's `issuerType` gains `dicastery`, or a generic `curial-body` that defers to CRCDR's dated `kind`.
5. The Latin wording of each key, which needs a Latinist's review before any key is frozen.

## Open questions from phase 1

Each item below was decided provisionally during the build, or held out. Each needs committee or TAG review before any key is frozen.

### Held out of phase 1 (no key minted)

- **Founding year not securable from sources** (`seed/founding_years.json` gives the evidence and the next source for each):
  - Apostolic Camera: 1192 is attested only through an officer (the camerarius Cencius), not the body, and is likely not the earliest attestation.
  - Secretariat of State.
  - Apostolic Briefs.
  - Briefs to Princes.
  - Apostolic Chancery.
  - Apostolic Datary.
  - Signatura Gratiae.
  - Ceremonial.
  - Papal Almonry: the 1409 bull was rejected because it was issued by Alexander V, a Pisan antipope.
- **Identity questions blocking a key:**
  - **Secretariat of State:** does it continue the *Secretaria Apostolica* founded in 1487? If so, its year comes from that founding act, and the answer also decides the two Briefs offices.
  - **`signatura-gratiae`:** which body is meant? The candidates are the referendaries' Signatura (attested 1586), the Sixtine congregation (founding act 1588), or both, as two bodies.
  - **`state-of-regulars`:** the research record conflates two bodies, one from 1652 and one from 1847 (its end date of 1906 belongs to the 1847 body).
- **Out of phase-1 scope:**
  - `sixtine-temporal-congregations`: one record stands for six bodies.
  - `fabric-st-peter`: an institution connected with the Holy See, which belongs to phase 2.

### Provisional decisions to confirm

- **Penitentiary key year 1256** (`cr:paenitentiaria-apostolica-1256`): is Pius V's 1569 suppression and reconstitution a re-foundation (identity rule 6)? If it is, the key year becomes 1569.
- **Early years to check against Del Re before freezing:** the medieval Penitentiary 1256 and Rota 1323 (`cr:rota-romana-1323`), both from secondary sources only; Visitation 1637 (`cr:visitatio-apostolica-urbis-1637`), an attested year, not a founding act; and Revision of Councils 1849 (`cr:conciliorum-revisio-1849`), from one secondary sentence.
- **Rota:** the year 1245 (Lyon I) given on vatican.va was rejected in favour of 1323, which a document supports.
- **Key years follow the effective date, not the signing date:**
  - `cr:administratio-patrimonii-sedis-apostolicae-1968`;
  - `cr:res-oeconomicae-sanctae-sedis-1968`;
  - `cr:pontificalis-domus-1968`;
  - `cr:integra-humana-progressio-fovenda-2017`;
  - and the founding date of `cr:communicatio-2015` (the Dicastery for Communication, effective 29 June 2015).
- **ev024, Bishops-and-Regulars in 1908:** recorded as suppression by omission (the default in identity rule 8). It is not recorded as a split, so Religious is *not* a successor of Bishops-and-Regulars. Whether the line of Consecrated Life goes back to Regulars (1586) is still open (H8).
- **ev030, *Dei providentis* (1917):** recorded as a re-foundation (inferred), so the Congregation for the Oriental Church succeeds the oriental section of Propaganda. The research report's H12 reads the act as "a clean suppression plus new foundation".
- **ev026, *Seminaria clericorum* (1915):** recorded as a rename of Studies (inferred). The alternative is a new body that absorbed Studies (H11).
- **Rename dates bounded by a terminus ante quem, not the actual rename date:**
  - Consistorial name: in use by 1908-11-03 (*Sapienti Consilio*).
  - Papal Household name: in use by 1989-03-01 (*Pastor Bonus*).
- **ev071:** its absorber, the Secretariat of State, is held out, so the event is recorded as an inferred suppression.
- **Latin key wording:** every `rule_note` in `seed/key_map.json` records a judgment; together they are the Latinist review list below. Notable ones: the gerundive slugs (`cr:nova-evangelizatio-promovenda-2010`, `cr:integra-humana-progressio-fovenda-2017`, `cr:codex-iuris-canonici-recognoscendus-1963`); the kind words kept for the two 2014 economic bodies (`cr:secretaria-res-oeconomica-2014`, `cr:consilium-res-oeconomica-2014`); and the slug for the *Consilium ad exsequendam Constitutionem de Sacra Liturgia* (`cr:exsequenda-constitutio-de-sacra-liturgia-1964`).

## Latinist review list

Generated from the `rule_note` of each entry in `seed/key_map.json` (64 entries). `minted_from_la` is the Latin name the slug was derived from.

| id | minted_from_la | rule_note |
|---|---|---|
| `cr:doctrina-fidei-1542` | Dicasterium pro Doctrina Fidei | Regular: 'Dicasterium' and 'pro' dropped; 'Doctrina Fidei' already nominative. Design example. Research name note: the Latin of PE was not checked (English text read). Year 1542 from Licet ab initio as recited in Integrae servandae; the Catholic Encyclopedia dates the congregation (as opposed to the tribunal) to 1558 (research erected.note) — a year question for review before freezing. |
| `cr:index-1571` | Sacra Congregatio Indicis | Kind words 'Sacra Congregatio' dropped; nominative reconstructed from the genitive 'Indicis' -> 'Index'. Founding year 1571 is secondary (Catholic Encyclopedia; act not identified). |
| `cr:ecclesia-dei-1988` | Pontificia Commissio «Ecclesia Dei» | 'Pontificia Commissio' dropped as a kind phrase by analogy with 'Pontificia Academia' (the list names only 'Commissio'); guillemets dropped; 'Ecclesia Dei' is already nominative (the incipit of Ecclesia Dei adflicta). |
| `cr:tutela-minorum-2014` | Pontificia Commissio pro Tutela Minorum | 'Pontificia Commissio' and 'pro' dropped; nominative 'Tutela Minorum' (ablative Tutela -> nominative, same spelling). The Latin name is secondary (research name verified: false); the 2014 chirograph was not read. |
| `cr:gentium-evangelizatio-1622` | Congregatio pro Gentium Evangelizatione | Ended 2022: minted from the last name (PB heading as rendered by vatican.va). 'Congregatio' and 'pro' dropped; nominative reconstructed 'Evangelizatione' -> 'Evangelizatio'; source word order kept ('Gentium Evangelizatio'). The common name 'Propaganda Fide' (1622-1968, and the 1968 suffix 'seu de Propaganda Fide') is not used: rule 2 mints from the last name. Whether 'seu de Propaganda Fide' survived in the official name is open (research: Annuario needed). |
| `cr:nova-evangelizatio-promovenda-2010` | Pontificium Consilium ad Novam Evangelizationem Promovendam | 'Pontificium Consilium' dropped; governing 'ad' dropped by analogy with pro/de; nominative reconstructed for the whole phrase including the gerundive ('Novam Evangelizationem Promovendam' -> 'Nova Evangelizatio Promovenda'). Alternative for the Latinist: drop the gerundive ('nova-evangelizatio'). The Latin was taken from a search extract (research: act not read in full). |
| `cr:evangelizatio-2022` | Dicasterium pro Evangelizatione | 'Dicasterium' and 'pro' dropped; nominative reconstructed 'Evangelizatione' -> 'Evangelizatio'. Distinct from cr:gentium-evangelizatio-1622 (a predecessor in the 2022 merger). The Latin title of PE was not checked by the research (English read). |
| `cr:negotia-ritus-orientalis-1862` | Sacra Congregatio de Propaganda Fide pro negotiis ritus orientalis | 'Sacra Congregatio' and the governing 'pro' dropped; the element 'de Propaganda Fide' is also dropped because it names the parent congregation, not this body (judgment); nominative reconstructed 'negotiis' -> 'negotia'. Name as in Dei providentis (research, primary). Sapienti consilio 6° n.6 has the plural 'Congregationem pro Negotiis rituum orientalium' (-> 'negotia-rituum-orientalium'); the singular of the later act was chosen. Founding year 1862 is secondary. |
| `cr:ecclesiae-orientales-1917` | Dicasterium pro Ecclesiis Orientalibus | 'Dicasterium' and 'pro' dropped; nominative plural reconstructed 'Ecclesiis Orientalibus' -> 'Ecclesiae Orientales'. Research: the Latin title in PE was not checked ('presumably' unchanged; English 'Eastern' translates 'Orientalibus', H18). |
| `cr:ritus-1588` | Sacra Congregatio Rituum | Ended 1969: last name. Research name_la holds two variants ('Sacra Congregatio Rituum / Congregatio sacrorum Rituum'); chose 'Sacra Congregatio Rituum', the form of REU n.58, the last governing act to name it. 'Sacra Congregatio' dropped; nominative plural reconstructed 'Rituum' -> 'Ritus' (4th declension). With the other variant the slug would be 'sacri-ritus'. |
| `cr:cultus-divinus-1969` | Sacra Congregatio pro Cultu Divino | Regular: 'Sacra Congregatio' and 'pro' dropped; nominative 'Cultus Divinus'. Design example (H6): same slug as cr:cultus-divinus-1984, distinguished by the founding year. |
| `cr:exsequenda-constitutio-de-sacra-liturgia-1964` | Consilium ad exsequendam Constitutionem de Sacra Liturgia | 'Consilium' dropped as a kind word (Latin term of kinds.json 'council'; not in the design's list); governing 'ad' dropped; nominative reconstructed for the rest in source order ('exsequendam Constitutionem' -> 'exsequenda Constitutio'). The inner 'de' is kept: it belongs to the title of the conciliar constitution, not to the body's name; 'Sacra' here is part of 'Sacra Liturgia', not the kind word. Flag: without the kind word the slug reads like a document; the Latinist may prefer keeping 'consilium'. Latin name and founding year 1964 are secondary (research: Sacram Liturgiam, secondary). |
| `cr:causae-sanctorum-1969` | Dicasterium de Causis Sanctorum | 'Dicasterium' and 'de' dropped; nominative plural reconstructed 'Causis' -> 'Causae'. Research: PE Latin form not checked. |
| `cr:disciplina-sacramentorum-1908` | Sacra Congregatio de disciplina Sacramentorum | Ended 1975: last (only) name. 'Sacra Congregatio' and 'de' dropped; 'disciplina Sacramentorum' nominative (ablative disciplina -> nominative, same spelling). |
| `cr:sacramenta-et-cultus-divinus-1975` | Sacra Congregatio pro Sacramentis et Cultu Divino | Ended 1984: research name (as in Quoniam in celeri, 1984). 'Sacra Congregatio' and 'pro' dropped; nominative reconstructed 'Sacramentis et Cultu Divino' -> 'Sacramenta et Cultus Divinus'; 'et' kept. Flag: the founding act Constans nobis n.2 reads 'pro Sacramentis divinoque Cultu' (research name note); minting from that form would give 'sacramenta-divinusque-cultus'. The research name_la was used. |
| `cr:sacramenta-1984` | Sacra Congregatio pro Sacramentis | Ended 1989: last name. 'Sacra Congregatio' and 'pro' dropped; nominative plural reconstructed 'Sacramentis' -> 'Sacramenta'. Distinct from cr:disciplina-sacramentorum-1908 (H6/H7). |
| `cr:cultus-divinus-1984` | Sacra Congregatio pro Cultu Divino | Regular: 'Sacra Congregatio' and 'pro' dropped. Design example (H6): same name as the 1969-1975 body, different body, different year. |
| `cr:cultus-divinus-et-disciplina-sacramentorum-1989` | Dicasterium de Cultu Divino et Disciplina Sacramentorum | 'Dicasterium' and 'de' dropped; nominative reconstructed 'Cultu Divino et Disciplina' -> 'Cultus Divinus et Disciplina'; 'et' kept. Year 1989 = PB's entry into force (research erected.date 1989-03-01), not the research key's 1988 (PB signing). The merger founding it is inferred (research: no merger clause found). Research: PE Latin not checked. |
| `cr:clerici-1564` | Dicasterium pro Clericis | 'Dicasterium' and 'pro' dropped; nominative plural reconstructed 'Clericis' -> 'Clerici'. Rule 2 mints from the current name, so the 1564-1968 name (Congregatio Concilii) leaves no trace in the key. Research: PE Latin not checked; founding date 1564-08-02 secondary (the incipit 'Alias nos nonnullas' is unverified). |
| `cr:lauretana-1698` | Congregatio Lauretana | Ended 1908: last (only) name. 'Congregatio' dropped; what remains is the adjective 'Lauretana' (feminine, agreeing with the dropped 'Congregatio'), kept as distinctive. Alternative: keep the kind word ('congregatio-lauretana'). Founding year 1698 secondary. |
| `cr:conciliorum-revisio-1849` | Congregatio specialis pro Conciliorum revisione | Ended 1908. 'Congregatio', the qualifying adjective 'specialis' and 'pro' dropped; nominative reconstructed 'revisione' -> 'revisio'; source word order kept. The name matches Sapienti consilio's 'Congregatione speciali ... pro Conciliorum revisione'. Year 1849 from seed/founding_years.json: weak (one secondary sentence, 'had consultors from 1849'; verify against Del Re before freezing). |
| `cr:episcopi-1588` | Dicasterium pro Episcopis | 'Dicasterium' and 'pro' dropped; nominative plural reconstructed 'Episcopis' -> 'Episcopi'. H18 name trap: this is the Consistorial line (1588), not the Sixtine congregation for consultations of bishops (cr:consultationes-episcoporum-et-aliorum-praelatorum-1588). Research: PE Latin not checked; Immensa itself not read (date via Sapienti consilio's recital). |
| `cr:consultationes-episcoporum-et-aliorum-praelatorum-1588` | Congregatio pro consultationibus Episcoporum et aliorum praelatorum | Ended 1601. 'Congregatio' and 'pro' dropped; nominative plural reconstructed 'consultationibus' -> 'consultationes'; the genitive complement kept as is; 'et' kept. Long, but no rule allows shortening. Latin title is secondary (Catholic Encyclopedia / Wikipedia). |
| `cr:consultationes-regularium-1586` | Congregatio super consultationibus regularium | Ended 1601. 'Congregatio' dropped; governing 'super' dropped by analogy with pro/de; nominative plural reconstructed 'consultationibus' -> 'consultationes'. Latin title and date secondary. |
| `cr:episcopi-et-regulares-1601` | Sacra Congregatio Episcoporum et Regularium | Ended 1908. 'Sacra Congregatio' dropped; nominative reconstructed from the genitives 'Episcoporum et Regularium' -> 'Episcopi et Regulares'; 'et' kept. Founding year 1601 secondary. |
| `cr:disciplina-regularis-1695` | Congregatio super disciplina Regulari | Ended 1906. 'Congregatio' and governing 'super' dropped; nominative reconstructed 'disciplina Regulari' -> 'disciplina regularis'. Latin and date secondary. |
| `cr:instituta-vitae-consecratae-et-societates-vitae-apostolicae-1908` | Dicasterium pro Institutis Vitae Consecratae et Societatibus Vitae Apostolicae | 'Dicasterium' and 'pro' dropped; nominative plural reconstructed 'Institutis ... et Societatibus' -> 'Instituta ... et Societates'; genitives kept; 'et' kept. Long, but no rule allows shortening. Research: PE Latin not checked. H8: the key starts the line in 1908 (new body), not with the 1586 Regulars congregation. |
| `cr:universitas-studii-romani-1588` | Congregatio pro universitate studii Romani | Ended 1824. 'Congregatio' and 'pro' dropped; nominative reconstructed 'universitate' -> 'universitas'; genitive 'studii Romani' kept. Latin title secondary. |
| `cr:seminaria-atque-studiorum-instituta-1824` | Congregatio de Seminariis atque Studiorum Institutis | Ended 2022: last name. Research name_la holds two variants ('Congregatio de Seminariis atque Studiorum Institutis / de Institutione Catholica'); chose the PB Latin heading on vatican.va (the governing act's form). 'Congregatio' and 'de' dropped; nominative plural reconstructed 'Seminariis ... Institutis' -> 'Seminaria ... Instituta'; connective 'atque' kept like 'et'. With the other variant (the REU name, common usage 'Catholic Education') the slug would be 'institutio-catholica'. Research: official form needs the Annuario. Founding 1824 secondary; H11 identity (1915) modelled as continuity. |
| `cr:cultura-1982` | Pontificium Consilium de Cultura | Ended 2022: last name (PB). 'Pontificium Consilium' and 'de' dropped; nominative 'Cultura'. The founding name 'pro hominum Cultura' (1982) would give 'hominum-cultura'. H5: the 1993 union with Non-Believers is modelled as absorption, so this body keeps its key. |
| `cr:dialogus-cum-non-credentibus-1965` | Pontificium Consilium pro Dialogo cum Non Credentibus | Ended 1993: last name. 'Pontificium Consilium' and 'pro' dropped; nominative reconstructed 'Dialogo' -> 'Dialogus'; the inner 'cum Non Credentibus' is kept (it governs the complement of 'Dialogus', not of the kind word). The founding name 'Secretariatus pro non credentibus' would give 'non-credentes'. Founding date secondary. |
| `cr:bona-culturalia-ecclesiae-1989` | Pontificia Commissio de Bonis Culturalibus Ecclesiae | Ended 2012: last name. 'Pontificia Commissio' (by analogy with 'Pontificia Academia') and 'de' dropped; nominative plural reconstructed 'Bonis Culturalibus' -> 'Bona Culturalia'; genitive 'Ecclesiae' kept. Latin from the title of Pulchritudinis fidei (research). |
| `cr:cultura-et-educatio-2022` | Dicasterium de Cultura et Educatione | 'Dicasterium' and 'de' dropped; nominative reconstructed 'Educatione' -> 'Educatio'; 'et' kept. Research: PE Latin not checked. |
| `cr:unitas-christianorum-fovenda-1960` | Dicasterium ad Unitatem Christianorum Fovendam | 'Dicasterium' dropped; governing 'ad' dropped by analogy with pro/de; nominative reconstructed including the gerundive ('Unitatem ... Fovendam' -> 'Unitas ... Fovenda'). Alternative for the Latinist: drop the gerundive ('unitas-christianorum'). Research: PE Latin not checked. The 1960 founding act names it only 'peculiaris Coetus seu Secretariatus'. |
| `cr:dialogus-interreligiosus-1964` | Dicasterium pro Dialogo Interreligioso | 'Dicasterium' and 'pro' dropped; nominative reconstructed 'Dialogo Interreligioso' -> 'Dialogus Interreligiosus'. Research: PE Latin not checked. |
| `cr:laici-1967` | Pontificium Consilium pro Laicis | Ended 2016: last name. 'Pontificium Consilium' and 'pro' dropped; nominative plural reconstructed 'Laicis' -> 'Laici'. |
| `cr:familia-1973` | Consilium de Familia | Ended 1981. Research name_la holds two forms ('Consilium de Familia (Comitatus pro Familia)'); chose 'Consilium de Familia', the form of Familia a Deo instituta (the act read, which ends it). 'Consilium' dropped as a kind word (kinds.json 'council'); 'de' dropped; 'Familia' nominative. Same slug as cr:familia-1981 (its re-foundation successor, H17), distinguished by year as in H6. |
| `cr:familia-1981` | Pontificium Consilium pro Familia | Ended 2016. 'Pontificium Consilium' and 'pro' dropped; 'Familia' nominative. Same slug as cr:familia-1973 (H17 re-foundation), distinguished by year. |
| `cr:laici-familia-et-vita-2016` | Dicasterium pro Laicis, Familia et Vita | 'Dicasterium' and 'pro' dropped; nominative reconstructed 'Laicis, Familia et Vita' -> 'Laici, Familia et Vita'; comma dropped; 'et' kept. founded_date: Sedula Mater signed 15 Aug 2016 (research erected.date), effective 1 Sep 2016 (research names[0].from and event ev097); same year either way. |
| `cr:iustitia-et-pax-1967` | Pontificium Consilium de Iustitia et Pace | Ended 2017: last name. 'Pontificium Consilium' and 'de' dropped; nominative reconstructed 'Iustitia et Pace' -> 'Iustitia et Pax'; 'et' kept. |
| `cr:cor-unum-1971` | Pontificium Consilium «Cor Unum» | Ended 2017. Research name_la is the full 1971 title 'Pontificium Consilium «Cor Unum» de humana et christiana progressione fovenda'; chose the short form 'Pontificium Consilium «Cor Unum»' used by PB (research name note), the last governing act. 'Pontificium Consilium' and guillemets dropped; 'Cor Unum' nominative. With the full title the slug would be 'cor-unum-humana-et-christiana-progressio-fovenda'. |
| `cr:spiritualis-migrantium-atque-itinerantium-cura-1970` | Pontificium Consilium de Spirituali Migrantium atque Itinerantium Cura | Ended 2017: last name. 'Pontificium Consilium' and 'de' dropped; nominative reconstructed 'Spirituali ... Cura' -> 'Spiritualis ... Cura'; source word order kept; 'atque' kept like 'et'. Long, but no rule allows shortening. |
| `cr:apostolatus-pro-valetudinis-administris-1985` | Pontificium Consilium de Apostolatu pro Valetudinis Administris | Ended 2017: last name. 'Pontificium Consilium' and the governing 'de' dropped; nominative reconstructed 'Apostolatu' -> 'Apostolatus'. The inner 'pro Valetudinis Administris' is kept: that 'pro' governs the complement of 'Apostolatus', not of the kind word, so it is not 'the governing preposition'. Flag for the Latinist: the alternative reading drops it too. |
| `cr:integra-humana-progressio-fovenda-2017` | Dicasterium pro Integra Humana Progressione Fovenda | 'Dicasterium' and 'pro' dropped; nominative reconstructed including the gerundive ('Integra Humana Progressione Fovenda' -> 'Integra Humana Progressio Fovenda'). Alternative: drop the gerundive. The research marks this Latin 'unverified' (Italian/Spanish titles say 'servizio dello sviluppo'); it is a reconstruction to be checked. YEAR FLAG: research erected.date is 2016-08-17 (Humanam progressionem signed); the act took effect 2017-01-01 (research names[0].from, kind and event ev099), and the effective year governs (design §4 rule 4). This deviates from 'year of research erected.date'. |
| `cr:codicis-canones-authentice-interpretandi-1917` | Pontificia Commissio ad Codicis canones authentice interpretandos | Ended 1984. 'Pontificia Commissio' and governing 'ad' dropped; nominative reconstructed for the rest including the gerundive and adverb, in source order ('Codicis canones authentice interpretandos' -> 'Codicis canones authentice interpretandi'). The gerundive is the distinguishing element here (interpretation vs revision), which is why gerundives are kept throughout. Title from the AAS 9-I index. |
| `cr:codex-iuris-canonici-recognoscendus-1963` | Pontificia Commissio Codici Iuris Canonici Recognoscendo | Ended 1983. 'Pontificia Commissio' dropped; nominative reconstructed from the dative gerundive phrase ('Codici Iuris Canonici Recognoscendo' -> 'Codex Iuris Canonici Recognoscendus'). The gerundive is kept: without it the slug would name the Code itself. Latin title and dates secondary. |
| `cr:legum-textus-1984` | Dicasterium de Legum Textibus | 'Dicasterium' and 'de' dropped; nominative plural reconstructed 'Textibus' -> 'Textus'; source word order kept ('Legum Textus'). Research: PE Latin not checked. H15: new body in 1984 (re-foundation by imitation of the 1917 commission). |
| `cr:communicationes-sociales-1948` | Pontificium Consilium de Communicationibus Socialibus | Ended 2016: last name. 'Pontificium Consilium' and 'de' dropped; nominative plural reconstructed 'Communicationibus Socialibus' -> 'Communicationes Sociales'. Founding year 1948 secondary (the 1948 Latin name is unknown). Distinct from cr:communicatio-2015, which absorbed it. |
| `cr:communicatio-2015` | Dicasterium pro Communicatione | 'Dicasterium' and 'pro' dropped; nominative reconstructed 'Communicatione' -> 'Communicatio'. The Latin of the 2018 rescript was not read (research: press-office summary); the 2015 name 'Secretaria pro Communicatione' is replaced in the key by the current name per rule 2. Year 2015: instituted 27 Jun, functioning from 29 Jun 2015 (same year). founded_date (Task 6): the research states the act was operative from 29 Jun 2015 (names[0].note 'functioning from 29 Jun 2015 (Art. 4)'; event ev095 note 'Operative 29 Jun 2015'), so the effective date governs (design §5 rule 9). |
| `cr:publica-ecclesiae-negotia-1793` | Sacrum Consilium pro Publicis Ecclesiae negotiis | Ended 1989: last name (REU n.26). 'Sacrum Consilium' dropped as a kind phrase (by analogy with 'Sacra' and with kinds.json 'council' = 'Consilium'); 'pro' dropped; nominative plural reconstructed 'Publicis ... negotiis' -> 'Publica ... Negotia'; source word order kept. IDENTITY FLAG: research (Catholic Encyclopedia) says the body was created 1793, lapsed 1809 and was re-established 1814; under design §5 rule 6 the 1814 re-establishment could be a re-foundation (new key, -1814). The research models one body from 1793; kept, pending review. Founding year 1793 secondary. |
| `cr:administratio-patrimonii-sedis-apostolicae-1968` | Administratio Patrimonii Sedis Apostolicae | No kind word to strip ('Administratio' is the distinctive head noun, kind 'office'); already nominative. YEAR FLAG: research erected.date 1967-08-15 is REU's signing date; REU took effect 1968-01-01 (research names[0].from, kind and event ev052), and the effective year governs (design §4 rule 4; research method §1: 'from' = date the act took effect). Deviates from 'year of research erected.date' (would be -1967). |
| `cr:res-oeconomicae-sanctae-sedis-1968` | Praefectura rerum oeconomicarum Sanctae Sedis | Ended 2016. 'Praefectura' dropped; nominative plural reconstructed from the genitive 'rerum oeconomicarum' -> 'res oeconomicae'; genitive 'Sanctae Sedis' kept. YEAR FLAG as for APSA: signed 1967-08-15, effective 1968-01-01; the effective year is used. |
| `cr:secretaria-res-oeconomica-2014` | Secretaria pro Re Oeconomica | Kind word KEPT: dropping 'Secretaria' leaves 'res-oeconomica', which is identical to what remains of the Council for the Economy, founded by the same act in the same year (design §4 rule 3, 'keep it if nothing distinctive would remain'). 'pro' dropped; nominative reconstructed 'Re Oeconomica' -> 'Res Oeconomica'. Flag for the Latinist: alternatives 'secretaria-pro-re-oeconomica' (literal) or 'secretaria-rei-oeconomicae' (genitive, like 'secretaria-status'). |
| `cr:consilium-res-oeconomica-2014` | Consilium pro Re Oeconomica | Kind word KEPT, for the same collision reason as cr:secretaria-res-oeconomica-2014 (same act, same year). 'pro' dropped; nominative reconstructed. Flag: alternatives 'consilium-pro-re-oeconomica' or 'consilium-rei-oeconomicae'. |
| `cr:revisor-generalis-2014` | Revisor Generalis | Research name_la is 'Revisor Generalis (Officium)', i.e. the officeholder's title with the kind word in parentheses; the office's own Latin name (presumably 'Officium Revisoris Generalis') was not verified by the research. 'Officium' dropped; 'Revisor Generalis' nominative. The slug names the officeholder, as PE does for the Camerlengo (H13); flag for the Latinist. |
| `cr:donationes-pro-sancta-sede-2025` | Commissio de donationibus pro Sancta Sede | Ended 2025. 'Commissio' and the governing 'de' dropped; nominative plural reconstructed 'donationibus' -> 'donationes'; the inner 'pro Sancta Sede' is kept (it governs a complement of 'donationes'). The Latin is the research's rendering of an Italian-language chirograph title (official-secondary); unverified. |
| `cr:paenitentiaria-apostolica-1256` | Sacra Paenitentiaria (Poenitentiaria) Apostolica | Research name_la holds spelling variants; chose 'Paenitentiaria' (the design's example spelling) over 'Poenitentiaria'. 'Sacra' dropped; 'Paenitentiaria' is itself the kind-like head noun and is kept, as in the design example. Year 1256 from seed/founding_years.json (attested, secondary; R12: whether Pius V's 1569 act is a re-foundation is on the review list). |
| `cr:rota-romana-1323` | Tribunal Rotae Romanae | 'Tribunal' dropped; nominative reconstructed from the genitive 'Rotae Romanae' -> 'Rota Romana'. Year 1323 from seed/founding_years.json (attested, secondary). H10: the 1908 revival keeps the key. |
| `cr:signatura-apostolica-1908` | Supremum Signaturae Apostolicae Tribunal | Research name_la holds two forms ('Signatura Apostolica / Supremum Signaturae Apostolicae Tribunal'); both give the same slug. Minted from the PB form: 'Supremum' dropped (by analogy with 'Suprema') and 'Tribunal' dropped; nominative reconstructed from the genitive 'Signaturae Apostolicae'. H10: re-founded 1908, so the key starts in 1908. |
| `cr:pontificalis-domus-1968` | Praefectura Pontificalis Domus | Living: minted from the current name (research: name verified in PB 1988; date of the rename from 'Apostolici Palatii Praefectura' not located). 'Praefectura' dropped; 'Pontificalis Domus' is nominative (genitive and nominative coincide for both words). YEAR FLAG as for APSA: signed 1967-08-15, effective 1968-01-01; the effective year is used. |
| `cr:liturgicae-celebrationes-summi-pontificis-1989` | Officium de Liturgicis Celebrationibus Summi Pontificis | 'Officium' and 'de' dropped; nominative plural reconstructed 'Liturgicis Celebrationibus' -> 'Liturgicae Celebrationes'; genitive 'Summi Pontificis' kept. Founding by PB in 1989 is inferred by the research (antecedents not traced). |
| `cr:visitatio-apostolica-urbis-1637` | Congregatio Visitationis Apostolicae Urbis | Ended 1908. 'Congregatio' dropped; nominative reconstructed from the genitive 'Visitationis Apostolicae' -> 'Visitatio Apostolica'; 'Urbis' kept. Year 1637 from seed/founding_years.json (attested, primary). |
| `cr:indulgentiae-et-sacrae-reliquiae-1669` | Congregatio Indulgentiarum et Sacrarum Reliquiarum | Ended 1904. 'Congregatio' dropped; nominative plural reconstructed from the genitives -> 'Indulgentiae et Sacrae Reliquiae'; 'Sacrae' kept (it qualifies the relics, not the kind word); 'et' kept. Latin and date secondary. |
| `cr:america-latina-1958` | Pontificia Commissio pro America Latina | 'Pontificia Commissio' (by analogy with 'Pontificia Academia') and 'pro' dropped; 'America Latina' nominative (ablative, same spelling). Founding date and Latin are secondary. |
