# Fase 1 — Agent C: Moderne pattern-PDF design og SVG-teknik

Researcher: Claude (Opus 4.7) · Dato: 2026-04-29

Mål: konkrete anbefalinger til typografi, palette, layout-grids og en
SVG-feature-liste der løfter vores Paged.js-pipeline til
"publikations-kvalitet i 2026".

---

## 1. Hvad gør "the big five" visuelt fede?

| Brand | Visuel signatur | Læring vi tager med |
|---|---|---|
| **PetiteKnit** (DK) | Stille, sand-/off-white baggrunde, masser af luft, kropsfoto i naturligt lys, en humanistisk sans-serif som titel og en lettere serif/sans-mix til brødtekst. Schematics er meget rene: tynde sorte linjer, ingen fyld, mål i centimeter. | "Hygge-minimalisme": store margins, få farver, foto driver siden. |
| **Lærke Bagger** (DK) | Højkontrast, legesyg, farverige accentblokke, rå/utraditionel — bryder bevidst grid'et. Foto er tit kontekst-styled (ikke kun produkt). | Tør bruge én bold display-font og én accentfarve. |
| **Aimee Sher Makes** | Editorial-look: stor display-serif øverst, generøs leading, fotomontager med beskårne detaljer, schematics med påført dimension-tekst i samme font som body. | Konsistent typografi *også* i schematics (ikke en "anden" font i SVG). |
| **Tin Can Knits** (Emily Wessel/Alexa Ludeman) | Klart, struktureret, "manualagtigt": tabeller for sizing, schematics med tydelige bemålinger, gode charts med stort symbol-grid. | Rigtigt godt benchmark for *læselighed* og pædagogik. |
| **Brooklyn Tweed** (Jared Flood) | "Editorialt fagblad": serif-driven, classic book-typography, schematics tegnet som tekniske tegninger med stiplede ribkanter, hatched zoner og full bleed-foto. | Guldstandarden for schematics og charts. Nær trykt bogkvalitet. |

Fælles træk:
- **2 fonts max** — én display + én body. Ingen blander 4 forskellige.
- **Schematics er linjebaseret**, ikke fladefyldt. Sort 0.6–1.0 pt
  outline, hvid eller transparent fill, tynde dimension-pile.
- **Charts har symbol-font + grid-baggrund**, ikke farvelagte celler
  (undtagen colorwork).
- **Foto-først**: første side er typisk hero-foto + titel, ikke
  instruktioner.

## 2. Typografi — konkret anbefaling

Jeg anbefaler **2 fonts**, begge SIL OFL 1.1 (gratis kommerciel brug):

### Display (titler, størrelser, "Pattern" hero-tekst)
**Fraunces** (Google Fonts, OFL). Variable font med optisk størrelse + en
"SOFT" og "WONK" akse. Giver bog-følelsen som Brooklyn Tweed bruger,
men med en moderne legesyg variant der matcher Lærke Bagger-energien
hvis vi skruer "wonk" op. Variable, så vi får alle vægte i én fil
(under 100 KB woff2-subset).

### Body (instruktioner, tabeller, schematic-labels)
**Inter** (Google Fonts, OFL, Rasmus Andersson). Skandinavisk
"workhorse"-sans, designet til skærm men trykker fint. Har alle danske
diakritiske tegn, ægte tabular numerals (`font-variant-numeric:
tabular-nums`) — kritisk for stitch-counts og størrelses-tabeller.
Variable font, alle vægte 100–900.

**Alternativ body**: **Source Serif 4** (OFL) hvis vi vil have et mere
PetiteKnit/Brooklyn-Tweed-bog-look. Men Inter er det sikreste valg for
læselighed på skærm + print.

**Brug ALDRIG fonts vi ikke kan bekræfte licens på.** Cormorant
Garamond, EB Garamond, Source Sans, Source Serif, Inter, Fraunces, IBM
Plex (alle vægte) — alle OFL, bekræftet.

## 3. Palette

Holdt minimal — vi bygger et "redaktionelt" look, ikke et brand:

