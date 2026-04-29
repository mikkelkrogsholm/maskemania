# Bidrag til strikkeopskrift

Tak fordi du vil hjælpe! Dette projekt lever af, at folk tilføjer
konstruktioner, finder fejl i opskrifter de selv har strikket, og forbedrer
det danske strikkesprog.

## Sådan kommer du i gang

```bash
git clone https://github.com/<dit-fork>/maskemania.git
cd maskemania/skills/strikning
python3 -m unittest tests.test_knitlib   # 29 tests skal passere
bash tests/edge_cases.sh                  # smoke test
```

Du skal kun bruge Python 3.10+. Ingen pip-pakker.

## Hvad mangler vi mest

Listen er prioriteret — top er det folk efterspørger oftest.

### Nye konstruktioner
- **Bottom-up sweater** (klassisk, ikke top-down). Mange foretrækker det,
  især til mønstrede stykker.
- **Sokker** (top-down med hæl). Standardstrukturen er velkendt; matematikken
  er overskuelig.
- **Top-down halv-pi sjal**. Elizabeth Zimmermanns klassiker.
- **Mitten / vanter**.
- **Strømper** i mønster.

### Tekniske udvidelser
- **Compound raglan**: forskellig udtagningsrate for krop vs ærme. Vigtigt
  for L+ størrelser hvor vi i dag ikke kan styre overarms-bredden uafhængigt.
- **Korte rækker over bagstykket** med faktisk række-for-række matematik
  (i dag beskrives det kun som et trin).
- **Bryst-darts** for store byster.
- **Mønsterrapporter** der spænder over flere sektioner (lace, snoninger).

### Udseende og ergonomi
- **Engelsk output**. Matematikken er sprog-agnostisk; kun
  `templates/`, `components/` og forkortelses-tabellen skal oversættes.
- **Direkte PDF-generering** via Chrome headless: `--pdf out.pdf` flag.
- **Live preview-server** der watcher CSS/components og reloader i browser.
- **Mønstret skematik**: vis stitch-pattern repeats inde i body-shape.
- **Garn-database**: foreslå pinde/fasthed for kendte garner.

### Opskrifts-test
- **Strik en testversion** af en genereret opskrift og rapporter afvigelser.
  Det er den vigtigste form for bidrag — ingen LLM kan erstatte at en
  rigtig strikker tester opskriften med pinde og garn.

## Coding-style

- **Pure Python uden afhængigheder** i `knitlib/`. Hvis du vil bruge en
  pakke (numpy, jinja2 etc.), åbn et issue først så vi kan diskutere.
- **Maskeantal må aldrig digtes**. Al matematik gennem `bookkeeping.RowValidator`
  eller validér på sektionsniveau via `Pattern.validate_continuity()`.
- **Tests først eller samtidig** med ny funktionalitet. Fit-warnings og
  edge cases hører hjemme i `tests/test_knitlib.py`.
- **Dansk i output, engelsk i kode**. Variablen hedder `bust_cm`, ikke
  `brystmaal_cm`. Strings vendt mod brugeren skrives på dansk.

## Bidragsproces

1. Åbn et issue og beskriv hvad du gerne vil tilføje. Vent på respons før
   du laver større ændringer — så undgår vi dobbeltarbejde.
2. Fork repo'et, lav din ændring på en branch.
3. Kør tests: `python3 -m unittest tests.test_knitlib`. Alle skal passere.
4. Hvis du tilføjer en ny konstruktion: tilføj edge cases til
   `tests/edge_cases.sh`.
5. Send pull request. Beskriv hvad ændringen gør og evt. *hvorfor*.

## Test af opskriften

Hvis du strikker en opskrift fra dette værktøj og finder en fejl, så åbn
et issue med:

- Hvilke input du brugte (gauge, mål, ease, konstruktion).
- Hvor i opskriften noget blev forkert (sektion, omgang).
- Hvad du forventede vs hvad der skete.
- Helst et billede af det færdige stykke + (hvis muligt) den fulde
  genererede markdown/HTML.

Det er guld værd. Maskevalideringen fanger alt der balancerer matematisk,
men ikke alt der balancerer matematisk er behageligt at strikke eller
passende ift. fit.

## Dansk strikkesprog

Forkortelses-konventionen i `reference/forkortelser_da.md` er Önling /
strikker.dk-stilen. Hvis du har en stærk præference for et andet system
(Sandnes, Filcolana, PetiteKnit), så åbn et issue — vi kan måske gøre det
til en flag.

## Code of conduct

Vær venlig. Det er strikning. Vi forsøger ikke at kurere kræft.
