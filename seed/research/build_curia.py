#!/usr/bin/env python3
"""Build bodies.json and events.json for the Roman Curia history research.

All keys are PROVISIONAL working keys, not identifiers.
verified=true means the fact was checked against the text of the act itself
(AAS PDF on vatican.va, or the act's page on vatican.va). Everything else is
verified=false, with source_type saying what supports it.
"""
import json, sys, os

OUT = sys.argv[1]

def AAS(v):
    return f"https://www.vatican.va/archive/aas/documents/AAS-{v}-ocr.pdf"

U = {
    "SC": AAS("01-1909"),            # Sapienti consilio, AAS 1 (1909) 7-19
    "CIC17": AAS("09-II-1917"),      # CIC 1917, cann. 242-264
    "AAS9I": AAS("09-I-1917"),       # Alloquentes proxime p.167; Dei providentis pp.529-531
    "AAS7": AAS("07-1915"),          # Seminaria clericorum pp.493-495
    "AAS22": AAS("22-1930"),
    "AAS30": AAS("30-1938"),
    "AAS52": AAS("52-1960"),
    "AAS56": AAS("56-1964"),
    "AAS57": AAS("57-1965"),
    "AAS58": AAS("58-1966"),
    "AAS59": AAS("59-1967"),
    "AAS60": AAS("60-1968"),
    "AAS61": AAS("61-1969"),
    "AAS62": AAS("62-1970"),
    "AAS63": AAS("63-1971"),
    "AAS65": AAS("65-1973"),
    "AAS67": AAS("67-1975"),
    "AAS68": AAS("68-1976"),
    "AAS73": AAS("73-1981"),
    "AAS74": AAS("74-1982"),
    "AAS76": AAS("76-1984"),
    "AAS77": AAS("77-1985"),
    "REU": "https://www.vatican.va/content/paul-vi/la/apost_constitutions/documents/hf_p-vi_apc_19670815_regimini-ecclesiae-universae.html",
    "PB_EN": "https://www.vatican.va/content/john-paul-ii/en/apost_constitutions/documents/hf_jp-ii_apc_19880628_pastor-bonus.html",
    "PB_LA": "https://www.vatican.va/content/john-paul-ii/la/apost_constitutions/documents/hf_jp-ii_apc_19880628_pastor-bonus.html",
    "PE": "https://www.vatican.va/content/francesco/en/apost_constitutions/documents/20220319-costituzione-ap-praedicate-evangelium.html",
    "INDE": "https://www.vatican.va/content/john-paul-ii/en/motu_proprio/documents/hf_jp-ii_motu-proprio_25031993_inde-a-pontificatus.html",
    "UBICUMQUE": "https://www.vatican.va/content/benedict-xvi/en/apost_letters/documents/hf_ben-xvi_apl_20100921_ubicumque-et-semper.html",
    "PULCHR": "https://m.vatican.va/content/benedict-xvi/la/motu_proprio/documents/hf_ben-xvi_motu-proprio_20120730_pulchritudinis-fidei.pdf",
    "MINISTRORUM": "https://www.vatican.va/content/benedict-xvi/en/motu_proprio/documents/hf_ben-xvi_motu-proprio_20130116_ministrorum-institutio.html",
    "FIDESPERDOCT": "https://m.vatican.va/content/benedict-xvi/en/motu_proprio/documents/hf_ben-xvi_motu-proprio_20130116_fides-per-doctrinam.pdf",
    "FDP": "https://www.vatican.va/content/francesco/en/motu_proprio/documents/papa-francesco-motu-proprio_20140224_fidelis-dispensator-et-prudens.html",
    "SPC2015": "https://www.vatican.va/content/francesco/en/motu_proprio/documents/papa-francesco-motu-proprio_20150627_segreteria-comunicazione.html",
    "SEDULA": "https://www.vatican.va/content/francesco/en/apost_letters/documents/papa-francesco-lettera-ap_20160815_sedula-mater.html",
    "HUMANAM": "https://www.vatican.va/content/francesco/en/motu_proprio/documents/papa-francesco-motu-proprio_20160817_humanam-progressionem.html",
    "RESCRIPT2018": "https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2018/06/23/180623f.html",
    "ED2019": "https://www.vatican.va/content/francesco/it/motu_proprio/documents/papa-francesco-motu-proprio-20190117_ecclesia-dei.html",
    "VINC2025F": "https://www.vatican.va/content/francesco/en/letters/2025/documents/20250211-chirografo-vinculum-unitatisetcaritatis.html",
    "VINC2025L": "https://www.vatican.va/content/leo-xiv/it/letters/2025/documents/20250929-chirografo-vinculum-unitatis.html",
    "REGCUR2025": "https://www.vaticannews.va/en/pope/news/2025-11/vatican-publishes-the-new-regulations-of-the-roman-curia.html",
    "CE_CONG": "https://www.newadvent.org/cathen/13136a.htm",
    "WP_IMMENSA": "https://en.wikipedia.org/wiki/Immensa_Aeterni_Dei",
    "WP_DATARY": "https://en.wikipedia.org/wiki/Apostolic_Datary",
    "WP_PREFECON": "https://en.wikipedia.org/wiki/Prefecture_for_the_Economic_Affairs_of_the_Holy_See",
    "VA_CEVANG": "https://www.vatican.va/roman_curia/congregations/cevang/documents/rc_con_cevang_20100524_profile_sp.html",
    "BNF_PCLT": "https://data.bnf.fr/13506922/eglise_catholique_pontificium_consilium_de_legum_textibus/fr.pdf",
    "VN_DONATIONS": "https://www.vaticannews.va/en/pope/news/2025-02/pope-establishes-a-commission-for-donations-to-the-holy-see.html",
}

ACT = {
    "IMMENSA": "Sixtus V, bull Immensa aeterni Dei, 22 Jan 1588 (dated 'xxii Ianuarii MDLXXXVII' in the Florentine/Incarnation style, as cited by Sapienti consilio)",
    "SC": "Pius X, ap. const. Sapienti consilio, 29 Jun 1908, in force 3 Nov 1908, AAS 1 (1909) 7-19",
    "CIC17": "Codex Iuris Canonici 1917 (promulgated 27 May 1917, in force 19 May 1918), cann. 242-264",
    "ALLOQ": "Benedict XV, m.p. Alloquentes proxime, 25 Mar 1917, AAS 9-I (1917) 167",
    "DEIPROV": "Benedict XV, m.p. Dei providentis, 1 May 1917, AAS 9-I (1917) 529-531",
    "SEMCLER": "Benedict XV, m.p. Seminaria clericorum, 4 Nov 1915, AAS 7 (1915) 493-495",
    "CUMIURIS": "Benedict XV, m.p. Cum iuris canonici Codicem, 15 Sep 1917 (AAS 9-I index)",
    "INTEGRAE": "Paul VI, m.p. Integrae servandae, 7 Dec 1965, AAS 57 (1965) 952-955",
    "REU": "Paul VI, ap. const. Regimini Ecclesiae universae, 15 Aug 1967, AAS 59 (1967) 885-928, in force 1 Jan 1968",
    "CATHOLICAM": "Paul VI, m.p. Catholicam Christi Ecclesiam, 6 Jan 1967, AAS 59 (1967) 25-28",
    "SACRARITUUM": "Paul VI, ap. const. Sacra Rituum Congregatio, 8 May 1969, AAS 61 (1969) 297-305",
    "CONSTANS": "Paul VI, ap. const. Constans nobis, 11 Jul 1975, AAS 67 (1975) 417-420",
    "QUONIAM": "John Paul II, chirograph Quoniam in celeri, 5 Apr 1984, AAS 76 (1984) 494-495",
    "RECOGNITO": "John Paul II, m.p. Recognito Iuris Canonici Codice, 2 Jan 1984, AAS 76 (1984) 433-434",
    "PB": "John Paul II, ap. const. Pastor bonus, 28 Jun 1988, in force 1 Mar 1989",
    "PE": "Francis, ap. const. Praedicate Evangelium, 19 Mar 2022, in force 5 Jun 2022 (Art. 250)",
    "QUOAPTIUS": "Paul VI, m.p. Quo aptius, 27 Feb 1973, AAS 65 (1973) 113-116",
    "SUPERNO": "John XXIII, m.p. Superno Dei nutu, 5 Jun 1960, AAS 52 (1960) 433-437 (n. 9)",
    "FINIS": "Paul VI, m.p. Finis Concilio, 3 Jan 1966, AAS 58 (1966) 37-40 (n. 11)",
    "PROGREDIENTE": "Paul VI, ap. letter Progrediente Concilio, 19 May 1964, AAS 56 (1964) 560",
    "INFRUCTIBUS": "Paul VI, m.p. In fructibus multis, 2 Apr 1964, AAS 56 (1964) 289-292",
    "APOSTOLATUS": "Paul VI, m.p. Apostolatus peragendi, 10 Dec 1976, AAS 68 (1976) 696ff",
    "IUSTITIAM": "Paul VI, m.p. Iustitiam et pacem, 10 Dec 1976, AAS 68 (1976) 700ff",
    "APOSTCARIT": "Paul VI, m.p. Apostolicae caritatis, 19 Mar 1970, AAS 62 (1970) 193ff",
    "AMORIS": "Paul VI, letter Amoris officio to Card. Villot, 15 Jul 1971, AAS 63 (1971) 669",
    "FAMILIA": "John Paul II, m.p. Familia a Deo instituta, 9 May 1981, AAS 73 (1981) 441-445",
    "CULTURA82": "John Paul II, letter to Card. Casaroli instituting the Pontificium Consilium pro hominum Cultura, 20 May 1982, AAS 74 (1982) 683",
    "DOLENTIUM": "John Paul II, m.p. Dolentium hominum, 11 Feb 1985, AAS 77 (1985) 457ff",
    "INDE": "John Paul II, m.p. Inde a Pontificatus, 25 Mar 1993",
    "UBICUMQUE": "Benedict XVI, m.p. Ubicumque et semper, 21 Sep 2010",
    "PULCHR": "Benedict XVI, m.p. Pulchritudinis fidei, 30 Jul 2012",
    "MINISTRORUM": "Benedict XVI, m.p. Ministrorum institutio, 16 Jan 2013",
    "FIDESPERDOCT": "Benedict XVI, m.p. Fides per doctrinam, 16 Jan 2013",
    "FDP": "Francis, m.p. Fidelis dispensator et prudens, 24 Feb 2014",
    "SPC2015": "Francis, m.p. L'attuale contesto comunicativo, 27 Jun 2015",
    "SEDULA": "Francis, ap. letter m.p. Sedula Mater, 15 Aug 2016 (effective 1 Sep 2016)",
    "HUMANAM": "Francis, m.p. Humanam progressionem, 17 Aug 2016 (effective 1 Jan 2017)",
    "RESCRIPT2018": "Rescript ex audientia (audience of 27 Feb 2018), published 23 Jun 2018",
    "ED2019": "Francis, m.p. [Ecclesia Dei] 'Da oltre trent'anni', 17 Jan 2019",
    "PONTDOMUS": "Paul VI, m.p. Pontificalis Domus, 28 Mar 1968, AAS 60 (1968)",
}

def name(la, en, frm, to, act, url, verified, src, note=None):
    d = {"name_la": la, "name_en": en, "from": frm, "to": to, "act": act,
         "act_source_url": url, "verified": verified, "source_type": src}
    if note: d["note"] = note
    return d

def kind(k, frm, to, basis, verified=True):
    return {"kind": k, "from": frm, "to": to, "basis": basis, "verified": verified}

def cc(date, change, act, verified, src="primary"):
    return {"date": date, "change": change, "act": act, "verified": verified, "source_type": src}

def link(key, event, date, note=None):
    d = {"key": key, "event": event, "date": date}
    if note: d["note"] = note
    return d

P, OS, S, INF = "primary", "official-secondary", "secondary", "inferred"

bodies = []
def body(**kw):
    kw.setdefault("provisional_key", True)
    kw.setdefault("predecessors", [])
    kw.setdefault("successors", [])
    kw.setdefault("competence_changes", [])
    kw.setdefault("issues_doctrinal_documents", False)
    order = ["key", "provisional_key", "line", "issues_doctrinal_documents", "curia_status", "names", "kind",
             "erected", "ended", "predecessors", "successors", "competence_changes", "notes"]
    bodies.append({k: kw[k] for k in order if k in kw})

# ---------------------------------------------------------------- Doctrine line
body(key="inquisition-holy-office-cdf-ddf", line="doctrine", issues_doctrinal_documents=True,
     curia_status="Counted in the Curia throughout; listed first among congregations in 1908, 1917, 1967, 1988; second dicastery in 2022.",
     names=[
        name("Sacra Congregatio Romanae et Universalis Inquisitionis", "Congregation of the Roman and Universal Inquisition", "1542-07-21", "1908-11-03", "Paul III, ap. const. Licet ab initio, 21 Jul 1542", U["AAS57"], True, P,
             "Founding act and date as stated in Integrae servandae, AAS 57 (1965) 953; Licet ab initio itself not read."),
        name("Congregatio Sancti Officii (Suprema Sacra Congregatio S. Officii)", "Congregation of the Holy Office (Supreme Sacred Congregation of the Holy Office)", "1908-11-03", "1965-12-07", ACT["SC"], U["SC"], True, P,
             "Sapienti consilio heading reads 'Congregatio Sancti Officii'; AAS headings of 1915 use 'Suprema Sacra Congregatio S. Officii'. Integrae servandae states that Sapienti consilio changed the name."),
        name("Congregatio pro doctrina fidei / Sacra Congregatio pro Doctrina Fidei", "Congregation for the Doctrine of the Faith (Sacred Congregation ...)", "1965-12-07", "2022-06-05", ACT["INTEGRAE"], U["AAS57"], True, P,
             "Integrae servandae n.1: 'Quae hactenus appellata est Sacra Congregatio Sancti Officii, in posterum appellabitur Congregatio pro doctrina fidei'. REU (1967) n.29: 'Sacra Congregatio pro Doctrina Fidei'. The Latin text of Pastor bonus online reads 'Congregatio de Doctrina Fidei' (pro -> de); the dropping of 'Sacra' and the pro/de variation are not tied to a located act."),
        name("Dicasterium pro Doctrina Fidei", "Dicastery for the Doctrine of the Faith", "2022-06-05", None, ACT["PE"], U["PE"], True, P, "PE Arts. 69-78 (English text read; Latin title not checked)."),
     ],
     kind=[kind("congregation", "1542-07-21", "2022-06-05", "Licet ab initio / Sapienti consilio / CIC 1917 can. 247 / REU / PB"),
           kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1542-07-21", "act": "Paul III, Licet ab initio", "verified": True, "source_type": P,
              "note": "Verified only through the recital in Integrae servandae (AAS 57 (1965) 953). The Catholic Encyclopedia notes it 'began as a congregation in 1558 under Paul IV' — the founding date of the *congregation* (as opposed to the tribunal) is itself debatable."},
     ended=None,
     predecessors=[link("index", "absorption", "1917-03-25"), link("ecclesia-dei-commission", "absorption", "2019-01-17")],
     successors=[],
     competence_changes=[
        cc("1908-11-03", "Gains all matters of indulgences (doctrine and use); loses ecclesiastical precepts (to Council), election of bishops (to Consistorial), dispensation of religious vows (to Religious).", ACT["SC"], True),
        cc("1917-03-25", "Absorbs the Congregation of the Index (new Sectio de Indice); loses indulgences (to Penitentiary, keeps dogmatic aspects).", ACT["ALLOQ"], True),
        cc("1965-12-07", "Renamed; purpose recast from defending to promoting doctrine; new procedure for examining books (author to be heard).", ACT["INTEGRAE"], True),
        cc("1966-06-14", "Index of Forbidden Books loses force of ecclesiastical law (CDF notification).", "CDF notification of 14 Jun 1966", False, S),
        cc("2019-01-17", "Absorbs all tasks of the Pontifical Commission Ecclesia Dei (dedicated section).", ACT["ED2019"], False, OS),
        cc("2022-06-05", "Pontifical Commission for the Protection of Minors established within it (PE Art. 78); PBC and ITC established within it (PE Art. 77).", ACT["PE"], True),
     ],
     notes="Core test case. The working hypothesis ('rename keeps the body') gives one continuous body 1542-present, which matches how the Holy See itself narrates it (Integrae servandae recites 1542 and 1908 as its own history). But 1965 is a rename + change of purpose + new 'ordo' at once, and 1917 adds a whole former congregation (Index). The Pope was prefect until 1968 (REU) — CIC 1917 can. 247; Integrae servandae n.2.")