```
--ink:    #1a1a1a   /* primær tekst, schematic outlines */
--paper:  #fafaf7   /* baggrund, varmere end pure white */
--muted:  #6b6b66   /* sekundær tekst, dimension-labels */
--rule:   #d9d6cf   /* tabel-skillelinjer, grid */
--accent: #8a3324   /* én accent (rust/brick), brugt sparsomt */
--haze:   rgba(138, 51, 36, 0.08)  /* transparent zone-overlay i schematics */
```

Én accentfarve. Hvis brugeren har et garn med farveangivelse, kan
`--accent` overrides via en CSS-variabel pr. opskrift.

## 4. Layout-grid (A4)

Anbefaling: **12-kolonne grid med 2-spalte tekstlayout** for body-sider,
**1-spalte fuld bredde** for hero/foto/schematic-sider.

```
A4: 210 × 297 mm
Margins: top 22 mm, bund 24 mm, indvendig 20 mm, udvendig 16 mm
Kolonne-bredde: 174 mm tilgængelig
Gutters: 6 mm
Baseline grid: 12 pt (4.23 mm) — alt snapper hertil
Body-tekst: 10/14 pt (10pt størrelse, 14pt linjeafstand)
Schematic max-bredde: 174 mm (full text-block)
```

Brug `@page` i Paged.js til at differentiere første side (`@page:first`)
fra øvrige (`@page`). Sidetal i bundgutter, opskriftsnavn i toppen
(running header).

## 5. Schematic-stil — hvad adskiller "kedelig" fra "flot"

Vores nuværende `svg.py` laver simple outlines. Det vi mangler:

### Must-have features
1. **Dimension lines** med pile, extension lines og målepile-stop
   (arrow-heads). SVG `<marker>` til pilespidser, lille gap mellem
   dimension-linje og det objekt der måles.
2. **Mål-labels** med samme font som body (Inter), italic eller small-caps,
   placeret midt på dimensionslinjen med hvid baggrund-pad så linjen
   "brydes" af tallet.
3. **Hatching pattern** for ribkant-zoner: SVG `<pattern>` med diagonal
   stroke 0.4 pt, spacing 1.5 mm. Genbrug som `fill="url(#rib-hatch)"`.
4. **Transparent zone-overlay** for stranded/colorwork-områder: 8 %
   opacity af `--accent` ovenpå outline-figuren.
5. **Stitch-direction arrows** (top-down vs. bottom-up) i hjørne af
   schematic.
6. **Stiplede linjer** (`stroke-dasharray: 2 2`) for skjulte/foldede
   kanter (fx skulder-søm bag halsudskæring).
7. **Multi-size schematics**: viser én outline med flere dimension-tal
   adskilt af `/` (S/M/L/XL) eller en lille legend.

### Nice-to-have
8. **Symboler for konstruktionsdetaljer**: raglan-decrease-markører,
   short-row-zoner, stitch-pickup-prikker.
9. **Flat schematic + 3D-projektion** (isometrisk lille thumbnail i
   hjørnet for at vise hvordan stykket sidder).
10. **Auto-layout**: hvis to dimension-tekster overlapper, flyt automatisk.

Implementering: alle ovenstående kan laves i ren SVG (ingen JS i
output). `<defs>` med `<marker>`, `<pattern>`, `<symbol>` — én
SVG-modul-fil pr. schematic-arketype.

## 6. Charts — symbol-fonts og åbne alternativer

### Status quo
- **Stitchmastery Knitting Fonts** er gratis (siden 2024-ish) og må
  bruges kommercielt iflg. deres egen side. MEN: licensen er en EULA,
  *ikke* OFL, og den må ikke redistribueres. Det betyder vi ikke kan
  bundle den i en Python-pakke eller en CDN — brugeren skal selv
  installere den, eller vi skal kunne fallback'e til SVG-symboler.
- **Knitter's Symbols (XRX)** er tilladt med credit-line — også
  EULA-style, ikke OFL.
