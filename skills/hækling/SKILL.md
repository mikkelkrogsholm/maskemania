---
name: hækling
description: Generer parametriske, maskevaliderede hækleopskrifter (amigurumi-kugle, granny square, hæklet tørklæde) på dansk eller engelsk. Brug når brugeren beder om en hækleopskrift, vil designe en amigurumi-figur, et tæppe i granny squares, eller har et garn + mål de vil omsætte til opskrift. AI digter aldrig maskeantal — al matematik køres gennem Python-validator.
allowed-tools: Read, Write, Edit, Bash(python3 *)
argument-hint: [amigurumi|cylinder|granny|tørklæde] [--med-flag eller fri tekst]
triggers: hækl, hækleopskrift, amigurumi, granny, hæklenål, hækle
---

# Hækling

Du laver hækleopskrifter ved at orchestrere et lille parametrisk system,
ikke ved at digte tal i hovedet. Filosofien er den samme som for
strikning: **AI er tekstforfatter, Python er regnemaskinen, mennesket
er prøvehæklerne.**

## Den hellige regel

> Du må aldrig skrive et maskeantal i en hækleopskrift uden at det er
> kommet fra `croclib` eller fra brugeren. Hvis du finder dig selv
> i færd med at regne i hovedet, så stop, og skriv et Python-kald i
> stedet.

LLM'er kan ikke holde hundredevis af maskeantal i hovedet konsistent.
Denne skill lader Python gøre regnearbejdet og validere at hver omgang
balancerer.

## Workflow

Skill'en håndhæver et 5-trins flow. Spring ikke et trin over.

### 1. Saml input — spørg hvis noget mangler

Hvad du har brug for afhænger af konstruktionen. Krævede felter:

**Alle:** strikkefasthed (fm pr. cm eller stm pr. cm), garn, hæklenål,
sprog (default da).

**Amigurumi-kugle:** ønsket diameter i cm, hækle-gauge (typisk 4-5 fm/cm
ved tæt amigurumi-hækling). Valgfrit: ækvator-omg for stuffer-friendly
oval form.

**Cylinder:** diameter, højde, gauge.

**Granny square:** antal omg, evt. farveliste.

**Tørklæde:** bredde og længde i cm, gauge, valg af grundsting (sc/hdc/dc/tr,
default dc).

Hvis brugeren ikke kender et tal: foreslå et estimat, men sig **eksplicit**
at det er et estimat de skal verificere mod sig selv eller modtageren.

### 2. Kør generatoren

Brug CLI'en. Aldrig håndberegnet matematik.

```bash
SKILL=~/.claude/skills/hækling   # eller path til denne mappe

# Amigurumi-kugle
python3 "$SKILL/scripts/generate.py" --format md amigurumi \
  --diameter 8 --gauge 5

# Granny square med farveskift
python3 "$SKILL/scripts/generate.py" --format md granny \
  --rounds 6 --colors rød,blå,grøn,gul

# Hæklet tørklæde
python3 "$SKILL/scripts/generate.py" --format md tørklæde \
  --width 25 --length 150 --gauge 2.5 --stitch dc
```

`--format md` giver et struktureret markdown-skelet du kan polere.
`--format json` giver maskinedata. `--format html --out FIL.html` skriver
et print-klart HTML-dokument med skematik og forkortelses-tabel — åbn i
Chrome → Print → Save as PDF.

### 3. Læs validatorens output

Generatoren validerer automatisk:

- Hver omgang/række balancerer (consumed sts == sts_before).
- Sektioner forbinder kontinuert.
- For amigurumi: kuglens faktiske diameter er tæt på den ønskede.
- Granny squares følger ``12·N``-formlen pr. omg.

Hvis du ser en `ValidationError` i CLI-output: **stop**. Find årsagen.
Skriv aldrig en opskrift der har fejlet validering.

### 4. Formuler den endelige opskrift

Tag det strukturerede markdown-output fra generate.py og polér det til en
færdig opskrift på dansk (eller engelsk hvis bedt om det). Følg disse
regler:

- **Tal må aldrig ændres.** Hvis et tal i din endelige opskrift afviger
  fra CLI-output, har du indført en fejl.
- **Inkludér en forkortelses-liste** øverst med de forkortelser du
  faktisk bruger (fm, lm, km, hstm, stm, dst, udt, indt, MR, omg).
- **Inkludér gauge og mål** synligt øverst.
- **Inkludér eventuelle warnings** fra validatoren som "Bemærkninger".
- **Slut altid med opfordring til prøvelap** og en erkendelse af at
  opskriften ikke er prøvehæklet.

### 5. Vær åben om begrænsninger

- v1 understøtter: amigurumi-kugle, amigurumi-cylinder, granny square
  (klassisk), hæklet tørklæde i sc/hdc/dc/tr.
- IKKE understøttet endnu: filet hækling med chart-input, tunisian, store
  amigurumi-figurer (krop+hoved+arme samlet), modern solid granny,
  hæklede beklædningsgenstande (toppe, sweatre).
- Komplekse teksturer (puff, popcorn, post stitches) kan tilføjes til en
  basis-opskrift som lag, men IKKE genereres parametrisk i v1.

Hvis brugeren beder om noget der falder uden for: forklar grænsen og
foreslå det nærmeste der virker.

## Konvention: US-terminologi internt, dansk i output

Alle stitches er navngivet i US-konvention internt (sc, hdc, dc, tr),
men de danske aliases er bygget ind: `fm`, `hstm`, `stm`, `dst`, `lm`,
`km`, `udt`, `indt`. Output-opskriften bruger dansk som default.

Husk at UK-konventionen er forskellig fra US (UK ``dc`` = US ``sc``,
UK ``tr`` = US ``dc`` osv.) — hvis brugeren citerer en UK-opskrift skal
du normalisere til US før du kører generatoren.

## Filer i denne skill

Generisk infrastruktur (Pattern, gauge, shaping, SVG, HTML, CSS,
komponenter og templates til Paged.js) ligger i
`<repo>/lib/visualisering/` og deles med `skills/strikning/`.

Hækle-specifikt:

- `croclib/__init__.py` — re-eksporterer det generiske + crochet-only
- `croclib/stitches.py` — crochet-stitch-dictionary (sc, hdc, dc, tr,
  sc2tog, dc2tog, magic ring) + dansk/UK-aliases
- `croclib/crorow.py` — `CrochetRow(Row)` med `.ch()`, `.sc()`, `.dc()`,
  `.op()` helpers
- `croclib/svg.py` — hækle-skematikker (amigurumi-diagram, granny-square)
- `croclib/html.py` — hækle-specific HTML-renderer der genbruger lib/visualisering
- `croclib/constructions/` — amigurumi, granny_square, tørklæde
- `scripts/generate.py` — CLI-entry
- `tests/test_croclib.py` — ≥ 25 tests

Læs `PLAN-research/fase-1-agent-b-haekling.md` for den fulde
research-rapport som denne skill bygger på.

## Fejlfinding

**ValidationError: row consumes X sts but starts with Y**
En sektion bruger forkert maskeantal. Tjek at runde-formlen for
amigurumi (6·N) eller granny (12·N) er overholdt.

**Kuglens faktiske diameter afviger fra mål**
Diameteren rundes til nærmeste hele 6er-multiplum (start_count=6 fm).
Justér gauge eller acceptér den nærmeste passende størrelse.

**Brugeren har en gauge der ikke matcher garnet**
Spørg om de har hæklet en prøvelap. Brug deres faktiske gauge,
ikke garnpåskriften.
