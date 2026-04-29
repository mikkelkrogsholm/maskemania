# Bidrag til maskemania

Tak fordi du overvejer at bidrage. Projektet lever af tre slags hjælp:
folk der tilføjer nye konstruktioner, folk der test-strikker eller
test-hækler en eksisterende opskrift og rapporterer afvigelser, og folk
der finpudser sproget i de danske og engelske templates.

## Den hellige regel

> AI digter aldrig maskeantal. Al matematik kommer fra `lib/visualisering`,
> `knitlib` eller `croclib` — eller direkte fra brugeren.

Hvis du finder dig selv i færd med at regne et maskeantal i hovedet (eller
bede en LLM om det), så stop og skriv et Python-kald i stedet. Det er
hele pointen med projektet. Brug `RowValidator` til at sikre at hver
række/omgang balancerer (`consumed sts == sts_before`), og brug
`Pattern.validate_continuity()` til at sikre at sektionerne hænger
sammen.

## Repo-opbygning

```
maskemania/
├── lib/
│   └── visualisering/      # delt Python-pakke (Pattern, gauge, SVG, HTML, charts, prosa, social, yarn-DB)
├── skills/
│   ├── strikning/          # strikkeopskrift-skill
│   │   └── knitlib/
│   │       └── constructions/   # 11 strik-konstruktioner
│   └── hækling/            # hækleopskrift-skill
│       └── croclib/
│           └── constructions/   # 9 hækl-konstruktioner
├── scripts/                # repo-niveau scripts (build_examples, strikkeklub)
├── examples/               # eksempel-CSV'er m.m.
└── PLAN-research/          # iterations-rapporter
```

`lib/visualisering` er domæne-agnostisk infrastruktur. Knit-specifikke
ting (k, p, ssk, raglan-formler, ease-tabeller) hører hjemme i
`skills/strikning/knitlib/`. Hækl-specifikke ting (sc, dc, magic ring,
amigurumi-formler) hører i `skills/hækling/croclib/`.

## Sådan kører du tests

```bash
# Strik (126 tests)
python3 -m unittest discover -s skills/strikning/tests

# Hækl (98 tests)
python3 -m unittest discover -s skills/hækling/tests

# Delt lib (33 tests)
python3 -m unittest discover -s lib/visualisering/tests
```

Total: 257 tests. Alle skal være grønne før merge — kør dem lokalt før
du sender pull request.

For røg-test af CLI'erne:

```bash
bash skills/strikning/tests/edge_cases.sh
```

Krav: Python 3.10+. Ingen pip-pakker. Hvis du vil bruge en, åbn et issue
først.

### PDF-eksport

Hvis du vil teste `--pdf`-output: installer WeasyPrint
(`pip install weasyprint`) — det er den anbefalede primære renderer.
Alternativt skal du have en headless-capable browser installeret
(Chrome, Chromium, Edge eller Brave); vi falder automatisk tilbage til
den hvis WeasyPrint mangler. Test-suiten bruger mocks, så ingen af
delene er nødvendige bare for at køre testsene.

## Sådan tilføjer du en ny konstruktion

Brug denne checkliste — den afspejler hvordan iterationerne i `PLAN.md`
er kørt indtil nu.

1. **Spec-research.** Find 2-3 publicerede opskrifter (PetiteKnit,
   Hobbii, Tin Can Knits, Drops, Ravelry) og udled formlen. Skriv
   research-noter i `PLAN-research/` med kilder. Stitch-niveau
   matematik skal kunne forklares — ingen "magisk konstant".

2. **Stitch-validering.** Tilføj nye stitches i
   `skills/<skill>/<lib>/stitches.py` hvis konstruktionen kræver det.
   Hver stitch skal have en præcis (consumes, produces) signatur. Læg
   danske og engelske aliaser ind i `ALIASES`-dicten.

3. **Construction-modul.** Tilføj `<konstruktion>.py` i
   `skills/<skill>/<lib>/constructions/`. Følg mønstret:
   - `<Konstruktion>Spec`-dataclass med valideret input.
   - `generate_<konstruktion>(spec) -> Pattern`.
   - Sæt `pattern.construction`, `pattern.difficulty`,
     `pattern.inputs[...]`.
   - Brug `RowValidator` per række hvor det giver mening.
   - Kald `pattern.validate_continuity()` til sidst hvis
     sektionerne deler maskecount.