- **MinimalistKnit / MinimalistColourwork** er paid (Gumroad).
- **Aldine** er Stitchmastery's *betalte* premium-font; ikke gratis.

### Konklusion: vi kan IKKE finde en SIL OFL-licenseret strikkechart-font.
Markedet har ikke en. Det betyder: **vi skal selv bygge SVG-symboler**.

### Anbefaling: SVG symbol library
Byg `lib/svg/chart_symbols.py` der genererer en `<defs>` med
`<symbol id="knit">`, `<symbol id="purl">`, osv. Kilder vi kan
basere på (alt CC0/public-domain-tegnbar):
- **Marnen Laibow-Koser's `knitting_symbols`** (GitHub
  marnen/knitting_symbols): SVG-filer for alle standard-symboler
  (knit, purl, YO, k2tog, ssk, kfb, cables 2x1 / 2x2, slip, BO).
  Licens er ikke specificeret — vi *bør ikke* kopiere direkte men
  redrawe i samme stil (ren geometrisk konstruktion, ikke
  copyright-bærende).
- **Craft Yarn Council's standard chart symbols** (publiceret som
  branche-standard, ingen ophavsret på selve formerne).

Symbolerne er så simple geometriske former (vandret streg = knit, prik
= purl, cirkel = YO, skrå streg = decrease) at de kan reproduceres
uden licens-bekymring. Vi laver dem i `svg.py` som Python-funktioner
der returnerer SVG-strings — så er der ingen font-fil overhovedet.

Bonus: vi kan style symbolerne via CSS (`stroke-width`, `color`) i
samme palette som resten af PDF'en. Det kan en font ikke.

### Chart-grid
- 5 mm celle-bredde for normal lace.
- 6 mm for cables (de fylder mere visuelt).
- Tykkere stroke hver 5. + 10. række/kolonne (som mm-papir).
- Række-numre højre side (RS-rækker) + venstre side (WS-rækker).

## 7. Paged.js i 2026 — er det stadig vejen frem?

### Vurdering
Paged.js er **stadig den mest pragmatiske vej** for vores stack, men
den er ikke længere det åbenlyse førstevalg.

| Tool | Fordele | Ulemper |
|---|---|---|
| **Paged.js** | Bruger Chromium, fuld CSS3 + variable fonts, JS-friendly, godt CSS Paged Media support, well-tested | Vedligeholdelse er stille-langsom (få releases siden 2022), bug-backlog vokser |
| **Vivliostyle.js** | Aktivt vedligeholdt, godt CJK + multi-column support, footnotes, EPUB-eksport | Mindre community, færre eksempler for komplekse skematik-layouts |
| **WeasyPrint** | Python-native (matcher vores stack!), god CSS Paged Media, hurtig, ingen Chromium-dependency | Ingen JavaScript (vi bruger ikke JS, så OK), lidt anderledes CSS-quirks, ingen variable fonts før v60+ |
| **Chrome `--headless --print-to-pdf`** | Nul dependencies, brugerens egen Chrome | Ringere paged-media-support end Paged.js (ingen running headers/footers, dårlige page-breaks) |
| **PrinceXML / DocRaptor** | Bedst-i-klassen output | Kommercielt ($$$). Disqualified for FOSS-projekt |

### Anbefaling
**Skift til WeasyPrint** som primær renderer. Begrundelser:
1. Vores pipeline er Python — fjerner Node.js dependency.
2. Aktivt vedligeholdt (Kozea, regelmæssige releases).
3. Variable fonts understøttes fra v60 (2024).
4. Ingen Chromium = hurtigere CI, mindre RAM, simplere Docker.
5. Vi bruger ingen JavaScript i output alligevel.

Behold Paged.js som *fallback* / preview-værktøj i browser (live
HTML-preview før PDF-render). Det er rart for udvikleren.

## 8. Konkret feature-liste til vores SVG-pipeline

Prioriteret roadmap:

