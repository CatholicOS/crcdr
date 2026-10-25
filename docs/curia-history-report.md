# Roman Curia, 1588–2026: institutional history as raw material for a curial-body registry

Companion to `bodies.json` (76 bodies) and `events.json` (121 events, 82 checked against the act's own text). Every key is a provisional working key (`provisional_key: true`), not a proposed identifier.

Source types: **primary** (the act's text, either the AAS PDF or the act's own vatican.va page) · **official-secondary** (a vatican.va or press-office page about the act) · **secondary** (Catholic Encyclopedia 1912, Wikipedia, BnF, Catholic-Hierarchy, news) · **inferred** (deduced from the structure of an act that does not state the fact).

## 1. Method and how far to trust each fact

- **Acts read in full (primary):**
  - *Sapienti consilio*, AAS 1 (1909) 7–19.
  - The 1917 Code, cann. 242–264.
  - The 1915–17 acts of Benedict XV: *Seminaria clericorum*, AAS 7 (1915) 493–495; *Alloquentes proxime*, AAS 9-I (1917) 167; *Dei providentis*, AAS 9-I (1917) 529–531.
  - The Vatican II era acts: *Superno Dei nutu*, AAS 52 (1960) 433–437; *In fructibus multis*, AAS 56 (1964) 289–292; *Progrediente Concilio*, AAS 56 (1964) 560; *Integrae servandae*, AAS 57 (1965) 952–955; *Finis Concilio*, AAS 58 (1966) 37–40; *Catholicam Christi Ecclesiam*, AAS 59 (1967) 25–28.
  - *Regimini Ecclesiae universae* (REU), Latin text, read in full.
  - The 1969–1985 acts: *Sacra Rituum Congregatio*, AAS 61 (1969); *Apostolicae caritatis*, AAS 62 (1970); *Quo aptius*, AAS 65 (1973) 113–116; *Constans nobis*, AAS 67 (1975) 417–420; *Apostolatus peragendi* and *Iustitiam et pacem*, AAS 68 (1976); *Familia a Deo instituta*, AAS 73 (1981) 441ff; *Recognito*, AAS 76 (1984) 433–434; *Quoniam in celeri*, AAS 76 (1984) 494–495; *Dolentium hominum*, AAS 77 (1985).
  - *Pastor bonus* (PB), English and Latin, on vatican.va; *Inde a Pontificatus*.
  - The Francis-era acts: *Fidelis dispensator et prudens*; *L'attuale contesto comunicativo*; *Sedula Mater*; *Humanam progressionem*; *Praedicate Evangelium* (PE), English.
  - Leo XIV's chirograph of 29 Sep 2025.
- **Identified only from AAS indexes (date and title, contents not read):** the 1930 historical section; *Sancta Dei Ecclesia* (1938); *Amoris officio* (1971); the 1982 letter founding the Council for Culture.
- **Official-secondary:** *Ubicumque et semper*, *Pulchritudinis fidei*, *Ministrorum institutio*, *Fides per doctrinam*, the 2019 motu proprio on Ecclesia Dei, the 2018 rescript, and the Propaganda profile on vatican.va.
- **Not consulted:** the *Annuario Pontificio*, the *Bullarium Romanum*, and Del Re's *La Curia Romana*.
- **Date convention:** a body's "from" date is the date the act took effect. The signing date is recorded in the act string.

## 2. Reform milestones

1. ***Immensa aeterni Dei* (Sixtus V), 22 Jan 1588.**
   - *Sapienti consilio* recites it as "xxii Ianuarii MDLXXXVII", which is 1587 in the Incarnation-style year and 1588 in modern reckoning. The Catholic Encyclopedia gives 11 Feb 1588.
   - It set up 15 congregations. Six governed the Papal States: Annona, Fleet, Sgravio, Roads-Bridges-Waters, Vatican Press and Consulta.
   - The other nine were church bodies: Inquisition, Signatura gratiae, Consistorial provisions, Rites and Ceremonies, Index, Council, Regulars, Bishops, and Roman University.
   - This list of the 15 is from secondary sources.
2. ***Sapienti consilio* (Pius X), 29 Jun 1908, in force 3 Nov 1908.**
   - It declares a closed list: only the bodies it names make up the Curia.
   - **11 congregations:**
     - Holy Office (Pope as prefect).
     - Consistorial (Pope as prefect).
     - Discipline of the Sacraments (new).
     - Council.
     - Religious (new).
     - Propaganda.
     - Index.
     - Rites.
     - Ceremonial.
     - Extraordinary Ecclesiastical Affairs.
     - Studies.
   - **3 tribunals:** Penitentiary; Rota (revived); Signatura (re-instituted).
   - **5 offices:** Chancery; Datary; Camera; Secretariat of State (in three parts); Briefs to Princes and Latin Letters.
   - **Suppressed by name:** the Visitation of Rome, the special congregation for the revision of councils, and the old Signatures of Grace and Justice.
   - **United to the Council:** the Congregation of Loreto (Lauretana).
   - **Dropped by omission from the closed list:** Bishops-and-Regulars.
3. **Benedict XV:**
   - *Seminaria clericorum* (4 Nov 1915) created the Congregation of Seminaries and Universities.
   - *Alloquentes proxime* (25 Mar 1917) ended the Index and moved indulgences to the Penitentiary.
   - *Dei providentis* (1 May 1917) created the Congregation for the Oriental Church as a body separate from Propaganda, effective 1 Dec 1917.
   - *Cum iuris canonici* (15 Sep 1917) created the commission for interpreting the Code.
4. **1917 Code, cann. 242–264:** 11 congregations (Index removed; Seminaries-and-Universities and the Oriental Church added), 3 tribunals, 5 offices.
5. **Vatican II bodies:**
   - The Secretariat for Christian Unity (1960) was founded as a body to prepare the Council.
   - The Secretariat for Non-Christians was founded in 1964.
   - The Social Communications body was renamed and given wider competence in 1964.
   - The Secretariat for Non-Believers was founded in 1965.
   - The Liturgy *Consilium* was founded in 1964.
   - *Finis Concilio* (3 Jan 1966) confirmed the secretariats as permanent.
6. ***Integrae servandae*, 7 Dec 1965:** the Holy Office became the CDF, with its name and its procedure (*ordo*) changed together.
7. **REU, 15 Aug 1967, in force 1 Jan 1968.**
   - **Renames:** Consistorial → for Bishops; Council → for the Clergy; Oriental Church → Oriental Churches; Religious → Religious and Secular Institutes; Seminaries-and-Universities → Catholic Education; Propaganda → Evangelization of Peoples; Extraordinary Affairs → *Sacrum Consilium pro Publicis Ecclesiae negotiis*.
   - **New:** the Laity council and Justice and Peace (both January 1967), APSA, the Prefecture for Economic Affairs, the Statistics Office, and the Prefecture of the Apostolic Palace.
   - **Not named:** the Datary and Ceremonial; the preamble says only "quibusdam suppressis".
8. **Rites split, 8 May 1969:** two new congregations, Divine Worship and Causes of Saints.
9. **Worship and Sacraments:** merged in 1975, split in 1984, merged again by PB in 1988/89.
10. **PB, 28 Jun 1988, in force 1 Mar 1989:**
    - It lists 9 congregations, 3 tribunals, 12 pontifical councils and 3 offices; the dicasteries are "juridically equal" (Art. 2).
    - The former secretariats and commissions became "Pontifical Councils".
    - The Council for Public Affairs became the 2nd Section of the Secretariat of State.
    - "Sacra" is dropped from the names.
11. **Between PB and PE:**
    - 1993: Culture absorbed Non-Believers.
    - 2010: New Evangelization founded.
    - 2012: Cultural Heritage absorbed into Culture.
    - 2013: competence transfers (seminaries to Clergy, catechesis to New Evangelization).
    - 2014: the economic bodies created.
    - 2015 and 2018: Secretariat for Communication founded, then renamed a dicastery.
    - 2016: Laity, Family and Life.
    - 2016/17: Integral Human Development.
    - 2019: Ecclesia Dei suppressed.
12. **PE, 19 Mar 2022, in force 5 Jun 2022:**
    - PB is abrogated, and PB bodies that PE does not provide for are abolished (Art. 250 §3).
    - The Curia is now the Secretariat of State, 16 dicasteries and other institutions, all "juridically equal" (Art. 12).
    - Evangelization (Art. 53–54, presided by the Pope) and Culture and Education (Art. 153 §2) are mergers.
    - The Almonry becomes the Dicastery for the Service of Charity (Art. 79).
    - The Commission for the Protection of Minors is placed within the DDF (Art. 78); the Biblical and Theological Commissions are placed within it too (Art. 77).
13. **2025–2026:**
    - The Commission for Donations was created on 11 Feb 2025. Leo XIV suppressed it with a chirograph dated 29 Sep 2025, effective 4 Dec 2025.
    - The new General Regulation of the Roman Curia was signed on 23 Nov 2025. It is known only from a news report, which describes no structural change.
    - No change to the list of 16 dicasteries was found through October 2026. This is a negative search result, not checked against AAS 2025–26.

## 3. The current dicasteries traced to their origins

Key: → rename · ⊕ merger · ⊘ split · ⊃ absorption.

- **Evangelization:** Propaganda (1622) → Evangelization of Peoples (1968). Merged in 2022 with New Evangelization (2010) to form a new body. The merger is inferred from the structure of PE; no article names the merged bodies.
- **Doctrine of the Faith:** Inquisition (1542) → Holy Office (1908) ⊃ Index (1917) → CDF (1965) ⊃ Ecclesia Dei (2019) → DDF (2022).
- **Service of Charity:** medieval papal almoner → office holder renamed *Eleemosynarius Sanctitatis Suae* (1968) → an institution connected with the Holy See under PB (outside the Curia) → dicastery (2022).
- **Eastern Churches:** Oriental-rite congregation within Propaganda (1862) ⊘ new Congregation for the Oriental Church (1 Dec 1917) → Oriental Churches (1968) → dicastery (2022).
- **Divine Worship and the Discipline of the Sacraments:** Rites (1588) ⊘ Divine Worship (1969); Sacraments (1908); merged 1975; split 1984; merged 1988/89 (inferred); dicastery 2022.
- **Causes of Saints:** Rites (1588) ⊘ Causes of Saints (1969) → dicastery (2022).
- **Bishops:** Consistorial provisions (1588) → Consistorial → for Bishops (1968) → dicastery (2022).
- **Clergy:** Council (1564) ⊃ Lauretana and Revision of Councils (1908) → Clergy (1968) → dicastery (2022).
- **Consecrated Life:** Regulars (1586) ⊕ Bishops (1588) form Bishops-and-Regulars (1601), which in 1908 ⊘ a new Congregation of Religious → renamed 1968 and 1989 → dicastery (2022).
- **Laity, Family and Life:** Laity council (1967) → Pontifical Council (1976). Family committee (1973) is succeeded by a new Family council (1981). The two councils merged in 2016.
- **Christian Unity:** Secretariat (1960), made permanent (1966) → Pontifical Council (1989) → dicastery (2022).
- **Interreligious Dialogue:** Secretariat for Non-Christians (1964) → Pontifical Council (1989) → dicastery (2022).
- **Culture and Education:**
  - The Culture line: founded 1982; merged with Non-Believers in 1993, keeping its own name; absorbed Cultural Heritage in 2012.
  - The Education line: Roman University (1588) → Studies (1824) → Seminaries and Universities (1915) → Catholic Education (1968).
  - The two lines merged in 2022.
- **Integral Human Development:** Justice and Peace (1967), Migrants (1970), Cor Unum (1971) and Health (1985) merged into a new dicastery (2017).
- **Legislative Texts:** the 1917 interpretation commission and the 1963 revision commission are followed by a new commission (1984) → Pontifical Council (1989) → renamed 1999 (unverified) → dicastery (2022).
- **Communication:** cinema commissions (1948–59) → Social Communications (1964) → Pontifical Council (1989), absorbed into the new Secretariat for Communication (2015/16) → renamed a dicastery (2018).
- **Secretariat of State:**
  - Origins in the 15th century, with no founding act.
  - 1968: absorbs the Secretariat of Briefs and the Briefs to Princes.
  - 1973: absorbs the Chancery.
  - 1989: absorbs the Council for Public Affairs.
- **Tribunals:**
  - Penitentiary: medieval.
  - Rota: revived in 1908.
  - Signatura: the old Signatures were suppressed and a new tribunal instituted in 1908.

## 4. Hard cases (H1–H20)

- **H1. Holy Office → CDF, 1965.** The act changes the name and the procedure (*nomen et ordo*) together, so a rename comes with a change of purpose. Without an explicit rule, the CDF (*Donum Veritatis*) and the DDF (*Fiducia Supplicans*) could be split into two issuers.
- **H2. Council → Clergy, 1967.** The rename comes with a redefined subject matter.
- **H3. *In fructibus multis*, 1964.** The text says "mutato nomine et munerum provincia amplificata", the clearest primary wording of a rename with new competences. A second problem: the Latin *Consilium* is called a "Commission" in English, so kind labels depend on language.
- **H4. Index → Holy Office, 1917.** The preamble talks of uniting the two ("unum fieri"), but the operative clause says "S. Congregatio Indicis iam nunc non erit". Absorption therefore has to be its own event type, in which the absorbing body keeps its identity.
- **H5. Culture and Non-Believers, 1993.** The act calls the result "a single entity that will be called the Pontifical Council for Culture". It is a merger in which one partner keeps its name. In 2022 the reverse happened: the merged bodies got new names, but PE never states the mergers in an article.
- **H6. Divine Worship.** The body existed from 1969 to 1975 and "ceased in its present configuration". An identically named congregation was created in 1984. The Sacraments congregation follows almost the same path. The registry therefore needs to look up names by date.
- **H7. The Worship and Sacraments cycle, 1969–1988:** a split, then a merger, a split and a merger again. That gives six bodies in twenty years.
- **H8. Religious.** Regulars (1586) was merged away in 1601. In 1908 a new congregation took over its subject matter. The registry has to decide whether this line goes back to 1586.
- **H9. Implicit suppressions.**
  - Bishops-and-Regulars disappeared in 1908 because *Sapienti consilio* declared a closed list without it.
  - The Datary and Ceremonial ended under REU, whose full Latin text names neither.
- **H10. Signatura and Rota, 1908.**
  - For the Signatura the act says "restituimus, seu melius instituimus" ("we restore, or rather institute").
  - For the dormant Rota it says "rursus in exercitium revocamus" ("we call it back into operation").
- **H11. *Seminaria clericorum*, 1915.** The act founds a new congregation for seminaries, adds the Congregation of Studies' functions to it, and gives it the combined name. It never says Studies is suppressed. It reads equally well as a rename of Studies or as a new body absorbing Studies; the data models it as a rename.
- **H12. *Dei providentis*, 1917.** The old body "esse desinat" and the new one is "seorsum" (separate). This is a clean suppression plus new foundation, useful as a baseline.
- **H13. Changes of kind with no change of identity.**
  - Secretariat of State: an office (1908), then a dicastery (1967–2022), then explicitly not one of the dicasteries (PE Art. 12).
  - Almonry: a household office, then an institution adhering to the Holy See (PB Part IX), then a dicastery.
  - Council for Public Affairs: a congregation, then a council, then a section of the Secretariat of State.
  - Apostolic Camera: in PE the office is named after its holder ("Camerlengo").
- **H14. Signing date versus effective date.**
  - *Sedula Mater*: signed 15 Aug, effective 1 Sep 2016.
  - *Humanam progressionem*: signed 17 Aug 2016, effective 1 Jan 2017.
  - PB: signed 28 Jun 1988, effective 1 Mar 1989.
  - PE: signed 19 Mar, effective 5 Jun 2022.
  - The 2018 Communication rescript: audience of 27 Feb, published 23 Jun 2018.

  Documents signed in the gap are signed by the old body.
- **H15. *Recognito*, 1984.** It follows Benedict XV's precedent and "erects" a new commission, with no succession clause. This is lineage by imitation.
- **H16. Part-of relations.**
  - Migrants (1970): placed "obnoxia" (subject) to the Congregation for Bishops.
  - Health (1985): made a "complens pars" (completing part) of the Laity council.
  - Cultural Heritage: placed inside the Congregation for the Clergy by PB.
  - Minors (2022): placed within the DDF.
  - The Migrants and Refugees Section after 2017 reported directly to the Pope (unverified).

  A flat registry cannot represent these; they need their own relation type.
- **H17. Family, 1981.** The new council "succedit eique sufficitur; quare hoc iam ilico cessat" ("succeeds and replaces it; therefore the old one ceases at once"). This is explicit succession by re-foundation. Compare the Laity council in 1976, which was simply renamed ("in posterum appellabitur").
- **H18. Name traps.**
  - The Sixtine "Congregation of Bishops" is not the ancestor of the 1967 "Congregation for Bishops"; the Consistorial is.
  - "Sacred Congregation for Divine Worship" names two different bodies.
  - The Catholic Encyclopedia describes two different "State of Regulars" congregations.
  - The CDF's Latin preposition varies: "pro" in 1965 and 1967, "de" in the online Latin of PB.
  - English "Eastern" translates Latin "Orientalibus".
- **H19. Personal unions:** shared presidents in 2006–07 (secondary sources). A common head should never be treated as a merger.
- **H20. Chirograph title collision.** The chirograph creating the Commission for Donations and the one suppressing it share the title *Vinculum unitatis et caritatis*. This directly affects `mag:` keys built on incipits.

**Suggested for the TAG (not decided):**
- Use these event types: rename, rename+competence, kind-change, absorption (the absorbing body keeps its identity), merger (new body), split (new bodies), re-foundation (explicit succession), attachment or part-of, and revival.
- Decide identity by the act's operative clause, not its preamble.
- Adopt a documented default for acts that are silent, and flag the result as inferred.
- Treat name and kind as dated attributes, never as part of the key.

## 5. Gaps and unverified facts

- **Before 1908:** almost all founding acts and dates are secondary. *Immensa aeterni Dei* itself was not read.
- **Inferred, not found in an act:**
  - The 1988/89 Worship and Sacraments merger.
  - The end of the Datary and of Ceremonial.
- **Not located at all:**
  - The 1999 rename of Legislative Texts (BnF record only).
  - The end of the Prefecture for Economic Affairs in 2016 (Wikipedia only).
  - The end of the Pontifical Council for Social Communications (about 2016).
  - The date of the rename to Prefecture of the Papal Household.
  - When "Sacra" was dropped from names.
- **Located but not read in full:**
  - The 2010–2013 motu proprios.
  - The 2019 motu proprio on Ecclesia Dei and the 2018 Communication rescript.
  - *Quaerit semper*, *Ecclesiae unitatem*, *Ad charisma tuendum* and the 2014 chirograph founding the Commission for the Protection of Minors.
  - The Latin names of the 2022 dicasteries.
- **Not traced:**
  - The Sixtine temporal congregations, individually.
  - Older Eastern antecedents.
  - The Commission for Religious Relations with the Jews and the Sacred Archaeology commission.
  - Vatican II interpretation commissions after 1966.
  - The Statistics Office, ULSA and the 1981 Council of Cardinals.
  - The Commission for Confidential Matters and the Investment Committee.
  - The antecedents of APSA and of the Office of Liturgical Celebrations.
- **After 2022:** needs a check against the AAS volumes for 2025 and 2026.
- **Commissions:** whether the *Annuario* counted them among the dicasteries in a given year is mostly unknown.

## 6. Where the *Annuario Pontificio* is needed

- The official Latin and Italian name of each body in each year, including the dropping of "Sacra" and the "seu de Propaganda Fide" suffix.
- Which bodies were counted as dicasteries: the commissions, the secretariats of 1960–67, and the Almonry before 2022.
- The Holy See's own lineage claims in its "Note storiche" (Consecrated Life to 1586? Education to 1588? Clergy to 1564? DDF to 1542? Evangelization to 1622?). This bears directly on H5, H8 and H11.
- Exact dates for the implicit suppressions, the 1988/89 merger, the 1999 rename, and the end of the Social Communications council and the Prefecture for Economic Affairs.
- The pre-1908 minor congregations, checked together with the *Bullarium Romanum* or Del Re, *La Curia Romana* (1998).
