# Standardstørrelser

Kilde: Craft Yarn Council Standard Body Measurements / Sizing.
Tal er gennemsnit, ikke garantier. **Spørg altid brugeren om de har egne
mål** — det er det eneste der virkelig tæller.

## Brystmål, kvinder (cm)

| Str. | Brystmål |
|---|---|
| XS  | 71–76 |
| S   | 81–86 |
| M   | 91–96.5 |
| L   | 101.5–106.5 |
| XL  | 111.5–117 |
| 2XL | 122–127 |
| 3XL | 132–137 |
| 4XL | 142–147 |

## Bryst, mænd (cm)

| Str. | Brystmål |
|---|---|
| S   | 86–91 |
| M   | 97–102 |
| L   | 107–112 |
| XL  | 117–122 |
| 2XL | 127–132 |

## Hovedomkreds (cm)

| Aldersgruppe | Hovedomkreds |
|---|---|
| Spædbarn (0–3 mdr.) | 33–38 |
| Baby (3–12 mdr.) | 38–46 |
| Småbarn | 46–48 |
| Barn | 48–51 |
| Teenager | 51–56 |
| Voksen S | 53–55 |
| Voksen M | 55–57 |
| Voksen L | 57–59 |
| Voksen XL | 59–61 |

## Andre nyttige mål, voksen (cm)

| Str. | Håndled | Overarm | Kropslængde u.arm→sk. |
|---|---|---|---|
| XS  | 14 | 26 | 35 |
| S   | 15 | 28 | 36 |
| M   | 16 | 31 | 37 |
| L   | 17 | 34 | 38 |
| XL  | 18 | 37 | 39 |
| 2XL | 19 | 41 | 40 |

## Bærestykke-dybde (raglan, top-down)

Tommelfingerregel: bærestykkets dybde fra hals til ærmegab ≈ brystomkreds / 4.

| Str. | Bærestykke-dybde |
|---|---|
| XS  | 19 |
| S   | 20 |
| M   | 21 |
| L   | 22 |
| XL  | 23 |
| 2XL | 24 |

## Børnemål (cm)

Tabellen lever i `lib/visualisering/sizing.py` og deles mellem strik- og
hækle-skill. Tallene er population-gennemsnit fra Craft Yarn Council
"Children" + PetiteKnit børnestørrelser + Drops Design babymål — brug
dem som *udgangspunkt*, og spørg altid om brugerens egne mål.

| Alder   | Hoved | Bryst | Fod-længde | Ærmelængde |
|---------|-------|-------|------------|------------|
| 0-3M    | 38    | 41    |  9.0       | 16         |
| 3-6M    | 41    | 43    | 10.0       | 18         |
| 6-12M   | 44    | 46    | 11.5       | 20         |
| 1-2y    | 47    | 49    | 13.0       | 23         |
| 2-4y    | 49    | 53    | 15.0       | 27         |
| 4-6y    | 51    | 57    | 17.0       | 30         |
| 6-8y    | 52    | 62    | 19.0       | 33         |
| 8-10y   | 53    | 67    | 21.0       | 36         |
| 10-12y  | 54    | 72    | 22.5       | 39         |

CLI-kortvej: brug `--age 6-12M` (eller en anden bånd-label) på
konstruktioner der tager body-mål — `hue`, `raglan`, `sweater`,
`compound-raglan`, `yoke-stranded`, `sokker`. Eksplicitte `--head`,
`--bust`, `--foot`, `--foot-length`, `--sleeve-length` vinder altid over
`--age`-defaults.

Kilder:
- Craft Yarn Council Standard Body Measurements / Sizing
  ([craftyarncouncil.com](https://www.craftyarncouncil.com)).
- PetiteKnit — Børnestørrelser (børnehue, raglan-strik).
- Drops Design — Mål til børnetøj 0-12 år.