body(key="index", line="doctrine", issues_doctrinal_documents=True,
     curia_status="One of the Sixtine 15 (1588); in Sapienti consilio (7th congregation); absent from CIC 1917.",
     names=[name("Sacra Congregatio Indicis", "Congregation of the Index", "1571", "1917-03-25", "Pius V, 1571 (Congregation for the Reform of the Index); confirmed by Immensa aeterni Dei 1588", U["CE_CONG"], False, S,
                 "Founding year from Catholic Encyclopedia; the 1571 act was not read. Name and existence in 1908 verified in Sapienti consilio.")],
     kind=[kind("congregation", "1571", "1917-03-25", "Sapienti consilio, 7°")],
     erected={"date": "1571", "act": "Pius V (act not identified)", "verified": False, "source_type": S},
     ended={"date": "1917-03-25", "act": ACT["ALLOQ"], "how": "absorbed", "verified": True, "source_type": P,
            "note": "Text: 'S. Congregatio Indicis iam nunc non erit'; its function passes to the Holy Office with a new Sectio de Indice and its officials. The preamble frames this as joining the two congregations ('ex eis Congregationibus unum fieri') — merger language, absorption mechanics."},
     successors=[link("inquisition-holy-office-cdf-ddf", "absorption", "1917-03-25")],
     competence_changes=[cc("1908-11-03", "Gains duty to search out (ex officio) and denounce harmful writings; secrecy shared with the Holy Office.", ACT["SC"], True)])

body(key="ecclesia-dei-commission", line="doctrine", issues_doctrinal_documents=False,
     curia_status="Pontifical Commission; not listed as a dicastery in Pastor bonus.",
     names=[name("Pontificia Commissio «Ecclesia Dei»", "Pontifical Commission Ecclesia Dei", "1988-07-02", "2019-01-17", "John Paul II, m.p. Ecclesia Dei adflicta, 2 Jul 1988", U["ED2019"], False, OS,
                 "Founding date recited in the 2019 motu proprio (search snippet of vatican.va); the 1988 act itself not read.")],
     kind=[kind("commission", "1988-07-02", "2019-01-17", "Ecclesia Dei adflicta; linked to the CDF from 2009 (Ecclesiae unitatem, not read)", False)],
     erected={"date": "1988-07-02", "act": "Ecclesia Dei adflicta", "verified": False, "source_type": OS},
     ended={"date": "2019-01-17", "act": ACT["ED2019"], "how": "absorbed", "verified": False, "source_type": OS,
            "note": "'È soppressa la Pontificia Commissione Ecclesia Dei'; tasks 'assegnati integralmente' to the CDF. Text located on vatican.va via search; quoted from search extract, not read in full."},
     successors=[link("inquisition-holy-office-cdf-ddf", "absorption", "2019-01-17")])

body(key="protection-minors-commission", line="doctrine",
     curia_status="Pontifical Commission (2014) connected to the Holy See; since 2022 'established within' the DDF (PE Art. 78).",
     names=[name("Pontificia Commissio pro Tutela Minorum", "Pontifical Commission for the Protection of Minors", "2014-03-22", None, "Francis, chirograph of 22 Mar 2014 (not read)", None, False, S)],
     kind=[kind("commission", "2014-03-22", None, "PE Art. 78 §1", True)],
     erected={"date": "2014-03-22", "act": "Francis, chirograph (not read)", "verified": False, "source_type": S},
     ended=None,
     competence_changes=[cc("2022-06-05", "Placed within the Dicastery for the Doctrine of the Faith, keeping its own president.", ACT["PE"], True)],
     notes="Not a curial dicastery; included because PE embeds it in the DDF. Hard case: a body that becomes a part of another body without losing its own name or head (neither merger nor absorption in the hypothesis' sense).")

