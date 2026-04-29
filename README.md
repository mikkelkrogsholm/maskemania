<p align="center"><img src="assets/logo.png" alt="maskemania" width="720"></p>

# maskemania

Open source-generator til validerede strikke- og hækleopskrifter på
dansk og engelsk. AI er tekstforfatter, Python er regnemaskinen,
mennesket er prøvestrikkeren.

LLM'er kan ikke holde hundredevis af maskeantal i hovedet konsistent.
Eksperimenter som SkyKnit har demonstreret det. Dette repo omgår
problemet ved at lade Python lave matematikken og validere at hver
række/omgang balancerer (`consumed sts == sts_before`), så vi ender med
en opskrift der faktisk hænger sammen — uanset om det er en hue, en
top-down raglan, et corner-to-corner-tæppe eller en stranded yoke.

## Quick start

Krav: Python 3.10+. Ingen pip-pakker.

```bash
git clone https://github.com/mikkelkrogsholm/maskemania.git
cd maskemania

# En hue (markdown til terminalen)
python3 skills/strikning/scripts/generate.py --format md hue \
  --head 56 --sts 22 --rows 30 --yarn "Drops Air"

# En amigurumi-kugle med Drops Air (gauge auto-fyldes fra yarn-DB)
python3 skills/hækling/scripts/generate.py --format md amigurumi \
  --diameter 8 --yarn "Drops Air"

# En raglan-sweater som PDF (Chrome headless)
python3 skills/strikning/scripts/generate.py --pdf raglan.pdf raglan \
  --bust 94 --sts 22 --rows 30 --ease 5 --sleeve-length 45

# En social-media preview (1080×1080 PNG)
python3 skills/strikning/scripts/generate.py --social square \
  --out hue.png hue --head 56 --sts 22 --rows 30
```

`--format` understøtter `md`, `json`, `html`. `--lang en` skifter cover,
materialer og forkortelser til engelsk (step-teksten i opskriften
forbliver dansk indtil videre).

### PDF-eksport

