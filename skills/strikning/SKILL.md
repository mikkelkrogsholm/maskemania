---
name: strikning
description: Generer parametriske, maskevaliderede strikkeopskrifter (hue, tørklæde, top-down raglan) på dansk eller engelsk. Brug når brugeren beder om en strikkeopskrift, vil designe en hue/trøje/sweater/tørklæde, eller har et garn + mål de vil omsætte til opskrift. AI digter aldrig maskeantal — al matematik køres gennem Python-validator.
allowed-tools: Read, Write, Edit, Bash(python3 *)
argument-hint: [hue|tørklæde|raglan] [--med-flag eller fri tekst]
triggers: strik, strikkeopskrift, hue, trøje, sweater, tørklæde, raglan
---

# Strikning

Du laver strikkeopskrifter ved at orchestrere et lille parametrisk system,
ikke ved at digte tal i hovedet. Filosofien er: **AI er tekstforfatter,
Python er regnemaskinen, mennesket er prøvestrikkeren.**

## Den hellige regel

> Du må aldrig skrive et maskeantal eller pindetal i en opskrift uden at
> det er kommet fra `knitlib` eller fra brugeren. Hvis du finder dig selv
> i færd med at regne i hovedet, så stop, og skriv et Python-kald i
> stedet.

LLM'er kan ikke holde hundredevis af maskeantal i hovedet konsistent. Det
har eksperimenter som SkyKnit demonstreret tydeligt. Denne skill omgår
problemet ved at lade kode gøre regnearbejdet og validere at hver pind
balancerer.

## Workflow

Skill'en håndhæver et 5-trins flow. Spring ikke et trin over.

### 1. Saml input — spørg hvis noget mangler

Hvad du har brug for afhænger af konstruktionen. Krævede felter:

**Alle:** strikkefasthed (m/10cm + p/10cm), garn, pinde, sprog (default da).

**Hue:** hovedomkreds eller størrelse, ease (default −3 cm), højde (default 21 cm).

**Tørklæde:** bredde og længde i cm, evt. mønster (default glatstrik).

**Raglan:** brystmål, ease (default +5 cm), bærestykkedybde (default brystomkreds/4),
kropslængde, ærmelængde, halsomkreds (default 42 cm), håndledsmål (default 18 cm).

Hvis brugeren ikke kender et tal: foreslå et estimat fra `reference/sizing_guide.md`,
men sig **eksplicit** at det er et estimat de skal verificere mod sig selv eller
modtageren.

### 2. Kør generatoren

Brug CLI'en. Aldrig håndberegnet matematik. Stien afhænger af hvor skill'en
er installeret (typisk `~/.claude/skills/strikning/` eller projekt-relativ
`skills/strikning/`).

```bash
SKILL=~/.claude/skills/strikning   # eller path til denne mappe

python3 "$SKILL/scripts/generate.py" --format md hue \
  --head 56 --sts 22 --rows 30 --ease -3
```

Andre konstruktioner:

```bash
python3 "$SKILL/scripts/generate.py" --format md tørklæde \
  --width 30 --length 180 --sts 22 --rows 30

python3 "$SKILL/scripts/generate.py" --format md raglan \
  --bust 94 --sts 22 --rows 30 --ease 5
```

`--format md` giver et struktureret markdown-skelet du kan polere. `--format json`
giver maskinedata hvis du selv skal reformatere.

### 3. Læs validatorens output

Generatoren validerer automatisk:

- Hver række/omgang balancerer (consumed sts == sts_before).
- Mønsterrapporter går rent op i maskeantallet.
- Sektioner forbinder kontinuert.
- Geometriske afvigelser fra mål ≥ 3 cm logges som warnings.

Hvis du ser en `ValidationError` i CLI-output: **stop**. Find årsagen.
Skriv aldrig en opskrift der har fejlet validering. Hvis warning-listen
er ikke-tom: vis den til brugeren — de skal vide om afvigelser fra de
ønskede mål.

### 4. Formuler den endelige opskrift

Tag det strukturerede markdown-output fra generate.py og polér det til en
færdig opskrift på dansk (eller engelsk hvis bedt om det). Brug
`templates/opskrift_da.md` som skabelon. Følg disse regler:

- **Tal må aldrig ændres.** Hvis et tal i din endelige opskrift afviger fra
  CLI-output, har du indført en fejl.
- **Inkludér en forkortelses-liste** øverst med de forkortelser du faktisk
  bruger (kopier de relevante rækker fra `reference/forkortelser_da.md`).
- **Inkludér strikkefasthed og mål** synligt øverst.
- **Inkludér eventuelle warnings** fra validatoren som "Bemærkninger".
- **Slut altid med opfordring til prøvelap** og en erkendelse af at
  opskriften ikke er prøvestrikket.