4. **CLI-subcommand.** Tilføj subparser i
   `skills/<skill>/scripts/generate.py` med danske aliaser. Test:
   `python3 scripts/generate.py --format md <kommando> [flags]` skal
   producere validerede tekstrækker, ikke tracebacks.

5. **Tests.** Mindst 6-10 tests pr. konstruktion: stitch-balance,
   geometriske mål rammer target, edge cases, fejl-paths
   (`raises ValueError`). Læg dem i `skills/<skill>/tests/`.

6. **Translation-keys.** Tilføj `construction.<navn>` og
   `fig.<navn>` i `lib/visualisering/lang/translations.py` på både
   `da` og `en`, så cover-undertitlen ikke viser den rå nøgle.

7. **Difficulty-rating.** Sæt `pattern.difficulty` til en af:
   `beginner`, `easy`, `intermediate`, `advanced`. Begrund i kommentar.

8. **CHANGELOG og hint.** Tilføj en bullet under `## [Unreleased]` i
   `CHANGELOG.md` med konstruktionens navn og hvilken iteration den
   hører til. Når en ny version frigives, flyttes bullet'en op.

9. **Eksempel.** Hvis konstruktionen er signifikant: tilføj den til
   `scripts/build_examples.py` så den dukker op på Pages-sitet.

## Coding-style

- **Python 3.10+, ingen pip-deps.** Stdlib only i `lib/`, `knitlib/` og
  `croclib/`. Hvis du vil bruge en pakke (numpy, jinja2 etc.), åbn et
  issue først.
- **PEP 8.** Hvor du er i tvivl, vinder læsbarhed.
- **Type-hints på offentlige funktioner.** Interne helpers behøver det
  ikke nødvendigvis, men hvis det krydser et modulskel skal det være
  typed.
- **Engelsk i kode, dansk i kunde-vendt output.** Variablen hedder
  `bust_cm`, ikke `brystmaal_cm`. Strings vendt mod brugeren skrives
  på dansk; engelsk ligger i `lang/en` og fås via `--lang en`.
- **Docstrings i imperative form.** En sætning der siger hvad funktionen
  gør, ikke hvad den "vil gøre".

## Sådan test-strikker eller test-hækler du

Det er den vigtigste form for bidrag. Generatoren fanger alt der
balancerer matematisk — den fanger ikke om en opskrift er behagelig at
strikke, om passformen er forkert, eller om instruktionerne er klare.

1. Generér opskriften med dine egne mål og garn:
   ```bash
   python3 skills/strikning/scripts/generate.py --format html \
     --out min-hue.html --garn "Drops Air" --pinde "4 mm" \
     hue --head 56 --sts 22 --rows 30
   ```
2. Strik / hækl den. Notér løbende hvor du tvivlede, hvor du gættede,
   og hvor noget ikke gik op.
3. Mål det færdige stykke. Sammenlign med spec.
4. Åbn et issue med titel `[test-strik] <konstruktion>` eller
   `[test-hækl] <konstruktion>`. Inkluder:
   - De CLI-flag du brugte (komplet kommando).
   - Faktisk gauge før og efter blokning.
   - Mål før / efter (cm, ikke "ca. en størrelse M").
   - Hvor i opskriften du stødte på noget uklart.
   - Helst et billede af det færdige stykke.

Afvigelser > 2 cm fra spec er issues vi vil rette. Mindre afvigelser kan
være OK, men vi vil stadig vide om dem så vi kan justere fit-warnings.

## Pull request-flow

1. Åbn et issue og beskriv hvad du gerne vil tilføje. Vent på respons
   før du starter — så undgår vi dobbeltarbejde med en parallel agent.
2. Fork repo'et, lav din ændring på en branch.
3. Kør de relevante test-suites. Alle skal være grønne.
4. Hvis du tilføjer en konstruktion: tilføj edge cases til
   `tests/edge_cases.sh` så CLI'en bliver røget igennem.
5. Send pull request. Beskriv hvad ændringen gør og *hvorfor*.
   Reference research-rapporten i `PLAN-research/` hvis der er en.

## Code of conduct

Vær venlig. Det er strikning og hækling. Vi forsøger ikke at kurere
kræft — vi forsøger at gøre opskrifter mere troværdige.