PDF-output bruger som standard [WeasyPrint](https://weasyprint.org/) —
en Python-native HTML→PDF-renderer med native CSS Paged Media-support
og ingen Chromium-afhængighed. Installér med:

```bash
pip install weasyprint
```

Hvis WeasyPrint ikke er installeret, falder vi automatisk tilbage til
headless Chrome / Chromium / Edge / Brave (og giver en klar fejl hvis
ingen af delene findes). Tving en specifik renderer med
`--pdf-renderer {auto,weasy,chrome}`. Default er `auto`.

### Flag-konvention

Tekniske inputs (mål, gauge) bruger **engelsk kebab-case som primær**
(`--head`, `--bust`, `--neck`, `--width`, `--length`, `--height`,
`--foot-length`, `--shoe-size`, `--sleeve-length`, `--upper-arm`,
`--row-gauge`, `--yoke-depth`, …). Hvert teknisk flag har en dansk
alias (`--hovedmål`, `--bryst`, `--hals`, `--bredde`, `--længde`,
`--højde`, `--fodlængde`, `--skostørrelse`, `--ærme`, `--overarm`,
`--række-gauge`, `--yokedybde`, …).

Materialer bruger **dansk som primær** fordi de er kunde-vendte
(`--garn`, `--garnløbe`, `--pinde`, `--nål`, `--år`, `--note`), men
accepterer engelske aliases (`--yarn`, `--yarn-run`/`--meterage`,
`--needles`, `--hook`, `--year`, `--notes`).

Begge varianter virker uden modifikationer i alle eksisterende scripts.

## Konstruktioner

20 konstruktioner i alt. Sværhedsgrad følger `Pattern.difficulty` i
koden.

### Strikning (11)

| Navn | CLI-subcommand | Sværhedsgrad |
|---|---|---|
| Hue | `hue` | beginner |
| Tørklæde | `tørklæde` | beginner |
| Top-down raglan | `raglan` | easy |
| Bottom-up sweater (Zimmermann EPS) | `sweater` | easy |
| Sokker (top-down med hæl + gusset) | `sokker` | intermediate |
| Compound raglan | `compound-raglan` | intermediate |
| Half-pi shawl (Zimmermann) | `half-pi` | intermediate |
| Short-rows crescent shawl | `short-rows` | intermediate |
| Lace shawl (feather-and-fan) | `lace` | intermediate |
| Colorwork-prøvelap | `colorwork` | easy |
| Stranded yoke (Icelandic-style) | `yoke-stranded` | advanced |

### Hækling (9)

| Navn | CLI-subcommand | Sværhedsgrad |
|---|---|---|
| Amigurumi-kugle | `amigurumi` | beginner |
| Amigurumi-cylinder | `cylinder` | beginner |
| Amigurumi-figur (bjørn / kanin) | `figur` | easy |
| Granny square | `granny` | beginner |
| Hæklet tørklæde | `tørklæde` | beginner |
| Filet (pixel-pattern) | `filet` | easy |
| C2C-blanket (corner-to-corner) | `c2c` | easy |
| Mandala | `mandala` | intermediate |
| Tunisian (TSS) | `tunisian` | intermediate |

## Features

- **Pattern-validator.** Hver række/omgang valideres via `RowValidator`
  (`consumed sts == sts_before`). Sektioner kan validere kontinuitet
  via `Pattern.validate_continuity()`. Geometriske afvigelser > 3 cm
  fra mål logges som warnings.
- **Dansk og engelsk.** `--lang da|en` skifter cover, materialer,
  schematics-captions, forkortelser og last-page. Step-tekst i selve
  opskriften er stadig dansk-først.
- **Garn-database.** 22 records (Drops, Sandnes, Önling, Hobbii,
  Cascade, Rowan) med fuzzy lookup. `--garn "Drops Air"` auto-fylder
  gauge, pind/hæklenål, garnløb. Fiber-baseret substitut-forslag via
  `--substitut`.
- **Børnesizing.** `CHILD_SIZES` for 9 alders-bånd (`0-3M` til
  `10-12y`). `--age 6-12M` auto-fylder hovedomkreds, brystmål,
  fodlængde, ærmelængde.
- **Lace- og colorwork-charts.** Ren-Python SVG-symboler (knit, purl,
  k2tog, ssk, yo, cdd, k3tog, sl1, no-stitch) + 5 stranded-motiver
  (`stars`, `diagonal`, `simple_dots`, `snowflake_band`,
  `icelandic_rose_band`). Ingen tredjeparts-fonts.
- **Prosa-intro.** Per-konstruktion fragment-bibliotek på dansk og
  engelsk, deterministisk seedet fra opskriftens metadata. Slå fra
  med `--no-prosa`.
- **Social-media preview.** `--social square` (1080×1080) eller
  `--social story` (1080×1920) genererer en PNG via Chrome headless.
  HTML-fallback hvis Chrome mangler.
- **Direkte PDF-eksport.** `--pdf out.pdf` finder Chrome cross-platform
  og kører `--headless --print-to-pdf`.
- **Strikkeklub-batch.** `scripts/strikkeklub.py CSV --out DIR`
  genererer en HTML-opskrift pr. medlem + index + zip.
- **Pages-site.** `scripts/build_examples.py --out _site` bygger 10
  eksempler + index. Deployes via `.github/workflows/pages.yml`.
- **CI.** `.github/workflows/ci.yml` kører begge test-suites + 4 CLI
  smoke-tests på pull request og push til main.

## Tests

```bash
# Strik (126 tests)
python3 -m unittest discover -s skills/strikning/tests

# Hækl (98 tests)
python3 -m unittest discover -s skills/hækling/tests

# Delt lib (33 tests)
python3 -m unittest discover -s lib/visualisering/tests
```

Total: 257 tests. Alle skal være grønne før merge. CI håndhæver det.

## Mappestruktur

```
maskemania/
├── lib/
│   └── visualisering/      # delt Python-pakke
│       ├── pattern.py      # Pattern, Section, Step
│       ├── bookkeeping.py  # Row, RowValidator, Stitch
│       ├── shaping.py      # Bresenham, evenly_spaced
│       ├── gauge.py        # cm <-> sts/rows + rounding
│       ├── sizing.py       # CHILD_SIZES + helpers
│       ├── svg.py          # schematics + helpers
│       ├── html.py         # pluggable domain renderers
│       ├── pdf.py          # Chrome headless wrapper
│       ├── preview.py      # live HTTP-server
│       ├── prosa.py        # template-baseret intro
│       ├── social.py       # 1:1 / 9:16 preview
│       ├── chart_symbols.py# lace + colorwork charts
│       ├── motifs/         # stranded-motiv-bibliotek
│       ├── yarn_db.py      # 22-garn database
│       ├── yarn_alternatives.py
│       ├── lang/           # da/en translations
│       ├── assets/         # style.css, paged.polyfill.js, social.css
│       ├── components/     # HTML-fragments
│       ├── templates/      # outer shells (pattern.html, social_card.html)
│       └── tests/          # 33 tests
├── skills/
│   ├── strikning/
│   │   ├── SKILL.md
│   │   ├── knitlib/
│   │   │   ├── stitches.py
│   │   │   ├── knitrow.py
│   │   │   ├── ease.py
│   │   │   ├── sizing.py   # re-eksport af shared sizing
│   │   │   └── constructions/  # 11 konstruktioner
│   │   ├── reference/      # forkortelser_da/en, sizing_guide, ease_guide
│   │   ├── scripts/        # generate.py, preview.py
│   │   ├── tests/          # 126 tests
│   │   └── assets/logo.svg
│   └── hækling/
│       ├── SKILL.md
│       ├── croclib/
│       │   ├── stitches.py
│       │   ├── crorow.py
│       │   ├── svg.py
│       │   ├── html.py
│       │   ├── sizing.py
│       │   └── constructions/  # 9 konstruktioner
│       ├── scripts/
│       ├── tests/          # 98 tests
│       └── assets/logo.svg
├── scripts/
│   ├── build_examples.py   # bygger _site/ til Pages
│   └── strikkeklub.py      # CSV -> batch af opskrifter
├── examples/
│   └── strikkeklub_eksempel.csv
├── PLAN.md                 # vision + roadmap
├── PLAN-research/          # iterations-rapporter
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Bidrage

Læs [`CONTRIBUTING.md`](CONTRIBUTING.md). Vigtigste regel:

> AI digter aldrig maskeantal. Al matematik kommer fra `lib/visualisering`,
> `knitlib` eller `croclib` — eller direkte fra brugeren.

Tilføjelse af en ny konstruktion følger en checkliste (Stitch-validering
→ Construction-modul → CLI-subcommand → tests → translations →
difficulty → CHANGELOG-hint). Test-strikning og test-hækling er den
mest værdifulde form for bidrag — generatoren fanger matematiske fejl,
ikke om en opskrift er behagelig at strikke.

## Licens

MIT. Se [`LICENSE`](LICENSE).

## Status

Pre-1.0. Versionsnumrene afspejler iterationer i `PLAN.md`, ikke
semver-promiser om bagudkompatibilitet. Alle 20 konstruktioner er
matematisk validerede gennem `RowValidator`, men ingen er endnu
test-strikket eller test-hæklet i den virkelige verden — det er Fase
4 i planen og afhænger af eksterne bidragsydere. Hvis du strikker eller
hækler en af opskrifterne og finder en afvigelse på mere end 2 cm fra
spec, så åbn et issue. Vi tager imod test-strikkere og test-hæklere med
kyshånd.
