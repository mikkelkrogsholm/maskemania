# Changelog

Alle bemærkelsesværdige ændringer i `maskemania` dokumenteres her.
Formatet følger [Keep a Changelog](https://keepachangelog.com/da/1.1.0/);
projektet er endnu pre-1.0 og versions-numrene afspejler iterationer i
`PLAN.md` snarere end semver-promiser om bagudkompatibilitet.

## [Unreleased]

### Removed
- GitHub Actions workflows (`ci.yml` og `pages.yml`). Tests køres lokalt
  før commit; ingen automatiseret CI/CD-pipeline længere.

### Added
- **Engelsk i18n for konstruktions-step-tekst.** Alle 20 generator-funktioner
  (`generate_X(spec, lang="da")`) tager nu en `lang`-parameter. Når CLI'en
  kaldes med `--lang en` produceres opskriftens trin-for-trin-tekst på
  engelsk — ikke kun cover/materialer/forkortelser.
  - 9 mest brugte konstruktioner har fuldt bilingualt step-text (hue,
    tørklæde knit, raglan_topdown, sokker, bottom_up_sweater, granny_square,
    amigurumi_sphere/cylinder, c2c_blanket, tørklæde crochet) — hver streng
    er eksplicit oversat med en lille `_l(da, en, lang)`-helper.
  - 11 andre konstruktioner falder tilbage til en post-hoc oversættelse i
    `lib/visualisering/lang/construction_strings.py` (`translate_pattern()`):
    sektion-titler oversættes via en eksplicit `SECTION_TITLES_EN`-tabel og
    step-tekst gennem en konservativ phrase-replace-pass (US-konvention:
    sc/dc/tr/sl-st/ch).
  - 14 nye tests (`test_i18n_constructions.py` i begge skill-test-mapper)
    verificerer at `lang="en"` producerer engelske markør-ord ("Cast on",
    "Knit", "Bind off", "magic ring", "sc", "dc") og at `lang="da"`
    fortsat fungerer uændret.
- Root `LICENSE` (MIT), `CONTRIBUTING.md` og fyldig root `README.md`.
- `--pdf-renderer {auto,weasy,chrome}` flag på begge `scripts/generate.py`
  så brugeren kan tvinge en specifik PDF-renderer.
- 9 nye tests i `lib/visualisering/tests/test_pdf_routing.py` der
  verificerer routing-logikken (alle med mocks, kræver hverken
  WeasyPrint eller Chrome installeret).
- Ny modul `lib/visualisering/pdf_weasy.py` med WeasyPrint-renderer,
  base-URL-håndtering for relative asset-references og graceful
  håndtering af manglende system-deps (Cairo/Pango).

### Changed
- **PDF: WeasyPrint som primær renderer; Chrome som fallback.**
  `lib/visualisering/pdf.py` har nu en `render_pdf()`-routing-funktion
  der prøver WeasyPrint først (Python-native, ingen Chromium-afhængighed,
  variable fonts via v60+) og falder tilbage til headless Chrome hvis
  WeasyPrint ikke kan importeres. Hvis ingen af delene er tilgængelige
  rejses en `ValueError` med klar besked om hvordan man installerer en
  af dem. Det legacy `html_to_pdf()`-API bevares for social-preview-
  pipelinen, der bruger Chrome direkte til PNG-rasterisering.
- **CLI:** standardiseret tekniske flag til engelsk kebab-case som
  primær (`--head`, `--bust`, `--neck`, `--width`, `--length`,
  `--height`, `--foot-length`, `--shoe-size`, `--sleeve-length`,
  `--upper-arm`, `--wrist`, `--body-length`, `--row-gauge`,
  `--yoke-depth`, …) på tværs af strik- og hækl-CLI'erne. Hvert
  teknisk flag har nu en dansk alias (`--hovedmål`, `--bryst`,
  `--hals`, `--bredde`, `--længde`, `--højde`, `--fodlængde`,
  `--skostørrelse`, `--ærme`, `--overarm`, `--håndled`, `--kropslængde`,
  `--række-gauge`, `--yokedybde`, …) — fuld bagudkompatibilitet.
- **CLI:** materialer-flag forbliver danske som primær (kunde-vendte
  navne) men accepterer nu engelske aliases: `--garn`/`--yarn`,
  `--garnløbe`/`--yarn-run`/`--meterage`, `--pinde`/`--needles`,
  `--nål`/`--hook`, `--år`/`--year`, `--note`/`--notes`.
- 15 nye tests i `lib/visualisering/tests/test_cli_flags.py` der
  verificerer alias-ækvivalens via subprocess-kald af begge CLI'er.

## [0.5.0] - 2026-04-29 (Fase 5 iter 5: Strikkeklub + garnsubstitution)

### Added
- `scripts/strikkeklub.py`: batch-mode der tager en CSV med medlemmer
  og genererer en HTML-opskrift pr. medlem, et samlet `index.html` og
  en zip-fil. Adapters for 8 konstruktioner (knit + crochet) med
  danske og engelske aliaser. Ukendte CSV-kolonner ender som
  per-medlem-noter.
- `examples/strikkeklub_eksempel.csv` med 7 fiktive medlemmer.
- `lib/visualisering/yarn_alternatives.py`: `build_alternatives()`,
  `attach_alternatives()` og rendere for HTML-aside og markdown.
  Foreslår justeret pind/nål via gauge-ratio.
- `--substitut` (alias `--garn-alternativer`) flag i begge
  `scripts/generate.py`. Giver `<aside class="yarn-alternatives">` i
  HTML og `## Garn-alternativer` i markdown.
- 7 ekstra garn i `yarn_db.YARNS` (Drops Nepal, Drops Wish, Hobbii
  Soft Like Cotton, Sandnes Smart, Cascade Eco+, Drops Sky, Drops
  Lace) så aran/worsted/lace-buckets har nok kandidater.
- 15 nye tests i `lib/visualisering/tests/` (7 strikkeklub, 8
  yarn-alternatives). Total: 257 tests.

### Fixed
- `prosa._facts()` manglede en `yoke_depth`-fact, hvilket gav KeyError
  for visse raglan-seeds. Fact udledes nu fra `inputs.yoke_depth_cm`.

## [0.4.0] - 2026-04-29 (Fase 5 iter 4: Colorwork-charts + prosa + social)

### Added
- `lib/visualisering/chart_symbols.colorwork_chart()`: SVG-renderer
  der tegner farvet stranded-chart med per-celle `<rect class="cw-cell
  cw-{key}">`, alternerende række-numre, indbygget farve-legend og
  valgfri repeat-bracket.
- `lib/visualisering/motifs/`: bibliotek med 5 motiver (`stars`,
  `diagonal`, `simple_dots`, `snowflake_band`, `icelandic_rose_band`).
- `colorwork_swatch`-konstruktion (#11 i strik): flad prøvelap med
  tile'et motiv og garter-kanter. Validerer at inner-sts og rows er
  multipla af motif-dimensioner.
- `--motif` flag på `yoke-stranded` med automatisk repeat-snap.
- `lib/visualisering/prosa.py`: template-baseret prosa-intro med
  per-konstruktion fragment-bibliotek på dansk og engelsk.
  Deterministisk seed fra `name + construction + gauge`.
- `lib/visualisering/social.py` + `templates/social_card.html` +
  `assets/social.css`: social-media preview i `square` (1080×1080) og
  `story` (1080×1920). HTML-fallback hvis Chrome mangler.
- `--no-prosa` og `--social {square,story,...}` flags på begge CLI'er.
- 38 nye tests (20 colorwork, 10 prosa, 8 social).

## [0.3.0] - 2026-04-29 (Fase 5 iter 3: Lace-charts + sizing + Pages)

### Added
- `lib/visualisering/chart_symbols.py`: ren-Python SVG-symbol-bibliotek
  (knit, purl, k2tog, ssk, yo, cdd, k3tog, sl1, no-stitch) plus
  `chart_grid()`, `legend_entries()` og CSS-styling. Ingen tredjeparts
  fonts.
- `lace_shawl`-konstruktion (#10 i strik) med `LaceRepeat`-validering,
  `feather_and_fan`-default repeat, garter-kant og automatisk
  repeat-fit på bredde og længde. Eksporterer `inputs["lace_chart"]`
  som HTML-rendereren tegner som `<figure class="chart">`.
- `lib/visualisering/sizing.py`: `CHILD_SIZES` for 9 alders-bånd med
  `head_circumference_cm`, `chest_cm`, `foot_length_cm`,
  `sleeve_length_cm`. Re-eksporteret fra både `knitlib/sizing.py` og
  `croclib/sizing.py`.
- `--age` flag på `hue`, `raglan`, `sokker`, `sweater`,
  `compound-raglan`, `yoke-stranded` (auto-fylder mål; eksplicit
  override vinder).
- `scripts/build_examples.py`: bygger 10 eksempler + index +
  `assets/` til GitHub Pages-deploy.
- `.github/workflows/pages.yml`: build + deploy af `_site/`.
- 24 nye tests (9 lace, 9 sizing, 3 build_examples, 3 hækl-sizing).

## [0.2.1] - 2026-04-29 (Fase 5 iter 2: Amigurumi-figur + sværhedsgrad + garn-DB)

### Added
- `amigurumi_figur`-konstruktion: sammensætter krop + hoved + 2 ører +
  2 arme + 2 ben (sphere + cylinder med `closed_top=True`) til en
  figur. Profiler: `bjørn` (default) og `kanin`. Samle-tekst i en
  `Samling`-sektion.
- `Pattern.difficulty: str` med 4 niveauer (`beginner`, `easy`,
  `intermediate`, `advanced`). Render i cover-undertitel via
  `{{DIFFICULTY_LINE}}` på både dansk og engelsk.
- `lib/visualisering/yarn_db.py`: 15 garn-records (Drops, Sandnes,
  Önling, Hobbii, Cascade, Rowan) med `Yarn`-dataclass,
  `weight_class`-validering, fuzzy `lookup_yarn()`,
  `suggest_substitute()`, `apply_yarn_to_pattern()`,
  `auto_gauge_from_yarn()` og `auto_hook_or_needle()`.
- `--gauge` på hækl-CLI er nu valgfri hvis `--garn` kan udfylde den.
- 28 nye tests (12 difficulty + 8 amigurumi-figur, 9 yarn-DB,
  serialiserings-tests).

## [0.2.0] - 2026-04-29 (Fase 5 iter 1+2: Avancerede konstruktioner + CI)

### Added
- 3 nye strik-konstruktioner: `compound_raglan` (uafhængig grading af
  body vs sleeve via staggered indtagning), `half_pi_shawl`
  (Zimmermanns verificerede `2·center+3`-progression),
  `yoke_stranded` (Tin Can Knits' 0.75/0.70 faktorer + `repeat_fit`
  motiv-snap + tekst-baseret color chart).
- `short_rows_shawl`-konstruktion: garter-tab crescent med
  `cast_on + 2·increase_rows`-formel, korte-rækker-cadence og
  RowValidator pr. række.
- 2 nye hækl-konstruktioner: `c2c_blanket` (corner-to-corner
  diagonal, `c2c_total_blocks`/`c2c_total_dc` closed-form) og
  `mandala` (rund mandala med RoundSpec-DSL og default progression).
- 3 nye stitches: `pop` (popcorn), `pic` (picot, decorativ),
  `cl3` (3-dc-cluster) med danske aliaser.
- `.github/workflows/ci.yml`: 2 jobs (`test` + `smoke`) der kører
  begge test-suites og 4 CLI-røg-tests på pull request og push til
  main. Python 3.12, ubuntu-latest, pip-cache.
- 64 nye tests (30 advanced strik, 22 hækl, 12 short-rows + sværhed).

## [0.1.0] - 2026-04-29 (Fase 0-3: Refaktor + research + hækling + polish)

### Added
- **Fase 0:** Refaktor af monolitisk `skills/strikkeopskrift/` til
  delt `lib/visualisering/` (Pattern, bookkeeping, shaping, gauge,
  svg, html, assets, components, templates) og to skills
  (`strikning`, `hækling`-stub). Knit-stitches isoleret i
  `knitlib/stitches.py`; `KnitRow(Row)` med `.k()/.p()/.op()`.
- **Fase 1:** Tre research-rapporter i `PLAN-research/`
  (strik-konstruktioner, hækling-fundament, modern PDF-design).
- **Fase 2:** Hækling-skill bygget op fra grunden:
  `croclib/stitches.py` (US-canonical + UK + dansk aliaser, magic
  ring, ch_sp-tracking-felter), `croclib/crorow.py`,
  `croclib/svg.py` (amigurumi-diagram, granny-square, scarf),
  `croclib/html.py`. Konstruktioner: `amigurumi_sphere`,
  `amigurumi_cylinder`, `amigurumi_taper`, `granny_square`,
  `haekle_tørklæde`. Hæklenål-logo. CLI med 4 subcommands.
- **Fase 3:**
  - `lib/visualisering/pdf.py`: `--pdf` flag der finder Chrome
    cross-platform og kører `--headless --print-to-pdf`.
  - Materialer-flags: `--garn`, `--garnløbe`, `--pinde`/`--nål`,
    `--designer`, `--år`, `--note` (repeterbart). Render i
    cover-designer-linje + `<ul class="materials-list">`.
  - i18n: `lib/visualisering/lang/translations.py` med `t()`,
    `register_translations()` og `--lang da|en` flag på begge CLI'er.
    Dækker shell + faste labels (cover, schematics, materials,
    abbreviations, last-page); konstruktion-step-tekst forbliver
    dansk.
  - `lib/visualisering/preview.py`: live-server med
    `ThreadingHTTPServer`, `os.walk`-baseret mtime-watch, JSON
    `/_changed?since=<ts>` endpoint og auto-reload-snippet.
    `scripts/preview.py --serve` på begge skills.
  - 2 nye strik-konstruktioner: `sokker` (top-down med heel flap +
    gusset, Sara Morris paritets-formel) og `bottom_up_sweater`
    (Zimmermann EPS).
  - 2 nye hækl-konstruktioner: `filet` (pixel-pattern på dc + ch
    mesh, `3·W+1`-formel) og `tunisian` (TSS, separat `TunisianRow`
    med forward+return-pass-struktur).
  - Refaktor: pluggable construction renderers via
    `register_domain_renderer()` + `register_renderer()`. Pattern
    markeres med `inputs["_domain"] = "knit"|"crochet"`.

[Unreleased]: https://github.com/mikkelkrogsholm/maskemania/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.5.0
[0.4.0]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.4.0
[0.3.0]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.3.0
[0.2.1]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.2.1
[0.2.0]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.2.0
[0.1.0]: https://github.com/mikkelkrogsholm/maskemania/releases/tag/v0.1.0