# ---------------------------------------------------------------- Evangelization line
body(key="propaganda-fide-evangelization", line="evangelization", issues_doctrinal_documents=True,
     curia_status="Congregation from 1622 to 2022 (6th in 1908; listed in CIC 1917, REU, PB). Since 2022 merged into the Dicastery for Evangelization.",
     names=[
        name("Sacra Congregatio de Propaganda Fide", "Sacred Congregation for the Propagation of the Faith", "1622-06-22", "1968-01-01", "Gregory XV, bull Inscrutabili divinae, 22 Jun 1622", U["VA_CEVANG"], False, OS,
             "Date from the dicastery's own profile on vatican.va and secondary literature; bull not read. Name in 1908 verified in Sapienti consilio."),
        name("Sacra Congregatio pro Gentium Evangelizatione seu de Propaganda Fide", "Sacred Congregation for the Evangelization of Peoples, or 'de Propaganda Fide'", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.81."),
        name("Congregatio pro Gentium Evangelizatione", "Congregation for the Evangelization of Peoples", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P, "PB Arts. 85-92 (Latin heading as rendered by vatican.va). Whether 'seu de Propaganda Fide' remains in its official name is not settled by the text read; Annuario needed."),
     ],
     kind=[kind("congregation", "1622-06-22", "2022-06-05", "Sapienti consilio / CIC 1917 / REU / PB")],
     erected={"date": "1622-06-22", "act": "Inscrutabili divinae", "verified": False, "source_type": OS,
              "note": "A cardinalitial commission for missions under Gregory XIII (1572-85) preceded it (Catholic Encyclopedia)."},
     ended={"date": "2022-06-05", "act": ACT["PE"], "how": "merged", "verified": True, "source_type": P,
            "note": "PE does not name the merged bodies article by article; it states in general that dicasteries with similar purposes were unified (Preamble II.11) and abolishes PB bodies not provided for (Art. 250 §3). The merger is therefore inferred from PE's structure (two sections of the new dicastery), not from an explicit clause."},
     successors=[link("evangelization-dicastery", "merger", "2022-06-05")],
     competence_changes=[
        cc("1862-01-06", "A congregation 'pro negotiis ritus orientalis' is joined to it (Pius IX, Romani Pontifices).", ACT["DEIPROV"], True),
        cc("1908-11-03", "England, Scotland, Ireland, Holland, Luxembourg, Canada, Newfoundland and the USA removed from its jurisdiction; its special economic prefecture ends; it takes over the administration of the Camera Spoliorum; the 'coetus pro unione Ecclesiarum dissidentium' is joined to it.", ACT["SC"], True),
        cc("1917-11-30", "Its Oriental-rite congregation ceases (moves to the new Congregation for the Oriental Church).", ACT["DEIPROV"], True),
     ])

body(key="new-evangelization-council", line="evangelization", issues_doctrinal_documents=True,
     curia_status="Pontifical Council, a dicastery under Pastor bonus (Ubicumque et semper Art. 1).",
     names=[name("Pontificium Consilium ad Novam Evangelizationem Promovendam", "Pontifical Council for Promoting the New Evangelization", "2010-09-21", "2022-06-05", ACT["UBICUMQUE"], U["UBICUMQUE"], False, OS, "Act exists on vatican.va; content summarised from search extract, not read in full.")],
     kind=[kind("pontifical council", "2010-09-21", "2022-06-05", "Ubicumque et semper", False)],
     erected={"date": "2010-09-21", "act": ACT["UBICUMQUE"], "verified": False, "source_type": OS},
     ended={"date": "2022-06-05", "act": ACT["PE"], "how": "merged", "verified": True, "source_type": P, "note": "Same caveat as Propaganda: merger inferred from PE structure."},
     successors=[link("evangelization-dicastery", "merger", "2022-06-05")],
     competence_changes=[
        cc("2013-01-16", "Receives catechesis from the Congregation for the Clergy.", ACT["FIDESPERDOCT"], False, OS),
        cc("2017-02-11", "Receives competence over shrines (m.p. Sanctuarium in Ecclesia; not read).", "Francis, m.p. Sanctuarium in Ecclesia, 11 Feb 2017", False, S),
     ])

body(key="evangelization-dicastery", line="evangelization", issues_doctrinal_documents=True,
     curia_status="Dicastery (first in PE order), presided directly by the Roman Pontiff (PE Art. 54).",
     names=[name("Dicasterium pro Evangelizatione", "Dicastery for Evangelization", "2022-06-05", None, ACT["PE"], U["PE"], True, P, "PE Arts. 53-68; two sections, each under a Pro-Prefect.")],
     kind=[kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "2022-06-05", "act": ACT["PE"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("propaganda-fide-evangelization", "merger", "2022-06-05"), link("new-evangelization-council", "merger", "2022-06-05")],
     notes="Section for First Evangelization and New Particular Churches = Propaganda's work; Section for Fundamental Questions = New Evangelization's work. Pope as head recalls the pre-1968 Holy Office/Consistorial model.")

# ---------------------------------------------------------------- Oriental
body(key="oriental-rites-propaganda", line="eastern",
     curia_status="Attached to Propaganda; Dei providentis calls it 'S. Congregatio de Propaganda Fide pro negotiis ritus orientalis'. Sapienti consilio lists it as a congregation united to Propaganda, not among the 11.",
     names=[name("Sacra Congregatio de Propaganda Fide pro negotiis ritus orientalis", "Congregation of Propaganda for Affairs of the Oriental Rite", "1862-01-06", "1917-11-30", "Pius IX, ap. const. Romani Pontifices, 6 Jan 1862", U["AAS9I"], True, P,
                 "Existence and founding pope verified in Dei providentis; the date 6 Jan 1862 and act name are secondary.")],
     kind=[kind("congregation (attached section)", "1862-01-06", "1917-11-30", "Sapienti consilio 6° n.6: 'Unitam habet Congregationem pro Negotiis rituum orientalium'")],
     erected={"date": "1862-01-06", "act": "Romani Pontifices", "verified": False, "source_type": S},
     ended={"date": "1917-11-30", "act": ACT["DEIPROV"], "how": "suppressed", "verified": True, "source_type": P,
            "note": "'...pro negotiis ritus orientalis die xxx mensis novembris huius anni esse desinat'."},
     successors=[link("oriental-churches", "split", "1917-12-01", "Explicit suppression followed next day by a new congregation 'seorsum a S. Congregatione de Propaganda Fide'.")])

body(key="oriental-churches", line="eastern", issues_doctrinal_documents=True,
     curia_status="Congregation 1917-2022 (CIC 1917 can. 257; REU; PB), dicastery since 2022.",
     names=[
        name("Sacra Congregatio pro Ecclesia Orientali", "Sacred Congregation for the Oriental Church", "1917-12-01", "1968-01-01", ACT["DEIPROV"], U["AAS9I"], True, P),
        name("Sacra Congregatio pro Ecclesiis Orientalibus", "Sacred Congregation for the Oriental Churches", "1968-01-01", "2022-06-05", ACT["REU"], U["REU"], True, P, "REU n.41; PB Latin 'Congregatio pro Ecclesiis Orientalibus'."),
        name("Dicasterium pro Ecclesiis Orientalibus", "Dicastery for the Eastern Churches", "2022-06-05", None, ACT["PE"], U["PE"], True, P, "English changes 'Oriental' to 'Eastern' although (presumably) the Latin does not; Latin title of PE not checked."),
     ],
     kind=[kind("congregation", "1917-12-01", "2022-06-05", "Dei providentis / CIC 1917 can. 257"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1917-12-01", "act": ACT["DEIPROV"], "verified": True, "source_type": P, "note": "Pope as prefect (Dei providentis II; CIC 1917 can. 257 §1)."},
     ended=None,
     predecessors=[link("oriental-rites-propaganda", "split", "1917-12-01")],
     competence_changes=[cc("1938-03-25", "Jurisdiction extended to entire territories (all faithful) in parts of the Near East (Pius XI, m.p. Sancta Dei Ecclesia).", "Pius XI, m.p. Sancta Dei Ecclesia, 25 Mar 1938, AAS 30 (1938) 154", False, P)],
     notes="Older antecedents (Gregory XIII's congregation for Greek affairs, 1573; the congregation for the correction of Oriental liturgical books) are not traced here — Annuario/Del Re needed.")

# ---------------------------------------------------------------- Rites / Worship / Saints / Sacraments
body(key="rites", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="One of the Sixtine 15; congregation until 1969.",
     names=[
        name("Congregatio pro sacris ritibus et caeremoniis", "Congregation for Sacred Rites and Ceremonies", "1588-01-22", "1908-11-03", ACT["IMMENSA"], U["CE_CONG"], False, S, "Sixtine title per Catholic Encyclopedia / Wikipedia; bull not read."),
        name("Sacra Congregatio Rituum / Congregatio sacrorum Rituum", "Sacred Congregation of Rites", "1908-11-03", "1969-05-08", ACT["SC"], U["SC"], True, P, "Sapienti consilio 8°; REU n.58 'Sacra Congregatio Rituum'."),
     ],
     kind=[kind("congregation", "1588-01-22", "1969-05-08", "Sapienti consilio / CIC 1917 / REU")],
     erected={"date": "1588-01-22", "act": ACT["IMMENSA"], "verified": False, "source_type": OS, "note": "vatican.va profile of the Congregation for the Causes of Saints attributes it to Immensa aeterni Dei."},
     ended={"date": "1969-05-08", "act": ACT["SACRARITUUM"], "how": "suppressed", "verified": True, "source_type": P,
            "note": "'in locum Sacrae Rituum Congregationis ... duas novas substituimus Congregationes' — an explicit split into two NEW bodies."},
     predecessors=[link("indulgences-relics", "absorption", "1904-01-28")],
     successors=[link("divine-worship-1969", "split", "1969-05-08"), link("causes-of-saints", "split", "1969-05-08")],
     competence_changes=[
        cc("1908-11-03", "Keeps rites and ceremonies of the Latin Church, beatification/canonization and relics; liturgical, historico-liturgical and sacred-music commissions joined to it.", ACT["SC"], True),
        cc("1930-02-06", "Historical section instituted (Pius XI, m.p. Già da qualche tempo).", "Pius XI, m.p. Già da qualche tempo, 6 Feb 1930 (AAS 22 (1930) index)", True, P),
        cc("1968-01-01", "REU: two sections (worship; causes) plus historico-hagiographical office.", ACT["REU"], True),
     ])

body(key="divine-worship-1969", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1969-1975.",
     names=[name("Sacra Congregatio pro Cultu Divino", "Sacred Congregation for Divine Worship", "1969-05-08", "1975-07-11", ACT["SACRARITUUM"], U["AAS61"], True, P)],
     kind=[kind("congregation", "1969-05-08", "1975-07-11", "Sacra Rituum Congregatio")],
     erected={"date": "1969-05-08", "act": ACT["SACRARITUUM"], "verified": True, "source_type": P},
     ended={"date": "1975-07-11", "act": ACT["CONSTANS"], "how": "merged", "verified": True, "source_type": P,
            "note": "Constans nobis n.1: the two congregations 'in ea, quam nunc obtinent, conformatione esse desinunt'; n.2: 'Nova S. Congregatio instituitur'."},
     predecessors=[link("rites", "split", "1969-05-08"), link("liturgy-consilium", "absorption", "1969-05-08")],
     successors=[link("sacraments-divine-worship-1975", "merger", "1975-07-11")])

body(key="liturgy-consilium", line="worship-saints",
     curia_status="Post-conciliar 'Consilium'; REU n.133 keeps it 'donec munus absolvat' — attached to, not among, the curial dicasteries.",
     names=[name("Consilium ad exsequendam Constitutionem de Sacra Liturgia", "Consilium for the Implementation of the Constitution on the Sacred Liturgy", "1964", "1969-05-08", "Paul VI, m.p. Sacram Liturgiam, 25 Jan 1964 (not read)", U["AAS58"], False, S,
                 "Named in Finis Concilio (1966) as founded by Paul VI; founding act/date secondary.")],
     kind=[kind("commission", "1964", "1969-05-08", "Finis Concilio; REU n.133", True)],
     erected={"date": "1964", "act": "Sacram Liturgiam (secondary)", "verified": False, "source_type": S},
     ended={"date": "1969-05-08", "act": ACT["SACRARITUUM"], "how": "absorbed", "verified": True, "source_type": P,
            "note": "'tamquam Corpus sui iuris finem capere volumus' and continues as a special commission inside the new Congregation for Divine Worship."},
     successors=[link("divine-worship-1969", "absorption", "1969-05-08")])

body(key="causes-of-saints", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1969-2022; dicastery since 2022.",
     names=[
        name("Sacra Congregatio pro Causis Sanctorum", "Sacred Congregation for the Causes of Saints", "1969-05-08", "1989-03-01", ACT["SACRARITUUM"], U["AAS61"], True, P),
        name("Congregatio de Causis Sanctorum", "Congregation for the Causes of Saints", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P, "PB Latin heading 'de Causis Sanctorum' (pro -> de)."),
        name("Dicasterium de Causis Sanctorum", "Dicastery for the Causes of Saints", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English name verified (PE Arts. 98-102); Latin form not checked."),
     ],
     kind=[kind("congregation", "1969-05-08", "2022-06-05", "Sacra Rituum Congregatio / PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1969-05-08", "act": ACT["SACRARITUUM"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("rites", "split", "1969-05-08")])

body(key="sacraments-1908", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1908-1975 (3rd in Sapienti consilio; CIC 1917; REU n.54).",
     names=[name("Sacra Congregatio de disciplina Sacramentorum", "Sacred Congregation for the Discipline of the Sacraments", "1908-11-03", "1975-07-11", ACT["SC"], U["SC"], True, P)],
     kind=[kind("congregation", "1908-11-03", "1975-07-11", "Sapienti consilio 3°")],
     erected={"date": "1908-11-03", "act": ACT["SC"], "verified": True, "source_type": P, "note": "New congregation; took over sacramental/matrimonial matters previously spread among Council, Rites, Datary and Penitentiary."},
     ended={"date": "1975-07-11", "act": ACT["CONSTANS"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("sacraments-divine-worship-1975", "merger", "1975-07-11")])

body(key="sacraments-divine-worship-1975", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1975-1984.",
     names=[name("Sacra Congregatio pro Sacramentis et Cultu Divino", "Sacred Congregation for the Sacraments and Divine Worship", "1975-07-11", "1984-04-05", ACT["CONSTANS"], U["AAS67"], True, P,
                 "Constans nobis n.2 reads 'Sacra Congregatio pro Sacramentis divinoque Cultu'; Quoniam in celeri (1984) calls it 'Sacra Congregatio pro Sacramentis et Cultu Divino'.")],
     kind=[kind("congregation", "1975-07-11", "1984-04-05", "Constans nobis")],
     erected={"date": "1975-07-11", "act": ACT["CONSTANS"], "verified": True, "source_type": P},
     ended={"date": "1984-04-05", "act": ACT["QUONIAM"], "how": "suppressed", "verified": True, "source_type": P, "note": "Divided into two congregations (split)."},
     predecessors=[link("sacraments-1908", "merger", "1975-07-11"), link("divine-worship-1969", "merger", "1975-07-11")],
     successors=[link("sacraments-1984", "split", "1984-04-05"), link("divine-worship-1984", "split", "1984-04-05")])

body(key="sacraments-1984", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1984-1988/89.",
     names=[name("Sacra Congregatio pro Sacramentis", "Sacred Congregation for the Sacraments", "1984-04-05", "1989-03-01", ACT["QUONIAM"], U["AAS76"], True, P,
                 "Name differs from the 1908 body ('de disciplina Sacramentorum').")],
     kind=[kind("congregation", "1984-04-05", "1989-03-01", "Quoniam in celeri")],
     erected={"date": "1984-04-05", "act": ACT["QUONIAM"], "verified": True, "source_type": P},
     ended={"date": "1989-03-01", "act": ACT["PB"], "how": "merged", "verified": False, "source_type": INF,
            "note": "PB simply describes one 'Congregation for Divine Worship and the Discipline of the Sacraments' (Arts. 62-70); no clause stating the merger was found in the portion read. Date = PB entry into force; some sources date the merger to PB's signing (28 Jun 1988). Annuario needed."},
     predecessors=[link("sacraments-divine-worship-1975", "split", "1984-04-05")],
     successors=[link("divine-worship-sacraments-1988", "merger", "1989-03-01")])

body(key="divine-worship-1984", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1984-1988/89.",
     names=[name("Sacra Congregatio pro Cultu Divino", "Sacred Congregation for Divine Worship", "1984-04-05", "1989-03-01", ACT["QUONIAM"], U["AAS76"], True, P,
                 "Identical name to the 1969-1975 body (divine-worship-1969).")],
     kind=[kind("congregation", "1984-04-05", "1989-03-01", "Quoniam in celeri")],
     erected={"date": "1984-04-05", "act": ACT["QUONIAM"], "verified": True, "source_type": P},
     ended={"date": "1989-03-01", "act": ACT["PB"], "how": "merged", "verified": False, "source_type": INF, "note": "As for sacraments-1984."},
     predecessors=[link("sacraments-divine-worship-1975", "split", "1984-04-05")],
     successors=[link("divine-worship-sacraments-1988", "merger", "1989-03-01")],
     notes="Hard case: suppressed in 1975 and re-founded in 1984 under the same name. Under the hypothesis this is a NEW body (product of a split), so 'Sacred Congregation for Divine Worship' maps to two different working keys depending on date.")

body(key="divine-worship-sacraments-1988", line="worship-saints", issues_doctrinal_documents=True,
     curia_status="Congregation 1988/89-2022; dicastery since 2022.",
     names=[
        name("Congregatio de Cultu Divino et Disciplina Sacramentorum", "Congregation for Divine Worship and the Discipline of the Sacraments", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium de Cultu Divino et Disciplina Sacramentorum", "Dicastery for Divine Worship and the Discipline of the Sacraments", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified (PE Arts. 88-97); Latin not checked."),
     ],
     kind=[kind("congregation", "1989-03-01", "2022-06-05", "PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1989-03-01", "act": ACT["PB"], "verified": False, "source_type": INF, "note": "See sacraments-1984."},
     ended=None,
     predecessors=[link("sacraments-1984", "merger", "1989-03-01"), link("divine-worship-1984", "merger", "1989-03-01")],
     competence_changes=[cc("2011-08-30", "Loses dispensations super rato and causes of nullity of ordination (to the Roman Rota) — m.p. Quaerit semper (existence confirmed by editorial note on PB Latin page; date secondary).", "Benedict XVI, m.p. Quaerit semper", False, OS)])

# ---------------------------------------------------------------- Council / Clergy
body(key="council-clergy", line="clergy", issues_doctrinal_documents=True,
     curia_status="Congregation 1564-2022 (one of the Sixtine 15; 4th in 1908; CIC 1917; REU n.65; PB); dicastery since 2022.",
     names=[
        name("Congregatio Cardinalium Concilii Tridentini interpretum (Sacra Congregatio Concilii)", "Congregation of the Council (of Trent)", "1564-08-02", "1968-01-01", "Pius IV, m.p. Alias nos nonnullas, 2 Aug 1564", U["CE_CONG"], False, S,
             "Founding date per Catholic Encyclopedia; the incipit 'Alias nos nonnullas' is from memory and unverified. Name 'Congregatio Concilii' verified in Sapienti consilio 4°."),
        name("Sacra Congregatio pro Clericis", "Sacred Congregation for the Clergy", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.65 rename."),
        name("Congregatio pro Clericis", "Congregation for the Clergy", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium pro Clericis", "Dicastery for the Clergy", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("congregation", "1564-08-02", "2022-06-05", "Sapienti consilio / CIC 1917 / REU / PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1564-08-02", "act": "Pius IV, motu proprio (CE)", "verified": False, "source_type": S},
     ended=None,
     predecessors=[link("lauretana", "absorption", "1908-11-03"), link("revision-of-councils", "absorption", "1908-11-03")],
     competence_changes=[
        cc("1908-11-03", "Discipline of secular clergy and Christian people; precepts of the Church; councils and episcopal conferences (special congregation for revision of councils suppressed); Lauretana congregation united to it; diocesan-government matters move to the Consistorial.", ACT["SC"], True),
        cc("1968-01-01", "Renamed 'pro Clericis' with its remit redefined around clergy (REU n.65ff).", ACT["REU"], True),
        cc("1989-03-01", "PB: Pontifical Commission for Preserving the Patrimony of Art and History placed inside it (Arts. 99-104).", ACT["PB"], True),
        cc("1993-03-25", "That Commission becomes autonomous.", ACT["INDE"], True, P),
        cc("2013-01-16", "Gains seminaries (from Catholic Education) and the Pontifical Work for Priestly Vocations; loses catechesis (to New Evangelization).", ACT["MINISTRORUM"] + "; " + ACT["FIDESPERDOCT"], False, OS),
        cc("2022-06-05", "Gains personal prelatures (from Bishops); implemented by m.p. Ad charisma tuendum (2022, not read).", ACT["PE"], False, S),
     ],
     notes="Hard case: the 1967 rename from 'of the Council [of Trent]' to 'for the Clergy' accompanies a redefinition of its subject matter. Under the hypothesis it remains one body; this needs an explicit rule ('a rename stays a rename even when competences are redefined in the same act').")

body(key="lauretana", line="clergy",
     curia_status="Congregation (Loreto); from 1908 a 'special congregation' united to the Congregation of the Council.",
     names=[name("Congregatio Lauretana", "Congregation of Loreto", "1698", "1908-11-03", "Innocent XII, 1698 (CE)", U["CE_CONG"], False, S)],
     kind=[kind("congregation", "1698", "1908-11-03", "CE; Sapienti consilio 4° n.5", False)],
     erected={"date": "1698", "act": "Innocent XII (CE)", "verified": False, "source_type": S},
     ended={"date": "1908-11-03", "act": ACT["SC"], "how": "absorbed", "verified": True, "source_type": P,
            "note": "'Congregationi Concilii adiungitur et unitur, qua Congregatio specialis, ea quae Lauretana dicitur' — united but kept as a 'special congregation'; later fate (lapse) not traced."},
     successors=[link("council-clergy", "absorption", "1908-11-03")])

body(key="revision-of-councils", line="clergy",
     curia_status="Special congregation (19th c.).",
     names=[name("Congregatio specialis pro Conciliorum revisione", "Special Congregation for the Revision of (Provincial) Councils", None, "1908-11-03", "Pius IX (CE: consultors from 1849)", U["CE_CONG"], False, S)],
     kind=[kind("congregation", None, "1908-11-03", "Sapienti consilio 4° n.3", True)],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1908-11-03", "act": ACT["SC"], "how": "suppressed", "verified": True, "source_type": P, "note": "'suppressa Congregatione speciali, quae hactenus fuit, pro Conciliorum revisione'; competence to the Council."},
     successors=[link("council-clergy", "absorption", "1908-11-03")])

# ---------------------------------------------------------------- Bishops
body(key="consistorial-bishops", line="bishops", issues_doctrinal_documents=True,
     curia_status="Congregation 1588-2022 (Sixtine 15; 2nd in 1908 with the Pope as prefect; CIC 1917; REU n.46; PB); dicastery since 2022.",
     names=[
        name("Congregatio pro erectione ecclesiarum et provisionibus consistorialibus", "Congregation for the Erection of Churches and Consistorial Provisions", "1588-01-22", None, ACT["IMMENSA"], U["CE_CONG"], False, S),
        name("Sacra Congregatio Consistorialis", "Sacred Consistorial Congregation", None, "1968-01-01", ACT["SC"], U["SC"], True, P, "Name in use by 1908 (Sapienti consilio 2°); date of adoption of the short name unknown."),
        name("Sacra Congregatio pro Episcopis", "Sacred Congregation for Bishops", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.46."),
        name("Congregatio pro Episcopis", "Congregation for Bishops", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium pro Episcopis", "Dicastery for Bishops", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("congregation", "1588-01-22", "2022-06-05", "Sapienti consilio / CIC 1917 can. 248 / REU / PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1588-01-22", "act": ACT["IMMENSA"], "verified": False, "source_type": S},
     ended=None,
     predecessors=[link("bishops-and-regulars", "absorption", "1908-11-03", "Only the diocesan-government share.")],
     competence_changes=[
        cc("1903-12-17", "Receives the nomination of bishops from the Holy Office (Pius X, Romanis Pontificibus; cited in Sapienti consilio preamble).", ACT["SC"], True),
        cc("1908-11-03", "Gains the government of dioceses formerly with Bishops-and-Regulars and the Council, plus seminaries; resolves competence conflicts among congregations.", ACT["SC"], True),
        cc("1915-11-04", "Seminaries move to the new Congregation of Seminaries and Universities.", ACT["SEMCLER"], True),
        cc("1970-03-19", "Pontifical Commission for migrants placed under it (to 1988).", ACT["APOSTCARIT"], True),
        cc("2022-06-05", "Loses personal prelatures to Clergy.", ACT["PE"], False, S),
     ],
     notes="Name trap: the Sixtine 'Congregation for consultations of Bishops' (later Bishops-and-Regulars) is a DIFFERENT body from this one, although 'Congregation for Bishops' (1967) sounds like its continuation.")

body(key="bishops-consultations-1588", line="religious",
     curia_status="Sixtine congregation (12th of 15).",
     names=[name("Congregatio pro consultationibus Episcoporum et aliorum praelatorum", "Congregation for Consultations of Bishops and other Prelates", "1588-01-22", "1601", ACT["IMMENSA"], U["CE_CONG"], False, S)],
     kind=[kind("congregation", "1588-01-22", "1601", "CE", False)],
     erected={"date": "1588-01-22", "act": ACT["IMMENSA"], "verified": False, "source_type": S},
     ended={"date": "1601", "act": "Clement VIII (act not identified)", "how": "merged", "verified": False, "source_type": S},
     successors=[link("bishops-and-regulars", "merger", "1601")])

body(key="regulars-consultations-1586", line="religious",
     curia_status="Congregation founded 1586, confirmed in Immensa (11th of 15).",
     names=[name("Congregatio super consultationibus regularium", "Congregation for Consultations of Regulars", "1586-05-17", "1601", "Sixtus V, brief of 17 May 1586; confirmed by Immensa aeterni Dei", U["CE_CONG"], False, S)],
     kind=[kind("congregation", "1586-05-17", "1601", "CE", False)],
     erected={"date": "1586-05-17", "act": "Sixtus V brief (CE)", "verified": False, "source_type": S},
     ended={"date": "1601", "act": "Clement VIII (act not identified)", "how": "merged", "verified": False, "source_type": S},
     successors=[link("bishops-and-regulars", "merger", "1601")])

body(key="bishops-and-regulars", line="religious",
     curia_status="Congregation 1601-1908.",
     names=[name("Sacra Congregatio Episcoporum et Regularium", "Congregation of Bishops and Regulars", "1601", "1908-11-03", "Clement VIII, 1601 (CE)", U["CE_CONG"], False, S, "Existence verified by mention in Sapienti consilio (2° n.3) and Seminaria clericorum.")],
     kind=[kind("congregation", "1601", "1908-11-03", "CE", False)],
     erected={"date": "1601", "act": "Clement VIII (CE)", "verified": False, "source_type": S},
     ended={"date": "1908-11-03", "act": ACT["SC"], "how": "suppressed", "verified": True, "source_type": P,
            "note": "Not named as suppressed; omitted from the closed list ('non alia sint ... quam quae praesenti Constitutione decernuntur'). Its diocesan matters go to the Consistorial (2° n.3), its religious matters to the new Congregation of Religious."},
     predecessors=[link("bishops-consultations-1588", "merger", "1601"), link("regulars-consultations-1586", "merger", "1601"),
                   link("state-of-regulars", "absorption", "1698"), link("discipline-of-regulars", "absorption", "1906-05-26")],
     successors=[link("religious-consecrated-life", "split", "1908-11-03"), link("consistorial-bishops", "absorption", "1908-11-03", "Only the diocesan-government share.")])

body(key="state-of-regulars", line="religious",
     curia_status="Minor congregation(s) for the state of regulars (1652-1698; 1847-1906). Treated here as one placeholder; CE describes two distinct bodies.",
     names=[name("Congregatio super statu Regularium", "Congregation on the State of Regulars", "1652-08-15", "1698-08-04", "Innocent X (CE); suppressed by Innocent XII (CE)", U["CE_CONG"], False, S,
                 "A second 'Congregation on the State of Regular Orders' was created by Pius IX on 17 Jun 1847 and suppressed 26 May 1906 (CE). Two bodies with near-identical names; should be split into two keys after verification.")],
     kind=[kind("congregation", "1652-08-15", "1906-05-26", "CE", False)],
     erected={"date": "1652-08-15", "act": "Innocent X (CE)", "verified": False, "source_type": S},
     ended={"date": "1906-05-26", "act": "Pius X, m.p. Sacrae Congregationi super negotiis, 26 May 1906 (cited in Sapienti consilio preamble)", "how": "absorbed", "verified": False, "source_type": S},
     successors=[link("bishops-and-regulars", "absorption", "1906-05-26")])

body(key="discipline-of-regulars", line="religious",
     curia_status="Minor congregation (1695-1906).",
     names=[name("Congregatio super disciplina Regulari", "Congregation on Regular Discipline", "1695-07-18", "1906-05-26", "Innocent XII (CE)", U["CE_CONG"], False, S)],
     kind=[kind("congregation", "1695-07-18", "1906-05-26", "CE", False)],
     erected={"date": "1695-07-18", "act": "Innocent XII (CE)", "verified": False, "source_type": S},
     ended={"date": "1906-05-26", "act": "Pius X, m.p. of 26 May 1906 (cited in Sapienti consilio preamble; content per CE)", "how": "absorbed", "verified": False, "source_type": S},
     successors=[link("bishops-and-regulars", "absorption", "1906-05-26")])

body(key="religious-consecrated-life", line="religious", issues_doctrinal_documents=True,
     curia_status="Congregation 1908-2022 (5th in 1908; CIC 1917 can. 251; REU n.71; PB); dicastery since 2022.",
     names=[
        name("Sacra Congregatio Negotiis religiosorum sodalium praeposita (de Religiosis)", "Sacred Congregation of Religious", "1908-11-03", "1968-01-01", ACT["SC"], U["SC"], True, P, "AAS 1909 page headings use 'S. Congregatio de Religiosis'."),
        name("Sacra Congregatio pro Religiosis et Institutis saecularibus", "Sacred Congregation for Religious and Secular Institutes", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.71."),
        name("Congregatio pro Institutis Vitae Consecratae et Societatibus Vitae Apostolicae", "Congregation for Institutes of Consecrated Life and Societies of Apostolic Life", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium pro Institutis Vitae Consecratae et Societatibus Vitae Apostolicae", "Dicastery for Institutes of Consecrated Life and Societies of Apostolic Life", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("congregation", "1908-11-03", "2022-06-05", "Sapienti consilio / CIC 1917 / REU / PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1908-11-03", "act": ACT["SC"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("bishops-and-regulars", "split", "1908-11-03")],
     notes="Hard case: the 1586 Regulars congregation was merged away in 1601 and its subject matter re-emerged as a new body in 1908. Treated as new body (split) per hypothesis; the Holy See's own narrative may trace the line back to 1586.")

# ---------------------------------------------------------------- Education
body(key="roman-university", line="education",
     curia_status="Sixtine congregation (10th of 15) for the University of Rome.",
     names=[name("Congregatio pro universitate studii Romani", "Congregation for the University of the Roman Study (Sapienza)", "1588-01-22", "1824-08-28", ACT["IMMENSA"], U["CE_CONG"], False, S)],
     kind=[kind("congregation", "1588-01-22", "1824-08-28", "CE", False)],
     erected={"date": "1588-01-22", "act": ACT["IMMENSA"], "verified": False, "source_type": S},
     ended={"date": "1824-08-28", "act": "Leo XII, bull Quod divina sapientia, 28 Aug 1824 (secondary)", "how": "absorbed", "verified": False, "source_type": S, "note": "Whether it lapsed earlier or was refounded is unclear; CE says Leo XII 'created a new congregation'."},
     successors=[link("studies-catholic-education", "re-foundation", "1824-08-28")])

body(key="studies-catholic-education", line="education", issues_doctrinal_documents=True,
     curia_status="Congregation 1824-2022 (11th in 1908; CIC 1917 can. 256; REU n.75; PB). Merged 2022.",
     names=[
        name("Sacra Congregatio Studiorum", "Sacred Congregation of Studies", "1824-08-28", "1915-11-04", "Leo XII, Quod divina sapientia (secondary)", U["SC"], False, S, "Existence and 1908 remit verified (Sapienti consilio 11°); founding act secondary."),
        name("Sacra Congregatio de Seminariis et (de) Studiorum Universitatibus", "Sacred Congregation of Seminaries and Universities", "1915-11-04", "1968-01-01", ACT["SEMCLER"], U["AAS7"], True, P, "CIC 1917 can. 256 has 'de Seminariis et Universitatibus studiorum'."),
        name("Sacra Congregatio pro Institutione catholica", "Sacred Congregation for Catholic Education", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.75: 'Quae hactenus ... de Seminariis et Studiorum Universitatibus nuncupata est, ... nomen sumit Sacrae Congregationis pro Institutione catholica'."),
        name("Congregatio de Seminariis atque Studiorum Institutis / de Institutione Catholica", "Congregation for Catholic Education (for Seminaries and Educational Institutions)", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P, "vatican.va Latin PB heading: 'Congregatio de Seminariis atque Studiorum Institutis'; English page: 'Congregation of Seminaries and Educational Institutions'; common usage 'Congregation for Catholic Education'. Official form needs the Annuario."),
     ],
     kind=[kind("congregation", "1824-08-28", "2022-06-05", "Sapienti consilio / CIC 1917 / REU / PB")],
     erected={"date": "1824-08-28", "act": "Quod divina sapientia (secondary)", "verified": False, "source_type": S},
     ended={"date": "2022-06-05", "act": ACT["PE"], "how": "merged", "verified": True, "source_type": P, "note": "Becomes the Section for Education of the Dicastery for Culture and Education (PE Art. 153 §2)."},
     predecessors=[link("roman-university", "re-foundation", "1824-08-28")],
     successors=[link("culture-education-dicastery", "merger", "2022-06-05")],
     competence_changes=[
        cc("1908-11-03", "Remit extended to all Church universities and faculties worldwide.", ACT["SC"], True),
        cc("1915-11-04", "Seminaries (from the Consistorial) are made a congregation of their own, to which the functions of the Congregation of Studies are added; the Studies cardinals become members ipso iure.", ACT["SEMCLER"], True),
        cc("2013-01-16", "Seminaries move to the Congregation for the Clergy.", ACT["MINISTRORUM"], False, OS),
     ],
     notes="Hard case (1915): Seminaria clericorum creates 'De Seminariis propria iam esto Sacra Congregatio' and then adds to it the functions of the Congregation of Studies, which takes the new combined name. Text never says Studies is suppressed. Reading A: Studies renamed + given seminaries (rename); Reading B: new body absorbing Studies (merger). Here modelled as one continuous body (reading A) — the opposite reading is equally defensible.")

body(key="culture-council", line="culture", issues_doctrinal_documents=True,
     curia_status="Pontifical Council 1982-2022 (in PB list).",
     names=[
        name("Pontificium Consilium pro hominum Cultura", "Pontifical Council for Culture", "1982-05-20", "1989-03-01", ACT["CULTURA82"], U["AAS74"], True, P, "Title verified in AAS 74 index only."),
        name("Pontificium Consilium de Cultura", "Pontifical Council for Culture", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("pontifical council", "1982-05-20", "2022-06-05", "PB Arts. 166-168")],
     erected={"date": "1982-05-20", "act": ACT["CULTURA82"], "verified": True, "source_type": P},
     ended={"date": "2022-06-05", "act": ACT["PE"], "how": "merged", "verified": True, "source_type": P, "note": "Becomes Section for Culture of the Dicastery for Culture and Education (PE Art. 153 §2)."},
     predecessors=[link("non-believers", "merger", "1993-03-25", "Merger in which the result keeps the name of one partner."),
                   link("cultural-heritage-commission", "absorption", "2012-07-30")],
     successors=[link("culture-education-dicastery", "merger", "2022-06-05")],
     competence_changes=[cc("1993-03-25", "Merged with the Council for Dialogue with Non-Believers 'in a single entity that will be called the Pontifical Council for Culture'; two sections.", ACT["INDE"], True, P),
                         cc("2012-07-30", "Absorbs the Pontifical Commission for the Cultural Heritage of the Church.", ACT["PULCHR"], False, OS)],
     notes="Hard case: 1993 is described as a union of two councils into a single entity, but the result keeps one partner's name. Hypothesis says merger => new body; usage says continuity of the Council for Culture.")

body(key="non-believers", line="culture",
     curia_status="Secretariat 1965-1988 (REU n.101 lists it among curial secretariats); Pontifical Council 1988-1993.",
     names=[
        name("Secretariatus pro non credentibus", "Secretariat for Non-Believers", "1965-04-09", "1989-03-01", "Paul VI (founded 1965; act not located in AAS 57)", U["AAS58"], False, S, "Founding by Paul VI verified via Finis Concilio n.11; the date 9 Apr 1965 is secondary."),
        name("Pontificium Consilium pro Dialogo cum Non Credentibus", "Pontifical Council for Dialogue with Non-Believers", "1989-03-01", "1993-03-25", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("secretariat", "1965-04-09", "1989-03-01", "REU n.101"), kind("pontifical council", "1989-03-01", "1993-03-25", "PB")],
     erected={"date": "1965-04-09", "act": "Paul VI (secondary date)", "verified": False, "source_type": S},
     ended={"date": "1993-03-25", "act": ACT["INDE"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("culture-council", "merger", "1993-03-25")])

body(key="cultural-heritage-commission", line="culture",
     curia_status="Pontifical Commission; 1988-1993 inside the Congregation for the Clergy (PB Arts. 99-104), 1993-2012 autonomous.",
     names=[
        name("Pontificia Commissio de Patrimonio Artis et Historiae conservando", "Pontifical Commission for Preserving the Patrimony of Art and History", "1989-03-01", "1993-03-25", ACT["PB"], U["PB_LA"], True, P),
        name("Pontificia Commissio de Bonis Culturalibus Ecclesiae", "Pontifical Commission for the Cultural Heritage (Patrimony) of the Church", "1993-03-25", "2012-07-30", ACT["INDE"], U["INDE"], True, P, "English text of Inde a Pontificatus: 'Pontifical Commission for the Cultural Patrimony of the Church'; Latin from the title of Pulchritudinis fidei."),
     ],
     kind=[kind("commission", "1989-03-01", "2012-07-30", "PB; Inde a Pontificatus")],
     erected={"date": "1989-03-01", "act": ACT["PB"], "verified": True, "source_type": P},
     ended={"date": "2012-07-30", "act": ACT["PULCHR"], "how": "absorbed", "verified": False, "source_type": OS, "note": "Latin title of the m.p.: 'Quibus Pontificia Commissio de Bonis Culturalibus Ecclesiae coniungitur cum Pontificio Consilio de Cultura' (title read from vatican.va listing; body not read)."},
     successors=[link("culture-council", "absorption", "2012-07-30")],
     notes="Hard case: a commission inside a congregation that is detached, made autonomous and renamed in one act (1993), then absorbed (2012).")

body(key="culture-education-dicastery", line="culture", issues_doctrinal_documents=True,
     curia_status="Dicastery since 2022.",
     names=[name("Dicasterium de Cultura et Educatione", "Dicastery for Culture and Education", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified (PE Arts. 153-162); Latin not checked.")],
     kind=[kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "2022-06-05", "act": ACT["PE"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("culture-council", "merger", "2022-06-05"), link("studies-catholic-education", "merger", "2022-06-05")])

# ---------------------------------------------------------------- Unity / Interreligious
body(key="christian-unity", line="unity", issues_doctrinal_documents=True,
     curia_status="Conciliar Secretariat 1960; confirmed 1966; among curial secretariats in REU (n.92); Pontifical Council 1988; dicastery 2022.",
     names=[
        name("Secretariatus ad Christianorum unitatem fovendam", "Secretariat for Promoting Christian Unity", "1960-06-05", "1989-03-01", ACT["SUPERNO"], U["AAS52"], True, P, "Superno Dei nutu n.9 'peculiaris Coetus seu Secretariatus instituitur' (unnamed there); name per Finis Concilio and REU n.92."),
        name("Pontificium Consilium ad Unitatem Christianorum Fovendam", "Pontifical Council for Promoting Christian Unity", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium ad Unitatem Christianorum Fovendam", "Dicastery for Promoting Christian Unity", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("secretariat (conciliar, preparatory)", "1960-06-05", "1966-01-03", "Superno Dei nutu"),
           kind("secretariat (curial)", "1966-01-03", "1989-03-01", "Finis Concilio n.11; REU n.92"),
           kind("pontifical council", "1989-03-01", "2022-06-05", "PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1960-06-05", "act": ACT["SUPERNO"], "verified": True, "source_type": P},
     ended=None,
     notes="Hard case: founded as a body for preparing a Council (not a curial organ), then confirmed as permanent (1966). The kind changes without a new body. Commission for Religious Relations with the Jews (1974) attached — not traced.")

body(key="interreligious-dialogue", line="interreligious", issues_doctrinal_documents=True,
     curia_status="Secretariat 1964 (REU n.96); Pontifical Council 1988; dicastery 2022.",
     names=[
        name("Secretariatus de non Christianis / pro non christianis", "Secretariat for Non-Christians", "1964-05-19", "1989-03-01", ACT["PROGREDIENTE"], U["AAS56"], True, P, "1964 act: 'Secretariatum de non Christianis'; REU n.96: 'Secretariatus pro non christianis'."),
        name("Pontificium Consilium pro Dialogo inter Religiones", "Pontifical Council for Interreligious Dialogue", "1989-03-01", "2022-06-05", ACT["PB"], U["PB_LA"], True, P),
        name("Dicasterium pro Dialogo Interreligioso", "Dicastery for Interreligious Dialogue", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("secretariat", "1964-05-19", "1989-03-01", "Progrediente Concilio; REU"), kind("pontifical council", "1989-03-01", "2022-06-05", "PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1964-05-19", "act": ACT["PROGREDIENTE"], "verified": True, "source_type": P},
     ended=None,
     notes="2006-2007: placed under the president of the Council for Culture (personal union, not a merger) — secondary, unverified; a test of whether a shared head implies a merged body (it should not).")

# ---------------------------------------------------------------- Laity / Family / Life
body(key="laity-council", line="laity",
     curia_status="Consilium de Laicis (1967, ad experimentum 5 years; REU n.103); Pontifical Council 1976-2016.",
     names=[
        name("Consilium de Laicis", "Council of the Laity", "1967-01-06", "1976-12-10", ACT["CATHOLICAM"], U["AAS59"], True, P, "Constituted 'experimenti gratia ... ad quinquennium' (n.7)."),
        name("Pontificium Consilium pro Laicis", "Pontifical Council for the Laity", "1976-12-10", "2016-09-01", ACT["APOSTOLATUS"], U["AAS68"], True, P, "'Consilium de Laicis in posterum appellabitur Pontificium Consilium pro Laicis'."),
     ],
     kind=[kind("council (experimental)", "1967-01-06", "1976-12-10", "Catholicam Christi Ecclesiam"), kind("pontifical council", "1976-12-10", "2016-09-01", "Apostolatus peragendi; PB")],
     erected={"date": "1967-01-06", "act": ACT["CATHOLICAM"], "verified": True, "source_type": P},
     ended={"date": "2016-09-01", "act": ACT["SEDULA"], "how": "merged", "verified": True, "source_type": P, "note": "'definitive cessation' of the Councils for the Laity and for the Family; competences transferred from 1 Sep 2016."},
     successors=[link("laity-family-life", "merger", "2016-09-01")],
     competence_changes=[cc("1985-02-11", "Health-care commission associated with it as 'complens pars' (to 1988).", ACT["DOLENTIUM"], True)],
     notes="1976 is rename + permanent status + new internal order in one act (hard case, same pattern as 1965 CDF).")

body(key="family-committee", line="laity",
     curia_status="Committee/Council for the Family within the Laity council (1973); not a separate dicastery.",
     names=[name("Consilium de Familia (Comitatus pro Familia)", "Committee for the Family", "1973-01-11", "1981-05-09", "Paul VI, 11 Jan 1973 (act not read)", U["AAS73"], False, S, "Its name 'Consilium de Familia' and its cessation verified in Familia a Deo instituta; founding date secondary.")],
     kind=[kind("committee", "1973-01-11", "1981-05-09", "secondary", False)],
     erected={"date": "1973-01-11", "act": "Paul VI (secondary)", "verified": False, "source_type": S},
     ended={"date": "1981-05-09", "act": ACT["FAMILIA"], "how": "suppressed", "verified": True, "source_type": P, "note": "'Pontificium Consilium pro Familia conditur, quod Consilio de Familia succedit eique sufficitur; quare hoc iam ilico cessat'."},
     successors=[link("family-council", "re-foundation", "1981-05-09", "Explicit succession: new body 'succeeds' the old, which ceases.")])

body(key="family-council", line="laity", issues_doctrinal_documents=True,
     curia_status="Pontifical Council 1981-2016 (PB).",
     names=[name("Pontificium Consilium pro Familia", "Pontifical Council for the Family", "1981-05-09", "2016-09-01", ACT["FAMILIA"], U["AAS73"], True, P)],
     kind=[kind("pontifical council", "1981-05-09", "2016-09-01", "Familia a Deo instituta; PB")],
     erected={"date": "1981-05-09", "act": ACT["FAMILIA"], "verified": True, "source_type": P},
     ended={"date": "2016-09-01", "act": ACT["SEDULA"], "how": "merged", "verified": True, "source_type": P},
     predecessors=[link("family-committee", "re-foundation", "1981-05-09")],
     successors=[link("laity-family-life", "merger", "2016-09-01")])

body(key="laity-family-life", line="laity", issues_doctrinal_documents=True,
     curia_status="Dicastery since 2016.",
     names=[name("Dicasterium pro Laicis, Familia et Vita", "Dicastery for the Laity, the Family and Life", "2016-09-01", None, ACT["SEDULA"], U["SEDULA"], True, P, "Instituted 15 Aug 2016; competences transfer 1 Sep 2016. Name unchanged by PE (Arts. 128-141).")],
     kind=[kind("dicastery", "2016-09-01", None, "Sedula Mater; PE")],
     erected={"date": "2016-08-15", "act": ACT["SEDULA"], "verified": True, "source_type": P, "note": "Two candidate erection dates: act date 15 Aug 2016 vs operative date 1 Sep 2016."},
     ended=None,
     predecessors=[link("laity-council", "merger", "2016-09-01"), link("family-council", "merger", "2016-09-01")],
     notes="'Life' in the name corresponds to no predecessor dicastery (the Pontifical Academy for Life is not a curial body); a newly named competence at merger time.")

# ---------------------------------------------------------------- Justice/peace / integral human development
body(key="justice-peace", line="human-development", issues_doctrinal_documents=True,
     curia_status="Pontifical Commission 1967 (REU n.103), definitively ordered 1976; Pontifical Council 1988-2016.",
     names=[
        name("Pontificia Commissio Studiosorum a «Iustitia et Pace»", "Pontifical Commission 'Justice and Peace'", "1967-01-06", "1989-03-01", ACT["CATHOLICAM"], U["AAS59"], True, P),
        name("Pontificium Consilium de Iustitia et Pace", "Pontifical Council for Justice and Peace", "1989-03-01", "2017-01-01", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("commission", "1967-01-06", "1989-03-01", "Catholicam Christi Ecclesiam; Iustitiam et pacem (1976)"), kind("pontifical council", "1989-03-01", "2017-01-01", "PB")],
     erected={"date": "1967-01-06", "act": ACT["CATHOLICAM"], "verified": True, "source_type": P},
     ended={"date": "2017-01-01", "act": ACT["HUMANAM"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("integral-human-development", "merger", "2017-01-01")],
     competence_changes=[cc("1976-12-10", "'certa ac definita ordinatione donatur' (made permanent).", ACT["IUSTITIAM"], True)])

body(key="cor-unum", line="human-development",
     curia_status="Pontifical Council 1971-2016 (PB).",
     names=[name("Pontificium Consilium «Cor Unum» de humana et christiana progressione fovenda", "Pontifical Council Cor Unum", "1971-07-15", "2017-01-01", ACT["AMORIS"], U["AAS63"], True, P, "Title verified from AAS 63 index; PB: 'Pontificium Consilium «Cor Unum»'.")],
     kind=[kind("pontifical council", "1971-07-15", "2017-01-01", "Amoris officio; PB")],
     erected={"date": "1971-07-15", "act": ACT["AMORIS"], "verified": True, "source_type": P},
     ended={"date": "2017-01-01", "act": ACT["HUMANAM"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("integral-human-development", "merger", "2017-01-01")])

body(key="migrants", line="human-development",
     curia_status="Commission subject to the Congregation for Bishops (1970-1988); Pontifical Council 1988-2016.",
     names=[
        name("Pontificia Commissio de spirituali migratorum atque itinerantium cura", "Pontifical Commission for the Spiritual Care of Migrants and Itinerant People", "1970-03-19", "1989-03-01", ACT["APOSTCARIT"], U["AAS62"], True, P, "'Sacrae Congregationi pro Episcopis obnoxiam'; its president is the Prefect of Bishops."),
        name("Pontificium Consilium de Spirituali Migrantium atque Itinerantium Cura", "Pontifical Council for the Pastoral Care of Migrants and Itinerant People", "1989-03-01", "2017-01-01", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("commission (inside a congregation)", "1970-03-19", "1989-03-01", "Apostolicae caritatis"), kind("pontifical council", "1989-03-01", "2017-01-01", "PB")],
     erected={"date": "1970-03-19", "act": ACT["APOSTCARIT"], "verified": True, "source_type": P},
     ended={"date": "2017-01-01", "act": ACT["HUMANAM"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("integral-human-development", "merger", "2017-01-01")],
     notes="After 2017 a 'Migrants and Refugees Section' of the new dicastery was placed directly under the Pope ad tempus (dicastery statutes; not verified). A sub-unit with its own reporting line — hard for a flat registry.")

body(key="health-care", line="human-development",
     curia_status="Commission associated with the Council for the Laity (1985-1988); Pontifical Council 1988-2016.",
     names=[
        name("Pontificia Commissio de Apostolatu pro Valetudinis Administris", "Pontifical Commission for the Apostolate of Health Care Workers", "1985-02-11", "1989-03-01", ACT["DOLENTIUM"], U["AAS77"], True, P, "'Consociari hanc Commissionem ... cum Pontificio Consilio pro Laicis, cuius complens sit ipsa pars'."),
        name("Pontificium Consilium de Apostolatu pro Valetudinis Administris", "Pontifical Council for Pastoral Assistance to Health Care Workers", "1989-03-01", "2017-01-01", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("commission (part of a council)", "1985-02-11", "1989-03-01", "Dolentium hominum"), kind("pontifical council", "1989-03-01", "2017-01-01", "PB")],
     erected={"date": "1985-02-11", "act": ACT["DOLENTIUM"], "verified": True, "source_type": P},
     ended={"date": "2017-01-01", "act": ACT["HUMANAM"], "how": "merged", "verified": True, "source_type": P},
     successors=[link("integral-human-development", "merger", "2017-01-01")])

body(key="integral-human-development", line="human-development", issues_doctrinal_documents=True,
     curia_status="Dicastery since 2017.",
     names=[name("Dicasterium pro Integra Humana Progressione Fovenda (Latin unverified)", "Dicastery for Promoting Integral Human Development", "2017-01-01", None, ACT["HUMANAM"], U["HUMANAM"], True, P,
                 "Italian/Spanish titles say 'servizio dello sviluppo umano integrale' rather than 'promoting'; name confirmed in PE Arts. 163-174.")],
     kind=[kind("dicastery", "2017-01-01", None, "Humanam progressionem; PE")],
     erected={"date": "2016-08-17", "act": ACT["HUMANAM"], "verified": True, "source_type": P, "note": "Instituted 17 Aug 2016, operative 1 Jan 2017."},
     ended=None,
     predecessors=[link("justice-peace", "merger", "2017-01-01"), link("cor-unum", "merger", "2017-01-01"), link("migrants", "merger", "2017-01-01"), link("health-care", "merger", "2017-01-01")])

body(key="papal-almonry-charity", line="charity",
     curia_status="Office of the papal household; in PB an 'institution adhering to the Holy See' (Part IX, Arts. 186-193), NOT a dicastery; since 2022 a dicastery (PE Art. 79).",
     names=[
        name("Eleemosynarius Secretus (office of)", "Secret Almoner / Apostolic Almonry", None, "1968-03-28", "medieval origins (not traced)", None, False, S),
        name("Eleemosynaria Apostolica (office of the Eleemosynarius Sanctitatis Suae)", "Office of Papal Charities", "1968-03-28", "2022-06-05", ACT["PONTDOMUS"] + "; " + ACT["PB"] + " Art. 193", U["AAS60"], True, P, "1968: 'Eleemosynarius Secretus ... Eleemosynarius Sanctitatis Suae ... appellabitur' (rename of the office-holder)."),
        name("Dicasterium de Caritatis Servitio (Latin unverified)", "Dicastery for the Service of Charity ('also known as the Office of the Papal Almoner')", "2022-06-05", None, ACT["PE"], U["PE"], True, P, "PE Art. 79."),
     ],
     kind=[kind("office (papal household)", None, "1989-03-01", "Pontificalis Domus", False), kind("institution adhering to the Holy See", "1989-03-01", "2022-06-05", "PB Part IX"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": None, "act": "medieval; not traced", "verified": False, "source_type": S},
     ended=None,
     notes="Hard case: a body outside the Curia promoted into it as a dicastery, renamed, and keeping its old name as an alias in the founding text itself. Under the hypothesis it is the same body (rename + kind change).")

# ---------------------------------------------------------------- Legislative texts
body(key="code-interpretation-1917", line="legislative",
     curia_status="Pontifical commission (1917-1983/84); not among the curial congregations.",
     names=[name("Pontificia Commissio ad Codicis canones authentice interpretandos", "Pontifical Commission for the Authentic Interpretation of the Code of Canon Law", "1917-09-15", "1984-01-02", ACT["CUMIURIS"], U["AAS9I"], True, P, "Title/date from AAS 9-I index; its continuation until 1984 is assumed, not verified.")],
     kind=[kind("commission", "1917-09-15", "1984-01-02", "Cum iuris canonici Codicem")],
     erected={"date": "1917-09-15", "act": ACT["CUMIURIS"], "verified": True, "source_type": P},
     ended={"date": "1984-01-02", "act": ACT["RECOGNITO"], "how": "suppressed", "verified": False, "source_type": INF, "note": "Recognito does not suppress it in the text read; it 'follows the footsteps' of Benedict XV and erects a new commission. End date of the 1917 commission (with the 1983 Code coming into force?) needs the Annuario."},
     successors=[link("legislative-texts", "re-foundation", "1984-01-02", "Lineage by imitation, not by explicit succession.")])

body(key="code-revision-1963", line="legislative",
     curia_status="Pontifical commission for the revision of the Code (1963-1983).",
     names=[name("Pontificia Commissio Codici Iuris Canonici Recognoscendo", "Pontifical Commission for the Revision of the Code of Canon Law", "1963-03-28", "1983", "John XXIII, 28 Mar 1963 (not read)", U["AAS58"], False, S, "Existence confirmed in Finis Concilio (1966); dates secondary.")],
     kind=[kind("commission", "1963-03-28", "1983", "secondary", False)],
     erected={"date": "1963-03-28", "act": "John XXIII (secondary)", "verified": False, "source_type": S},
     ended={"date": "1983", "act": "task completed with promulgation of CIC 1983 (secondary)", "how": "suppressed", "verified": False, "source_type": S},
     successors=[])

body(key="legislative-texts", line="legislative", issues_doctrinal_documents=False,
     curia_status="Commission 1984; Pontifical Council 1988 (PB); dicastery 2022.",
     names=[
        name("Pontificia Commissio Codici Iuris Canonici authentice interpretando", "Pontifical Commission for the Authentic Interpretation of the Code of Canon Law", "1984-01-02", "1989-03-01", ACT["RECOGNITO"], U["AAS76"], True, P),
        name("Pontificium Consilium de Legum Textibus Interpretandis", "Pontifical Council for the Interpretation of Legislative Texts", "1989-03-01", "1999", ACT["PB"], U["PB_LA"], True, P),
        name("Pontificium Consilium de Legum Textibus", "Pontifical Council for Legislative Texts", "1999", "2022-06-05", "act not identified", U["BNF_PCLT"], False, S, "1999 rename from a BnF authority record only; Annuario needed."),
        name("Dicasterium de Legum Textibus", "Dicastery for Legislative Texts", "2022-06-05", None, ACT["PE"], U["PE"], False, P, "English verified; Latin not checked."),
     ],
     kind=[kind("commission", "1984-01-02", "1989-03-01", "Recognito"), kind("pontifical council", "1989-03-01", "2022-06-05", "PB"), kind("dicastery", "2022-06-05", None, "PE")],
     erected={"date": "1984-01-02", "act": ACT["RECOGNITO"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("code-interpretation-1917", "re-foundation", "1984-01-02")],
     notes="Issues authentic interpretations (legal, not doctrinal). The 1967 Pontifical Commission for interpreting the decrees of Vatican II (and the 1966 Central Commission of Finis Concilio n.5) are further candidate predecessors — not traced.")

# ---------------------------------------------------------------- Communications
body(key="social-communications", line="communication",
     curia_status="Pontifical commission/council 1948-2016 (various names); a 'Council' in PB.",
     names=[
        name("(Pontifical Commission for didactic and religious cinema; later for cinema, radio and television)", "Pontifical Commission for Cinema / Cinema, Radio and Television", "1948", "1959-02-22", "Pius XII (acts not read)", None, False, S),
        name("Pontificium Consilium (de re cinematographica, radiophonica ac televisifica)", "Pontifical Commission for Cinema, Radio and Television", "1959-02-22", "1964-04-02", "John XXIII, m.p. Boni Pastoris, 22 Feb 1959, AAS 51 (1959) 183-187 (cited in In fructibus multis; date secondary)", U["AAS56"], False, P,
             "In fructibus multis says Boni Pastoris made it 'firmum ac stabile' and that it was aggregated to the Office for Public Affairs of the Church."),
        name("Pontificium Consilium instrumentis communicationis socialis praepositum", "Pontifical Commission for Social Communications", "1964-04-02", "1989-03-01", ACT["INFRUCTIBUS"], U["AAS56"], True, P, "'commemorati Consilii mutato nomine et munerum provincia amplificata'. Latin 'Consilium' is rendered 'Commission' in English usage."),
        name("Pontificium Consilium de Communicationibus Socialibus", "Pontifical Council for Social Communications", "1989-03-01", "2016", ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("commission", "1948", "1989-03-01", "secondary / In fructibus multis", False), kind("pontifical council", "1989-03-01", "2016", "PB")],
     erected={"date": "1948", "act": "Pius XII (secondary)", "verified": False, "source_type": S},
     ended={"date": "2016", "act": ACT["SPC2015"] + " (merger to be carried out in stages)", "how": "absorbed", "verified": False, "source_type": OS, "note": "L'attuale contesto comunicativo lists it first among the bodies to be combined into the Secretariat; the exact date of its extinction is not stated in the act read."},
     successors=[link("communication-dicastery", "absorption", "2016")],
     notes="Hard case (1964): explicit 'rename + enlarged competence' — the cleanest primary-source example of the rename-with-new-competences problem.")

body(key="communication-dicastery", line="communication",
     curia_status="Secretariat (a 'new Dicastery of the Roman Curia') 2015; renamed Dicastery 2018; PE.",
     names=[
        name("Secretaria pro Communicatione", "Secretariat for Communication", "2015-06-29", "2018-06-23", ACT["SPC2015"], U["SPC2015"], True, P, "Instituted 27 Jun 2015, functioning from 29 Jun 2015 (Art. 4)."),
        name("Dicasterium pro Communicatione", "Dicastery for Communication", "2018-06-23", None, ACT["RESCRIPT2018"], U["RESCRIPT2018"], False, OS, "Rescript dated (audience) 27 Feb 2018, published and in force 23 Jun 2018 — per press-office bulletin as summarised by search; bulletin not read directly."),
     ],
     kind=[kind("secretariat (dicastery)", "2015-06-29", "2018-06-23", "L'attuale contesto comunicativo"), kind("dicastery", "2018-06-23", None, "rescript 2018; PE", False)],
     erected={"date": "2015-06-27", "act": ACT["SPC2015"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("social-communications", "absorption", "2016")],
     notes="Absorbed nine bodies, most of them non-curial media institutions (Vatican Radio, L'Osservatore Romano, press office, etc.).")

# ---------------------------------------------------------------- Secretariat of State and diplomatic line
body(key="secretariat-of-state", line="state",
     curia_status="Office (1908, 1917); first 'dicastery' in REU (Secretaria Status seu Papalis, n.19) and PB; in PE a curial institution distinct from the dicasteries ('the Secretariat of State, the Dicasteries and other Institutions', Art. 12).",
     names=[
        name("Secretaria Status (seu Papalis)", "Secretariat of State", "15th-17th c.", None, "no founding act (Quo aptius: 'cuius initium saeculo xv tribuitur — Camera Secreta tunc dicebatur')", U["AAS65"], True, P),
     ],
     kind=[kind("office", None, "1968-01-01", "Sapienti consilio III 4°; CIC 1917 can. 263"), kind("dicastery", "1968-01-01", "2022-06-05", "REU; PB Art. 2"), kind("secretariat (curial institution, not a dicastery)", "2022-06-05", None, "PE Art. 12")],
     erected={"date": None, "act": None, "verified": False, "source_type": P, "note": "Gradual origin; no erection act."},
     ended=None,
     predecessors=[link("apostolic-briefs-secretariat", "absorption", "1968-01-01"), link("briefs-to-princes", "absorption", "1968-01-01"),
                   link("apostolic-chancery", "absorption", "1973-02-27"), link("public-affairs-extraordinary", "absorption", "1989-03-01")],
     competence_changes=[
        cc("1908-11-03", "Three parts: extraordinary affairs (headed by the Secretary of the Congregation for Extraordinary Ecclesiastical Affairs), ordinary affairs (Substitute), and expedition of Apostolic Briefs (Chancellor of Briefs).", ACT["SC"], True),
        cc("1968-01-01", "Absorbs the Secretariat of Apostolic Briefs, Briefs to Princes and Latin Letters (as stated retrospectively in Quo aptius); the Council for Public Affairs is separate from it.", ACT["REU"] + "; " + ACT["QUOAPTIUS"], True),
        cc("1973-02-27", "Absorbs the Apostolic Chancery (Cancellaria Litterarum Apostolicarum).", ACT["QUOAPTIUS"], True),
        cc("1989-03-01", "Two sections: General Affairs; Relations with States (= former Council for Public Affairs).", ACT["PB"], True),
        cc("2017-11-21", "Third section for diplomatic personnel (date secondary; existence verified in PE Art. 45 §2).", "Francis, letter of 21 Nov 2017 (not read)", False, S),
     ],
     notes="Hard case for 'kind': it is an office (1908), a dicastery (1967-2022) and then explicitly not one of the dicasteries (2022), with no change of identity.")

body(key="public-affairs-extraordinary", line="state",
     curia_status="Congregation 1814-1967 (10th in 1908; CIC 1917 can. 255); 'Sacrum Consilium' 1967-1988 (REU n.26); absorbed into the Secretariat of State as its Second Section in 1988.",
     names=[
        name("Congregatio super negotiis ecclesiasticis regni Galliarum", "Congregation for the Ecclesiastical Affairs of the Kingdom of France", "1793", "1814", "Pius VI (CE)", U["CE_CONG"], False, S, "CE: created 1793, renamed 1805, lapsed 1809, re-established 1814, renamed 1827."),
        name("Sacra Congregatio pro Negotiis ecclesiasticis extraordinariis", "Sacred Congregation for Extraordinary Ecclesiastical Affairs", "1814", "1968-01-01", ACT["SC"], U["SC"], True, P, "Name verified for 1908; 1814/1827 dates secondary."),
        name("Sacrum Consilium pro Publicis Ecclesiae negotiis", "Council for the Public Affairs of the Church", "1968-01-01", "1989-03-01", ACT["REU"], U["REU"], True, P, "REU n.26: 'Congregatio quae hactenus vocabatur ... appellabitur Sacrum Consilium ...'"),
     ],
     kind=[kind("congregation", "1793", "1968-01-01", "Sapienti consilio; CIC 1917"), kind("council (separate from the Secretariat of State)", "1968-01-01", "1989-03-01", "REU")],
     erected={"date": "1793", "act": "Pius VI (CE)", "verified": False, "source_type": S},
     ended={"date": "1989-03-01", "act": ACT["PB"], "how": "absorbed", "verified": True, "source_type": P, "note": "Becomes the 'Section for Relations with States' (PB Art. 40, 45-47)."},
     successors=[link("secretariat-of-state", "absorption", "1989-03-01")],
     notes="Hard case: congregation -> council (rename + kind change, 1967) -> section of another body (1988). Also: suppressed 1809 and re-established 1814 (secondary) — suppression and re-foundation under (nearly) the same name.")

body(key="apostolic-briefs-secretariat", line="state",
     curia_status="Office (Secretaria Brevium); from 1908 the third part of the Secretariat of State under the Chancellor of Briefs.",
     names=[name("Secretaria Brevium (Apostolicorum)", "Secretariat of (Apostolic) Briefs", "late 14th c.", "1968-01-01", "no founding act (Quo aptius)", U["AAS65"], True, P)],
     kind=[kind("office", None, "1968-01-01", "Quo aptius; Sapienti consilio III 4°")],
     erected={"date": None, "act": None, "verified": False, "source_type": P},
     ended={"date": "1968-01-01", "act": ACT["REU"] + " (as stated in " + ACT["QUOAPTIUS"] + ")", "how": "absorbed", "verified": True, "source_type": P,
            "note": "Already a part of the Secretariat of State from 1908; Quo aptius says it 'iam transisse ad Secretariam Status' under REU. Arguably absorbed in 1908."},
     successors=[link("secretariat-of-state", "absorption", "1968-01-01")])

body(key="briefs-to-princes", line="state",
     curia_status="Office (1908 Sapienti consilio III 5°; CIC 1917 can. 264).",
     names=[name("Secretariae Brevium ad Principes et Epistolarum latinarum", "Secretariat of Briefs to Princes and of Latin Letters", None, "1968-01-01", ACT["SC"], U["SC"], True, P, "Two offices described as one 'duplex Officium'.")],
     kind=[kind("office", None, "1968-01-01", "Sapienti consilio; CIC 1917")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1968-01-01", "act": ACT["REU"] + " (n.134; and " + ACT["QUOAPTIUS"] + ")", "how": "absorbed", "verified": True, "source_type": P,
            "note": "REU n.134 lets the two secretaries continue 'donec aliter provideatur'; Quo aptius (1973) states they had passed to the Secretariat of State. Exact end date of the offices (vs their holders) unclear."},
     successors=[link("secretariat-of-state", "absorption", "1968-01-01")])

body(key="apostolic-chancery", line="state",
     curia_status="Office (1908, CIC 1917, REU n.114).",
     names=[name("Cancellaria Apostolica", "Apostolic Chancery", "medieval", "1973-02-27", "no founding act", U["SC"], True, P, "1908: head titled Cancellarius instead of Vice-Cancellarius.")],
     kind=[kind("office", None, "1973-02-27", "Sapienti consilio; CIC 1917; REU")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1973-02-27", "act": ACT["QUOAPTIUS"], "how": "absorbed", "verified": True, "source_type": P, "note": "'Officium Cancellariae Apostolicae in Romana Curia uti tale esse desinit'; its business goes to a 'Cancellaria Litterarum Apostolicarum' inside the Secretariat of State."},
     successors=[link("secretariat-of-state", "absorption", "1973-02-27")])

body(key="apostolic-datary", line="state",
     curia_status="Office (1908 Sapienti consilio III 2°; CIC 1917 can. 261).",
     names=[name("Dataria Apostolica", "Apostolic Datary", "medieval", "1968-01-01", "no founding act", U["SC"], True, P, "1908: head titled Datarius instead of Pro-Datarius.")],
     kind=[kind("office", None, "1968-01-01", "Sapienti consilio; CIC 1917")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1968-01-01", "act": ACT["REU"], "how": "suppressed", "verified": False, "source_type": INF,
            "note": "REU never names the Datary: the word does not occur in the text. It is simply missing from the list of offices, and the preamble says only 'quibusdam suppressis'. Secondary (Wikipedia citing Jedin) says REU abrogated it. Successor of its residual functions not identified."},
     successors=[])

body(key="apostolic-camera", line="economic",
     curia_status="Office (1908, CIC 1917 can. 262, REU n.122, PB Art. 171). PE names the office 'Camerlengo of the Holy Roman Church' (Arts. 235-237).",
     names=[
        name("Camera Apostolica", "Apostolic Camera", "medieval", "2022-06-05", "no founding act", U["SC"], True, P),
        name("Camerarius Sanctae Romanae Ecclesiae (office of)", "Camerlengo of the Holy Roman Church", "2022-06-05", None, ACT["PE"], U["PE"], True, P, "PE Art. 12 §3 lists the Camerlengo among the Offices; the term 'Camera Apostolica' was not found in the portion of PE read."),
     ],
     kind=[kind("office", None, None, "Sapienti consilio; CIC 1917; REU; PB; PE")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended=None,
     notes="Hard case: an institution whose name in the 2022 constitution becomes the title of its officeholder.")

body(key="apsa", line="economic",
     curia_status="Office (REU n.123; PB Arts. 172-175; PE Arts. 219-221).",
     names=[name("Administratio Patrimonii Sedis Apostolicae", "Administration of the Patrimony of the Apostolic See", "1968-01-01", None, ACT["REU"], U["REU"], True, P, "REU dated 15 Aug 1967; 'erected 15 Aug 1967' in secondary sources.")],
     kind=[kind("office", "1968-01-01", None, "REU; PB; PE")],
     erected={"date": "1967-08-15", "act": ACT["REU"], "verified": True, "source_type": P},
     ended=None,
     notes="Antecedents (Administration of the Goods of the Holy See, Special Administration of 1929) not traced.")

body(key="prefecture-economic-affairs", line="economic",
     curia_status="Office (REU n.117; PB Arts. 176-179).",
     names=[name("Praefectura rerum oeconomicarum Sanctae Sedis", "Prefecture for the Economic Affairs of the Holy See", "1968-01-01", "2016-12-30", ACT["REU"], U["REU"], True, P)],
     kind=[kind("office", "1968-01-01", "2016-12-30", "REU; PB")],
     erected={"date": "1967-08-15", "act": ACT["REU"], "verified": True, "source_type": P},
     ended={"date": "2016-12-30", "act": "act not identified", "how": "suppressed", "verified": False, "source_type": S, "note": "Date from Wikipedia only; Catholic-Hierarchy says 2016. Functions overtaken by the Secretariat for the Economy."},
     successors=[link("secretariat-economy", "absorption", "2016-12-30", "Functional, not formal, successor.")])

body(key="secretariat-economy", line="economic",
     curia_status="Dicastery of the Roman Curia (FDP n.4); PE Arts. 212-218.",
     names=[name("Secretaria pro Re Oeconomica", "Secretariat for the Economy", "2014-02-24", None, ACT["FDP"], U["FDP"], True, P)],
     kind=[kind("secretariat (dicastery)", "2014-02-24", None, "FDP n.4; PE")],
     erected={"date": "2014-02-24", "act": ACT["FDP"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("prefecture-economic-affairs", "absorption", "2016-12-30")])

body(key="council-economy", line="economic",
     curia_status="Council (FDP 2014); PE Arts. 205-211.",
     names=[name("Consilium pro Re Oeconomica", "Council for the Economy", "2014-02-24", None, ACT["FDP"], U["FDP"], True, P)],
     kind=[kind("council", "2014-02-24", None, "FDP; PE")],
     erected={"date": "2014-02-24", "act": ACT["FDP"], "verified": True, "source_type": P},
     ended=None,
     notes="FDP does NOT state that it replaces the Council of Cardinals for the Study of Organizational and Economic Problems of the Holy See (1981); it only says that body was consulted. Any succession is inferred.")

body(key="auditor-general", line="economic",
     curia_status="Office (FDP 2014: 'Auditor General'); PE Arts. 222-224 'Office of the Auditor General'.",
     names=[name("Revisor Generalis (Officium)", "Office of the Auditor General", "2014-02-24", None, ACT["FDP"], U["FDP"], True, P, "FDP creates the post of Auditor General; 'Office' wording verified in PE.")],
     kind=[kind("office", "2014-02-24", None, "FDP; PE")],
     erected={"date": "2014-02-24", "act": ACT["FDP"], "verified": True, "source_type": P},
     ended=None)

body(key="donations-commission", line="economic",
     curia_status="Commission connected with the Holy See (2025); not shown to be part of the Curia.",
     names=[name("Commissio de donationibus pro Sancta Sede", "Commission for Donations for the Holy See", "2025-02-11", "2025-12-04", "Francis, chirograph Vinculum unitatis et caritatis, 11 Feb 2025", U["VINC2025F"], False, OS)],
     kind=[kind("commission", "2025-02-11", "2025-12-04", "chirograph", False)],
     erected={"date": "2025-02-11", "act": "Francis, chirograph Vinculum unitatis et caritatis", "verified": False, "source_type": OS},
     ended={"date": "2025-12-04", "act": "Leo XIV, chirograph Vinculum unitatis et caritatis, 29 Sep 2025 (published 4 Dec 2025), Art. 1", "how": "suppressed", "verified": True, "source_type": P,
            "note": "Suppressed 'a partire dalla promulgazione'; pending matters to the Secretariat for the Economy (Art. 5); assets to the Holy See via APSA (Art. 4). The founding and the suppressing chirographs share the same title — an identifier collision for document keys."},
     successors=[])

# ---------------------------------------------------------------- Tribunals
body(key="apostolic-penitentiary", line="tribunals",
     curia_status="Tribunal throughout (1908, CIC 1917, REU, PB, PE).",
     names=[name("Sacra Paenitentiaria (Poenitentiaria) Apostolica", "Apostolic Penitentiary", "medieval", None, "no founding act", U["SC"], True, P)],
     kind=[kind("tribunal", None, None, "Sapienti consilio; CIC 1917; REU; PB; PE")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended=None,
     competence_changes=[
        cc("1908-11-03", "Restricted to the internal forum; external-forum matrimonial dispensations go to the Congregation of the Sacraments.", ACT["SC"], True),
        cc("1917-03-25", "Receives all of indulgences (from the Holy Office) with the Holy Office's indulgence section.", ACT["ALLOQ"], True),
     ])

body(key="roman-rota", line="tribunals",
     curia_status="Tribunal (restored 1908; CIC 1917; REU; PB; PE).",
     names=[
        name("Sacra Romana Rota", "Sacred Roman Rota", "medieval", "1989-03-01", ACT["SC"], U["SC"], True, P),
        name("Tribunal Rotae Romanae", "Tribunal of the Roman Rota", "1989-03-01", None, ACT["PB"], U["PB_LA"], True, P),
     ],
     kind=[kind("tribunal", None, None, "Sapienti consilio; PB; PE")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended=None,
     notes="Hard case: by 1908 it had 'almost ceased to judge' and Sapienti consilio 'rursus in exercitium revocamus' with a new Lex propria. Revival of a dormant body — treated as continuity.")

body(key="signatura-gratiae", line="tribunals",
     curia_status="Sixtine congregation (2nd of 15, 'Signatura gratiae'); with the Signatura iustitiae formed the old 'tribunalia Signaturae papalis gratiae et iustitiae'.",
     names=[name("Signatura gratiae / Signatura iustitiae", "Signatures of Grace and of Justice", "medieval/1588", "1908-11-03", ACT["IMMENSA"], U["SC"], False, S, "Suppression verified; origins secondary. Possibly two bodies; kept as one placeholder.")],
     kind=[kind("congregation / tribunal", None, "1908-11-03", "Sapienti consilio II 3°", False)],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1908-11-03", "act": ACT["SC"], "how": "suppressed", "verified": True, "source_type": P, "note": "'antiqua ordinatione tribunalium Signaturae papalis gratiae et iustitiae suppressa'."},
     successors=[link("apostolic-signatura", "re-foundation", "1908-11-03")])

body(key="apostolic-signatura", line="tribunals",
     curia_status="Supreme tribunal (1908; CIC 1917; REU n.104; PB; PE).",
     names=[
        name("Signatura Apostolica / Supremum Signaturae Apostolicae Tribunal", "Supreme Tribunal of the Apostolic Signatura", "1908-11-03", None, ACT["SC"], U["SC"], True, P),
     ],
     kind=[kind("tribunal", "1908-11-03", None, "Sapienti consilio; PB; PE")],
     erected={"date": "1908-11-03", "act": ACT["SC"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("signatura-gratiae", "re-foundation", "1908-11-03")],
     competence_changes=[cc("1968-01-01", "Gains a section for administrative-contentious recourse (REU n.106; not re-read).", ACT["REU"], False, P)],
     notes="Hard case: 'restituendum censemus, et ... restituimus, seu melius instituimus' — the act itself hesitates between restoring the old body and instituting a new one.")

# ---------------------------------------------------------------- Household / ceremonies
body(key="ceremonial", line="household",
     curia_status="Congregation (9th in 1908; CIC 1917 can. 254; absent from REU 1967).",
     names=[name("Sacra Congregatio Caeremonialis", "Sacred Congregation of Ceremonies (Ceremonial)", "16th c.", "1968-01-01", ACT["SC"], U["SC"], True, P, "Founder disputed (Sixtus V or Gregory XIII per CE).")],
     kind=[kind("congregation", None, "1968-01-01", "Sapienti consilio; CIC 1917")],
     erected={"date": None, "act": "Gregory XIII or Sixtus V (CE)", "verified": False, "source_type": S},
     ended={"date": "1968-01-01", "act": ACT["REU"], "how": "suppressed", "verified": False, "source_type": INF, "note": "Not named in REU; omitted. Non-liturgical pontifical ceremonies are given to the Prefecture of the Apostolic Palace (REU n.126)."},
     successors=[link("papal-household-prefecture", "absorption", "1968-01-01", "Partial and inferred.")])

body(key="papal-household-prefecture", line="household",
     curia_status="Office (REU n.125; PB Art. 180; PE Arts. 228-230).",
     names=[
        name("Apostolici Palatii Praefectura", "Prefecture of the Apostolic Palace", "1968-01-01", None, ACT["REU"], U["REU"], True, P, "Still 'Praefectus Palatii Apostolici' in Pontificalis Domus (1968)."),
        name("Praefectura Pontificalis Domus", "Prefecture of the Papal Household", None, None, ACT["PB"], U["PB_LA"], True, P, "Name verified in PB (1988); date of the rename not located."),
     ],
     kind=[kind("office", "1968-01-01", None, "REU; PB; PE")],
     erected={"date": "1967-08-15", "act": ACT["REU"], "verified": True, "source_type": P},
     ended=None,
     predecessors=[link("ceremonial", "absorption", "1968-01-01")])

body(key="papal-liturgical-celebrations", line="household",
     curia_status="Office (PB Art. 182; PE Arts. 231-234).",
     names=[name("Officium de Liturgicis Celebrationibus Summi Pontificis", "Office for the Liturgical Celebrations of the Supreme Pontiff", "1989-03-01", None, ACT["PB"], U["PB_LA"], True, P)],
     kind=[kind("office", "1989-03-01", None, "PB; PE")],
     erected={"date": "1989-03-01", "act": ACT["PB"], "verified": False, "source_type": INF, "note": "Antecedent (papal masters of ceremonies / an earlier office of pontifical ceremonies) not traced."},
     ended=None)

# ---------------------------------------------------------------- Other pre-1908 bodies (placeholders)
body(key="fabric-st-peter", line="other",
     curia_status="Congregation (Reverenda Fabrica S. Petri); restricted in 1908 to the basilica; from REU listed apart (n.132); in PE an institution associated with the Holy See (Art. 244).",
     names=[name("Congregatio Reverendae Fabricae S. Petri", "Congregation of the Fabric of St Peter's", "1523", None, "Clement VII (college, 1523), later a congregation (CE)", U["SC"], False, S, "Existence and 1908 restriction verified.")],
     kind=[kind("congregation", None, "1968-01-01", "Sapienti consilio", False), kind("institution associated with the Holy See", "2022-06-05", None, "PE Art. 244")],
     erected={"date": "1523", "act": "Clement VII (CE)", "verified": False, "source_type": S},
     ended=None,
     notes="Example of a body that drifts OUT of the Curia without being suppressed.")

body(key="apostolic-visitation-urbis", line="other",
     curia_status="Congregation for the Apostolic Visitation of Rome.",
     names=[name("Congregatio Visitationis Apostolicae Urbis", "Congregation of the Apostolic Visitation of Rome", None, "1908-11-03", None, U["SC"], True, P)],
     kind=[kind("congregation", None, "1908-11-03", "Sapienti consilio")],
     erected={"date": None, "act": None, "verified": False, "source_type": S},
     ended={"date": "1908-11-03", "act": ACT["SC"], "how": "suppressed", "verified": True, "source_type": P, "note": "'Sublata Congregatione Visitationis Apostolicae Urbis'; rights pass to a special cardinalitial body at the Vicariate of Rome (outside the Curia)."},
     successors=[])

body(key="indulgences-relics", line="other",
     curia_status="Congregation (1669-1904).",
     names=[name("Congregatio Indulgentiarum et Sacrarum Reliquiarum", "Congregation of Indulgences and Relics", "1669", "1904-01-28", "Clement IX (secondary)", None, False, S)],
     kind=[kind("congregation", "1669", "1904-01-28", "secondary", False)],
     erected={"date": "1669", "act": "Clement IX (secondary)", "verified": False, "source_type": S},
     ended={"date": "1904-01-28", "act": "Pius X, m.p. Quae in Ecclesiae bonum, 28 Jan 1904 (cited in Sapienti consilio preamble; content secondary: united to Rites)", "how": "absorbed", "verified": False, "source_type": S},
     successors=[link("rites", "absorption", "1904-01-28")],
     notes="In 1908 indulgences went to the Holy Office and relics to Rites — a single body's competences split between two absorbers.")

body(key="sixtine-temporal-congregations", line="other",
     curia_status="Six of the Sixtine 15 dealt with the temporal government of the Papal States: Annona (abundance/supplies), Fleet, Sgravio (relief of burdens), Roads-Bridges-Waters, Vatican Press, Consulta. Whether they are 'Roman Curia' in the sense of a registry for magisterial issuers is doubtful.",
     names=[name("(six temporal congregations of Immensa aeterni Dei)", "Annona; Fleet; Relief of the Papal States; Roads, Bridges and Waters; Vatican Press; Consulta", "1588-01-22", None, ACT["IMMENSA"], U["CE_CONG"], False, S, "Placeholder — split into individual keys if the registry includes temporal bodies.")],
     kind=[kind("congregation", "1588-01-22", None, "CE", False)],
     erected={"date": "1588-01-22", "act": ACT["IMMENSA"], "verified": False, "source_type": S},
     ended={"date": None, "act": "various (most by 1870 or earlier)", "how": "suppressed", "verified": False, "source_type": S},
     successors=[])

body(key="latin-america-commission", line="other",
     curia_status="Pontifical Commission attached to the Congregation/Dicastery for Bishops (PB Arts. 83-84).",
     names=[name("Pontificia Commissio pro America Latina", "Pontifical Commission for Latin America", "1958-04-19", None, "Pius XII, 1958 (not read)", U["PB_EN"], False, S, "Existence verified in PB; date secondary.")],
     kind=[kind("commission (attached)", "1958-04-19", None, "PB Arts. 83-84", True)],
     erected={"date": "1958-04-19", "act": "Pius XII (secondary)", "verified": False, "source_type": S},
     ended=None)

# ------------------------------------------------------------------ events
events = []
def ev(date, act, etype, before, after, url, verified, src, note=None, precision="day"):
    d = {"date": date, "date_precision": precision, "act": act, "event_type": etype,
         "bodies_before": before, "bodies_after": after, "source": url, "source_type": src, "verified": verified}
    if note: d["note"] = note
    events.append(d)

Y = "year"
ev("1542-07-21", "Paul III, Licet ab initio", "foundation", [], ["inquisition-holy-office-cdf-ddf"], U["AAS57"], True, P, "Date as recited in Integrae servandae.")
ev("1564-08-02", "Pius IV, motu proprio (Congregation of the Council)", "foundation", [], ["council-clergy"], U["CE_CONG"], False, S)
ev("1571", "Pius V (Index)", "foundation", [], ["index"], U["CE_CONG"], False, S, precision=Y)
ev("1586-05-17", "Sixtus V, brief (Regulars)", "foundation", [], ["regulars-consultations-1586"], U["CE_CONG"], False, S)
ev("1588-01-22", ACT["IMMENSA"], "reorganization", [], ["rites", "consistorial-bishops", "bishops-consultations-1588", "roman-university", "sixtine-temporal-congregations", "signatura-gratiae"], U["SC"], True, P,
   "Date and 'fifteen congregations' verified from Sapienti consilio's recital ('die xxii mensis Ianuarii an. MDLXXXVII ... Congregationes constituit quindecim'); the list of the fifteen and their Latin titles are secondary (CE). Also confirmed existing bodies (Inquisition, Index, Council, Regulars).")
ev("1601", "Clement VIII", "merger", ["bishops-consultations-1588", "regulars-consultations-1586"], ["bishops-and-regulars"], U["CE_CONG"], False, S, precision=Y)
ev("1622-06-22", "Gregory XV, Inscrutabili divinae", "foundation", [], ["propaganda-fide-evangelization"], U["VA_CEVANG"], False, OS)
ev("1652-08-15", "Innocent X", "foundation", [], ["state-of-regulars"], U["CE_CONG"], False, S)
ev("1669", "Clement IX", "foundation", [], ["indulgences-relics"], None, False, S, precision=Y)
ev("1695-07-18", "Innocent XII", "foundation", [], ["discipline-of-regulars"], U["CE_CONG"], False, S)
ev("1698", "Innocent XII", "foundation", [], ["lauretana"], U["CE_CONG"], False, S, precision=Y)
ev("1793", "Pius VI", "foundation", [], ["public-affairs-extraordinary"], U["CE_CONG"], False, S, "Lapsed 1809, re-established 1814, renamed 1805 and 1827 (CE).", precision=Y)
ev("1824-08-28", "Leo XII, Quod divina sapientia", "re-foundation", ["roman-university"], ["studies-catholic-education"], None, False, S)
ev("1862-01-06", "Pius IX, Romani Pontifices", "foundation", [], ["oriental-rites-propaganda"], U["AAS9I"], False, S, "Founding by Pius IX verified in Dei providentis; date secondary.")
ev("1903-12-17", "Pius X, Romanis Pontificibus", "competence-transfer", ["inquisition-holy-office-cdf-ddf"], ["consistorial-bishops"], U["SC"], True, P, "Cited in Sapienti consilio's preamble; content (nomination of bishops) per CE.")
ev("1904-01-28", "Pius X, Quae in Ecclesiae bonum", "absorption", ["indulgences-relics"], ["rites"], U["SC"], False, S, "Act cited in Sapienti consilio; effect secondary.")
ev("1906-05-26", "Pius X, Sacrae Congregationi super negotiis", "absorption", ["discipline-of-regulars", "state-of-regulars"], ["bishops-and-regulars"], U["SC"], False, S, "Act cited in Sapienti consilio; effect per CE.")
ev("1908-11-03", ACT["SC"], "reorganization", ["bishops-and-regulars", "revision-of-councils", "lauretana", "apostolic-visitation-urbis", "signatura-gratiae"],
   ["sacraments-1908", "religious-consecrated-life", "apostolic-signatura"], U["SC"], True, P,
   "Closed list of 11 congregations, 3 tribunals, 5 offices from 3 Nov 1908. Rename Inquisition -> Holy Office; Bishops-and-Regulars dissolved (diocesan matters to Consistorial, religious to new Congregation of Religious); Sacraments created; Lauretana united to Council; Visitation and Revision of Councils suppressed; Rota revived; Signatura refounded; Secretariat of Briefs becomes 3rd part of the Secretariat of State.")
ev("1908-11-03", ACT["SC"], "rename", ["inquisition-holy-office-cdf-ddf"], ["inquisition-holy-office-cdf-ddf"], U["SC"], True, P)
ev("1908-11-03", ACT["SC"], "split", ["bishops-and-regulars"], ["religious-consecrated-life", "consistorial-bishops"], U["SC"], True, P, "Implicit: B&R omitted from the closed list, its matters distributed.")
ev("1908-11-03", ACT["SC"], "re-foundation", ["signatura-gratiae"], ["apostolic-signatura"], U["SC"], True, P, "'restituimus, seu melius instituimus'.")
ev("1908-11-03", ACT["SC"], "revival", ["roman-rota"], ["roman-rota"], U["SC"], True, P, "'rursus in exercitium revocamus'.")
ev("1908-11-03", ACT["SC"], "absorption", ["lauretana"], ["council-clergy"], U["SC"], True, P)
ev("1908-11-03", ACT["SC"], "suppression", ["apostolic-visitation-urbis"], [], U["SC"], True, P)
ev("1908-11-03", ACT["SC"], "absorption", ["revision-of-councils"], ["council-clergy"], U["SC"], True, P)
ev("1915-11-04", ACT["SEMCLER"], "merger-or-rename", ["studies-catholic-education"], ["studies-catholic-education"], U["AAS7"], True, P,
   "New congregation for seminaries (from the Consistorial) to which the functions of the Congregation of Studies are added; combined name. Modelled as continuity of Studies — see hard cases.")
ev("1917-03-25", ACT["ALLOQ"], "absorption", ["index"], ["inquisition-holy-office-cdf-ddf"], U["AAS9I"], True, P, "Also indulgences: Holy Office -> Penitentiary.")
ev("1917-05-27", ACT["CIC17"], "codification", [], [], U["CIC17"], True, P, "Lists 11 congregations (Index gone; Seminaries and Universities and the Oriental Church added), 3 tribunals, 5 offices. Oriental Church listed before it formally began (1 Dec 1917).")
ev("1917-09-15", ACT["CUMIURIS"], "foundation", [], ["code-interpretation-1917"], U["AAS9I"], True, P)
ev("1917-11-30", ACT["DEIPROV"], "split", ["oriental-rites-propaganda"], ["oriental-churches"], U["AAS9I"], True, P, "Old body ceases 30 Nov; new congregation from 1 Dec 1917.")
ev("1930-02-06", "Pius XI, m.p. Già da qualche tempo", "competence-transfer", ["rites"], ["rites"], U["AAS22"], True, P, "Historical section created.")
ev("1938-03-25", "Pius XI, m.p. Sancta Dei Ecclesia", "competence-transfer", ["propaganda-fide-evangelization"], ["oriental-churches"], U["AAS30"], False, P, "Title/date verified from AAS index; territorial content not read.")
ev("1958-04-19", "Pius XII", "foundation", [], ["latin-america-commission"], None, False, S)
ev("1959-02-22", "John XXIII, Boni Pastoris", "kind-change", ["social-communications"], ["social-communications"], U["AAS56"], False, P, "Made permanent; date secondary.")
ev("1960-06-05", ACT["SUPERNO"], "foundation", [], ["christian-unity"], U["AAS52"], True, P)
ev("1963-03-28", "John XXIII", "foundation", [], ["code-revision-1963"], None, False, S)
ev("1964", "Paul VI, Sacram Liturgiam", "foundation", [], ["liturgy-consilium"], None, False, S, precision=Y)
ev("1964-04-02", ACT["INFRUCTIBUS"], "rename", ["social-communications"], ["social-communications"], U["AAS56"], True, P, "Rename with enlarged competences ('mutato nomine et munerum provincia amplificata').")
ev("1964-05-19", ACT["PROGREDIENTE"], "foundation", [], ["interreligious-dialogue"], U["AAS56"], True, P)
ev("1965-04-09", "Paul VI", "foundation", [], ["non-believers"], U["AAS58"], False, S, "Founder verified (Finis Concilio); date secondary.")
ev("1965-12-07", ACT["INTEGRAE"], "rename", ["inquisition-holy-office-cdf-ddf"], ["inquisition-holy-office-cdf-ddf"], U["AAS57"], True, P, "Name and 'ordo' changed.")
ev("1966-01-03", ACT["FINIS"], "kind-change", ["christian-unity"], ["christian-unity"], U["AAS58"], True, P, "Secretariat confirmed beyond the Council.")
ev("1967-01-06", ACT["CATHOLICAM"], "foundation", [], ["laity-council", "justice-peace"], U["AAS59"], True, P, "Both ad experimentum for five years.")
ev("1968-01-01", ACT["REU"], "reorganization", ["apostolic-datary", "ceremonial", "apostolic-briefs-secretariat", "briefs-to-princes"],
   ["apsa", "prefecture-economic-affairs", "papal-household-prefecture"], U["REU"], True, P,
   "Signed 15 Aug 1967, in force 1 Jan 1968. Renames: Consistorial->pro Episcopis; Council->pro Clericis; Oriental Church->Oriental Churches; Religious->+Secular Institutes; Seminaries&Universities->Catholic Education; Propaganda->Evangelization of Peoples; Extraordinary Affairs->Council for Public Affairs. Datary and Ceremonial not named (implicitly suppressed).")
for k in ["consistorial-bishops", "council-clergy", "oriental-churches", "religious-consecrated-life", "studies-catholic-education", "propaganda-fide-evangelization"]:
    ev("1968-01-01", ACT["REU"], "rename", [k], [k], U["REU"], True, P)
ev("1968-01-01", ACT["REU"], "rename+kind-change", ["public-affairs-extraordinary"], ["public-affairs-extraordinary"], U["REU"], True, P, "Congregation becomes 'Sacrum Consilium'.")
ev("1968-01-01", ACT["REU"], "suppression", ["apostolic-datary"], [], U["REU"], False, INF, "Not named in REU.")
ev("1968-01-01", ACT["REU"], "suppression", ["ceremonial"], ["papal-household-prefecture"], U["REU"], False, INF, "Not named in REU.")
ev("1968-01-01", ACT["REU"], "absorption", ["apostolic-briefs-secretariat", "briefs-to-princes"], ["secretariat-of-state"], U["AAS65"], True, P, "As stated retrospectively by Quo aptius.")
ev("1968-03-28", ACT["PONTDOMUS"], "rename", ["papal-almonry-charity"], ["papal-almonry-charity"], U["AAS60"], True, P, "Office-holder renamed Eleemosynarius Sanctitatis Suae.")
ev("1969-05-08", ACT["SACRARITUUM"], "split", ["rites"], ["divine-worship-1969", "causes-of-saints"], U["AAS61"], True, P, "'in locum ... duas novas substituimus Congregationes'.")
ev("1969-05-08", ACT["SACRARITUUM"], "absorption", ["liturgy-consilium"], ["divine-worship-1969"], U["AAS61"], True, P)
ev("1970-03-19", ACT["APOSTCARIT"], "foundation", [], ["migrants"], U["AAS62"], True, P)
ev("1971-07-15", ACT["AMORIS"], "foundation", [], ["cor-unum"], U["AAS63"], True, P)
ev("1973-01-11", "Paul VI", "foundation", [], ["family-committee"], None, False, S)
ev("1973-02-27", ACT["QUOAPTIUS"], "absorption", ["apostolic-chancery"], ["secretariat-of-state"], U["AAS65"], True, P)
ev("1975-07-11", ACT["CONSTANS"], "merger", ["sacraments-1908", "divine-worship-1969"], ["sacraments-divine-worship-1975"], U["AAS67"], True, P)
ev("1976-12-10", ACT["APOSTOLATUS"], "rename+kind-change", ["laity-council"], ["laity-council"], U["AAS68"], True, P)
ev("1976-12-10", ACT["IUSTITIAM"], "kind-change", ["justice-peace"], ["justice-peace"], U["AAS68"], True, P, "Made permanent.")
ev("1981-05-09", ACT["FAMILIA"], "re-foundation", ["family-committee"], ["family-council"], U["AAS73"], True, P, "'succedit eique sufficitur ... hoc iam ilico cessat'.")
ev("1982-05-20", ACT["CULTURA82"], "foundation", [], ["culture-council"], U["AAS74"], True, P)
ev("1984-01-02", ACT["RECOGNITO"], "foundation", ["code-interpretation-1917"], ["legislative-texts"], U["AAS76"], True, P, "New erection modelled on the 1917 commission; no explicit succession clause.")
ev("1984-04-05", ACT["QUONIAM"], "split", ["sacraments-divine-worship-1975"], ["sacraments-1984", "divine-worship-1984"], U["AAS76"], True, P)
ev("1985-02-11", ACT["DOLENTIUM"], "foundation", [], ["health-care"], U["AAS77"], True, P)
ev("1988-07-02", "John Paul II, Ecclesia Dei adflicta", "foundation", [], ["ecclesia-dei-commission"], U["ED2019"], False, OS)
ev("1989-03-01", ACT["PB"], "reorganization", ["sacraments-1984", "divine-worship-1984", "public-affairs-extraordinary"],
   ["divine-worship-sacraments-1988", "papal-liturgical-celebrations", "cultural-heritage-commission"], U["PB_EN"], True, P,
   "Signed 28 Jun 1988, in force 1 Mar 1989. 9 congregations, 3 tribunals, 12 pontifical councils, 3 offices; 'Sacra' dropped from names; secretariats and commissions become 'Pontifical Councils'; Council for Public Affairs becomes 2nd Section of the Secretariat of State.")
ev("1989-03-01", ACT["PB"], "merger", ["sacraments-1984", "divine-worship-1984"], ["divine-worship-sacraments-1988"], U["PB_EN"], False, INF, "No merger clause found; inferred from the single congregation described.")
ev("1989-03-01", ACT["PB"], "absorption", ["public-affairs-extraordinary"], ["secretariat-of-state"], U["PB_EN"], True, P)
for k in ["christian-unity", "interreligious-dialogue", "non-believers", "justice-peace", "migrants", "health-care", "legislative-texts", "social-communications"]:
    ev("1989-03-01", ACT["PB"], "rename+kind-change", [k], [k], U["PB_LA"], True, P)
for k in ["religious-consecrated-life", "studies-catholic-education", "causes-of-saints"]:
    ev("1989-03-01", ACT["PB"], "rename", [k], [k], U["PB_LA"], True, P)
ev("1993-03-25", ACT["INDE"], "merger", ["culture-council", "non-believers"], ["culture-council"], U["INDE"], True, P, "Result keeps the name of one partner.")
ev("1993-03-25", ACT["INDE"], "rename+kind-change", ["cultural-heritage-commission"], ["cultural-heritage-commission"], U["INDE"], True, P, "Detached from the Congregation for the Clergy, autonomous, renamed.")
ev("1999", "act not identified", "rename", ["legislative-texts"], ["legislative-texts"], U["BNF_PCLT"], False, S, precision=Y)
ev("2010-09-21", ACT["UBICUMQUE"], "foundation", [], ["new-evangelization-council"], U["UBICUMQUE"], False, OS)
ev("2011-08-30", "Benedict XVI, Quaerit semper", "competence-transfer", ["divine-worship-sacraments-1988"], ["roman-rota"], U["PB_LA"], False, OS)
ev("2012-07-30", ACT["PULCHR"], "absorption", ["cultural-heritage-commission"], ["culture-council"], U["PULCHR"], False, OS)
ev("2013-01-16", ACT["MINISTRORUM"], "competence-transfer", ["studies-catholic-education"], ["council-clergy"], U["MINISTRORUM"], False, OS, "Seminaries.")
ev("2013-01-16", ACT["FIDESPERDOCT"], "competence-transfer", ["council-clergy"], ["new-evangelization-council"], U["FIDESPERDOCT"], False, OS, "Catechesis.")
ev("2014-02-24", ACT["FDP"], "foundation", [], ["secretariat-economy", "council-economy", "auditor-general"], U["FDP"], True, P)
ev("2014-03-22", "Francis, chirograph", "foundation", [], ["protection-minors-commission"], None, False, S)
ev("2015-06-27", ACT["SPC2015"], "foundation", [], ["communication-dicastery"], U["SPC2015"], True, P, "Operative 29 Jun 2015; nine bodies to be combined into it.")
ev("2016", ACT["SPC2015"], "absorption", ["social-communications"], ["communication-dicastery"], U["SPC2015"], False, OS, precision=Y)
ev("2016-09-01", ACT["SEDULA"], "merger", ["laity-council", "family-council"], ["laity-family-life"], U["SEDULA"], True, P, "Act 15 Aug 2016; operative 1 Sep 2016.")
ev("2016-12-30", "act not identified", "suppression", ["prefecture-economic-affairs"], ["secretariat-economy"], U["WP_PREFECON"], False, S)
ev("2017-01-01", ACT["HUMANAM"], "merger", ["justice-peace", "cor-unum", "migrants", "health-care"], ["integral-human-development"], U["HUMANAM"], True, P, "Act 17 Aug 2016; operative 1 Jan 2017.")
ev("2018-06-23", ACT["RESCRIPT2018"], "rename", ["communication-dicastery"], ["communication-dicastery"], U["RESCRIPT2018"], False, OS)
ev("2019-01-17", ACT["ED2019"], "absorption", ["ecclesia-dei-commission"], ["inquisition-holy-office-cdf-ddf"], U["ED2019"], False, OS)
ev("2022-06-05", ACT["PE"], "reorganization", ["propaganda-fide-evangelization", "new-evangelization-council", "culture-council", "studies-catholic-education"],
   ["evangelization-dicastery", "culture-education-dicastery"], U["PE"], True, P,
   "Signed 19 Mar 2022, in force 5 Jun 2022. PB abrogated (Art. 250 §3). 16 dicasteries, all juridically equal with the Secretariat of State (Art. 12). All congregations and councils renamed 'Dicastery'. Almonry becomes the Dicastery for the Service of Charity. PCPM established within the DDF.")
ev("2022-06-05", ACT["PE"], "merger", ["propaganda-fide-evangelization", "new-evangelization-council"], ["evangelization-dicastery"], U["PE"], True, P, "Inferred from PE structure; no article names the merged bodies.")
ev("2022-06-05", ACT["PE"], "merger", ["culture-council", "studies-catholic-education"], ["culture-education-dicastery"], U["PE"], True, P, "Inferred from PE structure (two sections, Art. 153 §2).")
for k in ["inquisition-holy-office-cdf-ddf", "oriental-churches", "divine-worship-sacraments-1988", "causes-of-saints", "consistorial-bishops", "council-clergy",
          "religious-consecrated-life", "christian-unity", "interreligious-dialogue", "legislative-texts"]:
    ev("2022-06-05", ACT["PE"], "rename+kind-change", [k], [k], U["PE"], True, P)
ev("2022-06-05", ACT["PE"], "rename+kind-change", ["papal-almonry-charity"], ["papal-almonry-charity"], U["PE"], True, P, "Institution connected with the Holy See -> dicastery.")
ev("2022-06-05", ACT["PE"], "attachment", ["protection-minors-commission"], ["inquisition-holy-office-cdf-ddf"], U["PE"], True, P, "Established within the DDF (Art. 78).")
ev("2022-06-05", ACT["PE"], "competence-transfer", ["consistorial-bishops"], ["council-clergy"], U["PE"], False, S, "Personal prelatures.")
ev("2022-06-05", ACT["PE"], "rename", ["apostolic-camera"], ["apostolic-camera"], U["PE"], True, P, "Office now named after its holder (Camerlengo).")
ev("2025-02-11", "Francis, chirograph Vinculum unitatis et caritatis", "foundation", [], ["donations-commission"], U["VINC2025F"], False, OS)
ev("2025-12-04", "Leo XIV, chirograph Vinculum unitatis et caritatis (29 Sep 2025, published 4 Dec 2025)", "suppression", ["donations-commission"], [], U["VINC2025L"], True, P)
ev("2025-11-24", "Leo XIV, General Regulation of the Roman Curia (signed 23 Nov 2025)", "regulation", [], [], U["REGCUR2025"], False, OS, "Replaces the 1999 regulation; no structural change reported.")

events.sort(key=lambda e: (e["date"] or "9999", e["event_type"]))
for i, e in enumerate(events, 1):
    e["id"] = f"ev{i:03d}"
    events[i-1] = {"id": e.pop("id"), **e}

# ---- consistency checks
keys = {b["key"] for b in bodies}
assert len(keys) == len(bodies), "duplicate keys"
errs = []
for b in bodies:
    for rel in ("predecessors", "successors"):
        for l in b[rel]:
            if l["key"] not in keys: errs.append(f"{b['key']} {rel} -> {l['key']}")
for e in events:
    for k in e["bodies_before"] + e["bodies_after"]:
        if k not in keys: errs.append(f"{e['id']} -> {k}")
# successor/predecessor symmetry
pairs = {(b["key"], l["key"]) for b in bodies for l in b["successors"]}
back = {(l["key"], b["key"]) for b in bodies for l in b["predecessors"]}
for a in sorted(pairs - back): errs.append(f"asymmetric successor {a}")
for a in sorted(back - pairs): errs.append(f"asymmetric predecessor {a}")
if errs:
    print("\n".join(errs)); sys.exit(1)

meta = {"warning": "All keys are PROVISIONAL working keys for research only, not identifiers. 'verified': true = checked against the text of the act (AAS PDF or vatican.va page). source_type: primary = act text read; official-secondary = vatican.va/press office summary or search extract of the act; secondary = encyclopedias, Wikipedia, GCatholic, BnF, news; inferred = deduced from the structure of an act that does not state it.",
        "generated": "2026-10-25"}
with open(os.path.join(OUT, "bodies.json"), "w") as f:
    json.dump({"_meta": meta, "bodies": bodies}, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "events.json"), "w") as f:
    json.dump({"_meta": meta, "events": events}, f, ensure_ascii=False, indent=2)
print(len(bodies), "bodies;", len(events), "events;", sum(e["verified"] for e in events), "events verified")