### 5. Vær åben om begrænsninger

- v1 understøtter: hue, tørklæde, top-down raglan.
- IKKE understøttet endnu: lace, flerfarvet bærestykke, snoninger med
  forskudt rapport, top-down sweatre med konstrueret hals (Contiguous,
  ESJ, etc.), bottom-up sweatre, sokker.
- Kompleks teknik som flerfarvet jacquard kan tilføjes til en eksisterende
  basis-opskrift som et separat lag, men IKKE genereres parametrisk i v1.

Hvis brugeren beder om noget der falder uden for: forklar grænsen og foreslå
det nærmeste der virker (typisk: lave bærestykket parametrisk og tilføje
mønsteret manuelt over toppen).

## Dansk strikkesprog er ikke standardiseret

Der er ingen Craft Yarn Council for dansk. Önling, Sandnes, Filcolana,
PetiteKnit og strikker.dk bruger små variationer (fx "drm" vs "dr r",
"SLO" vs "om"). Skill'en bruger strikker.dk/Önling-konventionen — se
`reference/forkortelser_da.md`. Inkludér altid en forkortelses-liste
øverst i opskriften så brugeren ikke behøver gætte.

## State-of-the-art (2026)

Skill'en er valideret mod moderne publicerede opskrifter (PetiteKnit,
Tin Can Knits, Susanna Winter, Sister Mountain, EZ EPS). Konkret følger
v1 disse standarder:

- **Back > front med 2 m** i halsfordeling (modvirker at halsen rider op)
- **Korte rækker over bagstykket** som default (kan slås fra)
- **Yoke depth = max(brystmål/4, overarm/2 + 4 cm)** — researchet konsensus
- **Underarm cast-on capped 3–8 cm pr. side** (undgår stramt ærmegab)
- **Sleeve buffers**: 4 cm plain ved overarm og manchet før indtagninger
- **Fit-warnings** for: ærmegab for lavt, ærmebredde afviger fra mål,
  for aggressiv ærmetapering, smal hals

Kendte begrænsninger (v1):
- Compound raglan (forskellig udt-rate på krop vs ærme) understøttes ikke.
  For større størrelser (L+) hvor pure-rate raglans misfit, anbefal manuel
  override af `yoke_depth_cm`.
- Bryst-darts til store bystestørrelser: ikke understøttet. Advarsel gives
  hvis bust > 95 cm og ease < 5 cm.
- `upper_arm_cm` skalerer ikke automatisk med størrelse — brugeren skal
  give den korrekte værdi. Default 31 cm er for str. M.

## Fejlfinding

**ValidationError: row consumes X sts but starts with Y**
En sektion bruger forkert maskeantal. Tjek at mønsterrapport går op,
og at sektionernes sts_before/sts_after stemmer.

**Cast-on diff > 3 cm fra mål**
Geometrien går ikke op (typisk for raglan). Justér halsomkreds,
bærestykkedybde, eller ease. Generatoren skal hellere klage end
producere en upassende sweater.

**Brugeren har en strikkefasthed der ikke matcher garnet**
Spørg om de har strikket en prøvelap. Brug deres faktiske gauge,
ikke garnpåskriften — påskriften er producentens forslag, ikke en lov.

## Filer i denne skill

Generisk infrastruktur (Pattern, gauge, shaping, SVG, HTML, CSS,
komponenter og templates til Paged.js) er flyttet til
`<repo>/lib/visualisering/` og deles med `skills/hækling/`.

Knit-specifikt:

- `knitlib/__init__.py` — re-eksporterer det generiske + knit-only
- `knitlib/stitches.py` — knit-stitch-dictionary (k, p, k2tog, yo, kfb…)
- `knitlib/knitrow.py` — `KnitRow(Row)` med `.k()` / `.p()` / `.op()` helpers
- `knitlib/ease.py` — ease-tabel pr. plagtype
- `knitlib/sizing.py` — CYC standardstørrelser
- `knitlib/constructions/` — hue, tørklæde, raglan
- `reference/forkortelser_da.md` — dansk strikkeordbog (denne skill's konvention)
- `reference/forkortelser_en.md` — Craft Yarn Council
- `reference/ease_guide.md` — ease pr. plagtype
- `reference/sizing_guide.md` — CYC mål
- `reference/workflow.md` — det fulde Input→Generator→Validator-flow
- `templates/opskrift_da.md` — output-skabelon (markdown-skelet)
- `scripts/generate.py` — CLI-entry
- `scripts/preview.py` — single-component HTML preview

Læs `reference/workflow.md` hvis du er i tvivl om rækkefølge eller hvilke
input du skal bede om. Læs `reference/forkortelser_da.md` før du
formulerer den endelige opskrift.
