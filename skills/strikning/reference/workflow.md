# Workflow: Input → Generator → Validator → Tekst

Denne skill håndhæver et 4-trins flow. Spring aldrig et trin over.

## Trin 1: Saml input

Krævede oplysninger afhænger af konstruktionen:

**Alle:**
- Strikkefasthed (masker pr. 10 cm, pinde pr. 10 cm) — målt på en prøvelap
- Garn (navn, sammensætning, løbelængde) og anbefalet pindstørrelse
- Sprog (dansk / engelsk)

**Hue:**
- Hovedomkreds (eller størrelseskategori)
- Ønsket ease (default: −3 cm)
- Højde (default: ~21 cm til kronemidte)

**Tørklæde:**
- Bredde og længde i cm
- Mønster (default: glatstrik)
- Kantmasker / kantpinde

**Top-down raglan:**
- Brystmål (eller størrelse)
- Ease (default: +5 cm = klassisk)
- Bærestykkedybde (default: brystomkreds / 4)
- Kropslængde fra ærmegab til skørt
- Ærmelængde fra ærmegab til manchet
- Halsomkreds
- Håndledsmål

Hvis brugeren ikke kender et tal, så **spørg** før du går videre.
Brug `reference/sizing_guide.md` til at foreslå standardværdier, men
gør det tydeligt at det er et estimat.

## Trin 2: Kør generator

Brug `scripts/generate.py`:

```bash
python3 ~/.claude/skills/strikning/scripts/generate.py hue \
  --head 56 --sts 22 --rows 30 --ease -3
```

Eller importer `knitlib.constructions` direkte og kald
`generate_hue(spec)`, `generate_tørklæde(spec)`, `generate_raglan(spec)`.

Resultatet er et `Pattern`-objekt med strukturerede sektioner og masketal.

## Trin 3: Valider

Generatoren validerer automatisk:
- Maskeantal går op for hver pind/omgang
- Mønsterrapporter divideres rent op i maskeantallet
- Sektioner forbinder kontinuert (sts_after = next.sts_before)
- Geometriske afvigelser fra mål logges som warnings

Hvis validatoren rejser en `ValidationError`: **stop**. Find årsagen.
Skriv aldrig en opskrift der har fejlet validering.

## Trin 4: Formuler opskrift

Brug `templates/opskrift_da.md` (eller _en) til at lægge en pæn dansk/engelsk
opskrift over den strukturerede output. LLM må gerne hjælpe med
formulering, men aldrig ændre tal eller maskeantal.

Inkluder altid:
- Materialer (garn, pinde, evt. tilbehør)
- Strikkefasthed
- Mål (færdige + ease)
- Forkortelses-liste (fra `reference/forkortelser_da.md`)
- Selve opskriften, sektion for sektion
- Eventuelle noter og advarsler fra validatoren
- Anbefaling om at strikke prøvelap

## Trin 5: Anbefal teststrik

Den endelige opskrift er stadig et udkast indtil nogen har strikket den.
Vær åben om det. Ingen LLM-genereret opskrift er færdig før den er testet.