**P0 (must, fase 2)**
- [ ] `<marker>` for arrow-heads (4 varianter: normal, inset, dimension-stop, raglan)
- [ ] Dimension-line helper: `dim_line(x1, y1, x2, y2, label, side)`
- [ ] Hatching `<pattern>` library: `rib`, `seed`, `stockinette`, `stranded-zone`
- [ ] Multi-size dimension labels (S/M/L overlay)
- [ ] CSS-variabler for farve (kan re-styles uden re-render)
- [ ] Tabular-numerals `font-feature-settings: 'tnum'` i alle SVG-tekster

**P1 (skal/burde, fase 3)**
- [ ] Symbol-bibliotek: knit, purl, YO, k2tog, ssk, k3tog, sssk, sl, M1L, M1R
- [ ] Cable-symboler: 1x1, 2x1, 2x2, 3x3, twist L/R
- [ ] Chart-grid generator med RS/WS row-numbering
- [ ] Stitch-direction-arrow (top-down/bottom-up indikator)
- [ ] Foldable/hidden-edge dashed lines

**P2 (nice-to-have)**
- [ ] Lace-symboler (alle yo/dec-kombinationer)
- [ ] Brioche-symboler (brk, brp, sl1yo)
- [ ] Isometrisk 3D-thumbnail
- [ ] Auto-collision-detection på dimension-labels
- [ ] Eksport af chart som standalone-SVG (uden hele opskriften)

## 9. Sammenfatning

Vi løfter "publikations-kvalitet" gennem tre håndtag:

1. **Typografi**: skift til Fraunces (display) + Inter (body), begge OFL.
   Aktivér tabular numerals overalt.
2. **Schematics**: byg dimension-line/hatching/marker-system i `svg.py`.
   Sigt på Brooklyn Tweed-niveau, ikke MS-Paint-niveau.
3. **Charts**: byg vores eget SVG-symbol-bibliotek (ingen font-licens-
   problemer), styled via CSS.
4. **Renderer**: skift fra Paged.js til WeasyPrint — Python-native,
   aktivt vedligeholdt, ingen Chromium-bagage.

Tidsestimat: P0+P1 features ≈ 3–5 dage Python-arbejde. WeasyPrint-skift
≈ 1 dag (de fleste af vores CSS er kompatibelt).

---

## Kilder

- [Brooklyn Tweed pattern library](https://brooklyntweed.com/collections/patterns)
- [PetiteKnit — Laine journal feature](https://lainepublishing.com/en-us/blogs/journal/petiteknit-the-epitome-of-danish-knitwear-design)
- [Tin Can Knits patterns](https://tincanknits.com/patterns)
- [Stitchmastery free knitting fonts](https://stitchmastery.com/fonts/) (EULA, ikke OFL)
- [Marnen — knitting_symbols (SVG library)](https://marnen.github.io/knitting_symbols/symbols/)
- [Google Fonts: Fraunces](https://fonts.google.com/specimen/Fraunces) (OFL)
- [Google Fonts: Inter](https://fonts.google.com/specimen/Inter) (OFL)
- [Google Fonts: Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond) (OFL)
- [SIL Open Font License](https://openfontlicense.org/ofl-fonts/)
- [Vivliostyle.js (GitHub)](https://github.com/vivliostyle/vivliostyle.js/)
- [print-css.rocks — Paged Media tools comparison](https://print-css.rocks/tools)
- [WeasyPrint vs DocRaptor showdown](https://dev.to/thawkin3/docraptor-vs-weasyprint-a-pdf-export-showdown-34f)
- [Hacker News — Paged.js maintenance status](https://news.ycombinator.com/item?id=35244120)
- [Canonical — A4 grid + typography deep dive](https://canonical.com/blog/a-look-under-the-hood-of-our-grid-system-and-typography-for-the-a4-format)
- [SVG hatching patterns guide](https://www.codegenes.net/blog/simple-fill-pattern-in-svg-diagonal-hatching/)
- [Features Needed in SVG2 for Technical Diagrams (W3C)](https://www.w3.org/Graphics/SVG/WG/wiki/images/d/d8/Features_needed_in_SVG2_for_Technical_Diagrams.pdf)
