# Fase 1 Agent B — Hækling: fundamentale konstruktioner

Research-rapport til `croclib`-design (Fase 2). Fokus: konkret matematik
en programmør kan kode op, plus stitch-dictionary med
(consumes, produces)-bookkeeping.

Konvention i hele rapporten: **amerikanske termer (US)**. Danske og britiske
oversættelser opført separat.

---

## 1. Stitch-dictionary

Bookkeeping-modellen fra strik er `(consumes_n, produces_n)` pr. stitch:
hvor mange masker fra forrige række/omg "spises", og hvor mange nye masker
står tilbage på højre side af arbejdet.

For hækling skal vi være præcise om hvad "consumes" betyder. I hækling:

- En stitch indsættes typisk i én eksisterende stitch (eller chain-space).
- Der er aldrig "loops on needle" — kroghen holder kun arbejdsløkken.
- Den nye stitch tæller som 1 stitch i den næste række/omg, medmindre
  den er en chain (lm) der er trailing/turning, eller en sl st (km)
  der ikke producerer noget tællende.

| US-navn | US-fork. | UK-fork. | Dansk navn | Dansk fork. | consumes | produces | yarn-overs | noter |
|---|---|---|---|---|---|---|---|---|
| chain | ch | ch | luftmaske | lm | 0 | 1* | 0 | *tæller normalt ikke i wraps; turning-chains tæller variabelt |
| slip stitch | sl st | ss | kædemaske | km | 1 | 0 | 0 | bruges til at forbinde / forflytte; tæller ikke |
| single crochet | sc | dc | fastmaske | fm | 1 | 1 | 0 | grundmaske amigurumi |
| half double crochet | hdc | htr | halvstangmaske | hstm | 1 | 1 | 1 | mellemhøj |
| double crochet | dc | tr | stangmaske | stm | 1 | 1 | 1 | grundmaske granny/filet |
| treble crochet | tr | dtr | dobbeltstangmaske | dst (dbstm) | 1 | 1 | 2 | høj stitch |
| double treble | dtr | trtr | tredobbeltstangmaske | tdst | 1 | 1 | 3 | sjælden |
| sc increase (sc-inc) | inc / sc2 | — | udtagning | udt | 1 | 2 | 0 | 2 sc i samme stitch |
| sc decrease | sc2tog | dc2tog | indtagning (2 fm sm) | indt / 2 fm sm | 2 | 1 | 0 | invisible decrease er en variant |
| dc decrease | dc2tog | tr2tog | 2 stm sm | 2 stm sm | 2 | 1 | 1 | |
| magic ring (start) | MR / mr | — | magisk ring | mr / mc | 0 | n* | 0 | *producerer N=6 typisk |
| chain space | ch-sp | ch-sp | luftmaskebue | lm-bue | 0 | (skip) | 0 | space mellem stitches; consumes håndteres som "skip" |

### Vigtige twists

1. **Turning chain (t-ch)**: row-baseret hækling starter hver række med
   en t-ch hvis højde matcher næste stitch: sc=1, hdc=2, dc=3, tr=4 ch.
   Tæller nogle gange som første stitch (især dc/tr), nogle gange ikke
   (sc). Modellér eksplicit.
2. **Magic ring**: produces N uden at consume — *initialiserings-stitch*.
   Som `cast_on` i strik.
3. **Working into chain-space vs stitch**: granny squares arbejder
   *mellem* stitches via ch-sp, ikke i en stitch.
4. **BLO/FLO**: tællingen er uændret, kun tekstur — flag som modifier.

### Bookkeeping-implikation: passer (consumes, produces) direkte ind?

**Næsten, men med tre udvidelser.** Hækling kræver:

- **`creates_chain_space`**: dc/tr efterfulgt af lm-bue producerer både
  en stitch og et "rum" som næste round kan hække ind i. Strik har ikke
  dette koncept.
- **`works_into`**: en enum {stitch, chain_space, magic_ring,
  starting_chain, between_stitches}. Flere hæklemasker arbejder ind i
  forskellige targets.
- **`turning_chain` / `closing_round`**: Round-baseret hækling skal
  kende sluttet (sl st til top af første stitch) eller spiralform
  (amigurumi: ingen join, bare fortsæt).

Forslag til Stitch-klassen:

```python
@dataclass
class CrochetStitch:
    name: str
    consumes: int           # masker spist
    produces: int           # masker tilbage på row/round
    yarn_overs: int         # 0=sc, 1=hdc/dc, 2=tr...
    works_into: Literal["stitch", "ch_sp", "mr", "starting_ch"]
    counts_as_stitch: bool = True  # False for ch, sl st
    creates_ch_sp: int = 0  # antal lm efter stitch der tæller som rum
```

---

## 2. Amigurumi (rounds-based, magic ring + sc-increases)

### Grundprincippet — flad cirkel

Reglen er: **øg med samme antal som start-stitches pr. omg**. Med
6-sc magic ring: 6, 12, 18, 24, 30, 36, ... I omg N er stitch-count
`6*N`.

Matematisk baggrund: omkredsen af en cirkel er `2πr ≈ 6.283·r`.
Hver omg svarer til at radius øges med 1 stitch-højde, altså skal
omkredsen øges med ~6.28 stitches. Vi runder til 6.

**Konsekvens**: Resultatet er teknisk en hexagon hvis alle increases
sker samme sted. Løsningen er at *staggere* increases (forskyd 1
position pr. omg) — så bliver formen rund.

### Increase-skema for omg N

```
Omg 1: MR → 6 sc i ringen           → 6 stitches
Omg 2: 6 × inc                       → 12
Omg 3: 6 × (sc, inc)                 → 18
Omg 4: 6 × (2 sc, inc)               → 24
Omg N (N>=2): 6 × ((N-2) sc, inc)    → 6N
```

Generelt: omg N har `(N-1)` reps mellem hver increase, og 6 increases
totalt. Stagger-offset: `offset = (N-1) mod (N-1)` — eller bare gem
offset-tæller pr. omg.

### Sphere-formler (kugle)

En kugle med max-omkreds `C_max` (i stitches, dvs. `6N_max`) har:

- **Increase-fase**: omg 1 til omg N_max. Stitches: 6, 12, 18, ..., 6N_max.
- **Equator-rounds**: K omg uden inc/dec, alle med 6N_max stitches.
  K kan være 0 for en præcis kugle, eller >0 for "kugle med jævn midte"
  (oval). Standard amigurumi-tilgang: K = N_max ÷ 3 til N_max÷2 for
  visuelt rund kugle, eller K=N_max for stuffer-friendly form.
- **Decrease-fase**: spejling — 6N_max, 6(N_max-1), ..., 12, 6.
  Slut med "draw-string close": træk garnet gennem de sidste 6 fm.

For en simpel matematisk kugle (ren sfærisk):
- **Antal increase rounds = antal decrease rounds = N_max**
- **K (mellem-omg) = 0**
- **Total rounds = 2·N_max - 1** (sidste increase-omg + spejlet decrease,
  men midter-omg deles ikke; deler man midter, er det 2·N_max)

Diameter: ca. `2·N_max` stitches diameter når man tæller flad-cirkel.
Faktisk fysisk diameter afhænger af gauge: `d_cm = (6·N_max / π) /
stitches_per_cm`. Eksempel: gauge 4 sc/cm, N_max=8 → omkreds 48 sc =
12 cm → diameter ~3.8 cm.

### Cylinder-formler

```
Increase-fase:  omg 1..N → 6, 12, ..., 6N      (flad bund)
Tube-fase:      H omg af 6N stitches           (cylinderhøjde)
[valgfri lukning]
Decrease-fase:  6N → 6(N-1) → ... → 6           (rund top)
```

Cylinderdiameter ~ flad-cirkel-diameter ovenfor. Højden:
`h_cm = H · row_gauge_cm`. Typisk amigurumi-gauge: ~5 rows/cm i sc.

### Taper / kegle / oval

Lineær taper: i tube-fasen, decrement med konstant antal pr. omg
(f.eks. 1 sc dec hver 2. omg) — giver kegle. Stitches efter k omg
= `start_stitches - k·(dec_rate)`.

Hovedform i amigurumi (figur): increase op til hovedomkreds, K omg
lige, derefter aggressivt decrement (4-6 dec pr. omg) → "cocoon"-form.

### Standard-skabelon (krop af amigurumi-figur)

```
HEAD:   inc(N_h) → straight(K_h) → dec(N_h)         # kugle
BODY:   inc(N_b) → straight(K_b) → dec(N_b)         # ovoid
ARMS:   inc(N_a=2..3) → straight(K_a) → close       # små rør
LEGS:   inc(N_l=3..4) → straight(K_l) → close
TAIL/EARS: ad hoc minor shapes
```

---

## 3. Granny square

### Klassisk (åben)

3-dc-clusters separeret af ch-1 (sider) og ch-2 (corners).

**Round 1** (i magic ring eller ch-4-loop):
```
[3 dc, ch 2] × 4   → 12 dc, 4 corner-spaces
total stitch count: 12
```

**Round 2** (i hver corner):
```
I hver corner-space: [3 dc, ch 2, 3 dc]
Mellem corners: ch 1
→ 24 dc, 4 corner ch-2-sp, 4 side ch-1-sp
```

**Round N (N≥3)**:
```
Pr. side: (N-2) clusters af 3 dc, hver separeret af ch 1
Pr. corner: [3 dc, ch 2, 3 dc]
→ stitches per side: (N-1) clusters × 3 dc = 3(N-1) dc per side
→ total dc round N = 4 × 3(N-1) = 12(N-1)
   PLUS 4 corner ch-2-sp og 4(N-2) side ch-1-sp pr. round.
```

Sidekanter-længde i stitches: omg N har `(N-1)` clusters pr. side.

### Modern solid (4-corner solid dc-square)

Dense version uden side-ch-1: kun corner ch-2 (eller corner ch-1 for
ekstra tæt). Stitch-count:

**Round 1**: 12 dc i magic ring, 4 corners markeret med ch-1 eller
arbejdet med (2 dc, ch 2, 2 dc) i ringen.

**Round N (N≥2)**: pr. side = `2N+1` dc; corners: [2 dc, ch 2, 2 dc].
- Stitches pr. side: `2N+1` for N≥1 (tjek lokal definition — kilder
  varierer ±1 pga. om corner-dc tælles med i sidetæller eller ej).

**Generel regel**: hver round øger sidelængden med 4 dc (én ny
cluster + én ny "splitting" stitch per corner-side). Corner-vinklen
holdes af `[N dc, ch K, N dc]`-format. Standard: N=2, K=2 (modern
solid); N=3, K=2 (klassisk granny).

### Bookkeeping i granny

Worker-targets veksler: round 1 arbejdes ind i `mr` eller `starting_ch_loop`;
round N≥2 arbejdes overvejende ind i `ch_sp` (for corners) plus ind i
`stitch` (for sider, hvis solid). Det betyder croclib skal have eksplicit
target-tracking pr. stitch i et grid.

---

## 4. Filet hækling

### Grundkonstruktion

Filet er pixel-grafik på en mesh af dc + ch.

**Mesh-cell**: 1 dc + 2 ch (åben) ELLER 3 dc (fyldt).
**Block** efter første cell: hver yderligere åben cell = 2 ch + 1 dc;
hver yderligere fyldt cell = 2 dc (delt dc med foregående cell).

### Stitch-count formel

For et W × H grid (kolonner × rækker):

```
Stitches pr. række = 3·W + 1
                     (W cells × 3 stitches + 1 ekstra dc til at lukke
                     den sidste cell — hver cell deler én dc med næste,
                     undtagen den sidste)
```

Eksempel: 10 × 10 grid → hver række = 31 stitches.

### Læseretning og charts

Charts læses bottom-up. Odd rows: højre→venstre. Even rows: venstre→højre.
Hver celle på charten er enten "tom" (åben mesh) eller "fyldt" (solid
block). Pixel-art-modellen: oplagt til bytemap-input.

### Beginning og turning chains

- Foundation chain: `3·W + 2` ch (afhængigt af variant).
- Turning chain pr. række: 3 ch hvis første cell er åben (= dc + 2 ch),
  ellers 5 ch (= dc + 2 ch + dc-højde-skip).

### Increasing/decreasing til ikke-rektangulære former

Filet kan formes (hjerte-shapes etc.) ved at tilføje/skære cells i
kanten. Hver tilføjet åben cell = 5 ch i begyndelsen af række; hver
afkortet = sl st over de cells der droppes.

---

## 5. Tunisian crochet

### Konstruktion

Hver "row" består af to passes:
1. **Forward pass (FP)**: fra højre mod venstre, plukker loops op på
   en lang krog. Endelig loop-count = stitch-width + 1 (slipknot).
2. **Return pass (RP)**: fra venstre mod højre, ch 1, dernæst gentagent
   (yo, pull through 2 loops) indtil 1 loop tilbage.

Arbejdet vendes aldrig — RS er altid ud.

### Tunisian Simple Stitch (TSS) — grundmaske

FP: skip first vertical bar; for hver vertical bar: insert hook under
front vertical bar, yo, pull up loop. Sidste maske: arbejd gennem
begge lag for stabil kant.

### Stitch-count

For width W:
- Foundation row: ch W → FP plukker W loops op (inkl. slip knot).
- RP reducerer til 1 loop tilbage.
- Hver efterfølgende row: FP samler W loops, RP reducerer til 1.
- Stitch-count er konstant W gennem hele tøjstykket (medmindre man
  inkrementerer/decrementerer i FP).

### Bookkeeping-implikation

Tunisian bryder den simple `(consumes, produces)`-pattern fordi en
"row" er to passes. Forslag:

- Modellér en `TunisianRow` som en bundle af `(forward_stitches,
  return_stitches)` med invariant: `len(forward) == width`,
  `return_pass` er deterministisk afledt.
- Eller: behandl FP og RP som to separate "rows" der altid kommer i par.

Variants (TKS = Tunisian Knit Stitch, TPS = Tunisian Purl Stitch) ændrer
kun *hvordan* loops plukkes op, ikke tællingen.

---

## 6. Freeform

Freeform (scrumbling) har **ingen patternstruktur** — ad hoc stitches,
farver, garn, ofte syet sammen af "scrumbles". Walters & Cosh navngav
teknikken.

**Anbefaling: skip i Fase 2.** Ingen formler, ingen syntax, ingen
deterministisk opskrift. Eventuelt en minimal "scrumble template
helper" senere (foreslå stitch-vokabular + farver). Lav prioritet.

---

## 7. Danske kilder

Bekræftede:

- **rito.dk** har en kortliste over fm/lm/km/hstm/stm/sm.
- **haekleskolen.dk/ordbog/** har en bredere ordbog med eksplicit
  US/UK-mapping og inkluderer dst (dobbeltstangmaske).
- **Hobbii** og **Drops/Garnstudio** er standardkilder for danske
  hækleopskrifter; de bruger samme forkortelser (fm, stm, lm, km, hstm).
- **hæklemester.dk** og **Hæklestjernen**: eksisterer (jeg har set dem
  refereret), men jeg fetched dem ikke for konkret terminologi-bekræftelse.

Standard danske forkortelser bekræftet:

```
lm    = luftmaske          = chain (ch)
km    = kædemaske           = slip stitch (sl st)
fm    = fastmaske           = single crochet (sc)
hstm  = halvstangmaske      = half double crochet (hdc)
stm   = stangmaske          = double crochet (dc)
dst   = dobbeltstangmaske   = treble crochet (tr)
sm    = sammen              = together (suffix til indtagning)
indt  = indtagning          = decrease
udt   = udtagning           = increase
omg   = omgang              = round
rk    = række               = row
```

---

## 8. Bookkeeping-konklusion for croclib

**Stitch-modellen skal udvides** ift. strik-modellen med:

1. **`works_into`**: enum med `STITCH | CH_SP | MAGIC_RING | STARTING_CH`.
2. **`creates_ch_sp: int`**: antal trailing chains der danner et brugbart
   chain-space til næste round.
3. **`yarn_overs: int`**: 0/1/2/3 — bestemmer stitch-højde (relevant for
   row_height i schematic-rendering).
4. **`turning_chain_height: int`**: Antal ch der svarer til denne stitch
   ved row-skift.

**Specielle stitch-typer** der ikke passer ind i standard-tabellen:

- **MagicRing(n)**: `consumes=0, produces=n, works_into=NONE`.
  Initialiserings-stitch. Fungerer som `cast_on(n)` i strik.
- **CornerCluster(n_dc, ch_k)**: kompositstitch der både producerer
  `2*n_dc` stitches OG en chain-space af længde k.
- **TurnRound / SlipStitchJoin**: round-afslutning. consumes=1
  (slip stitch ind i top af første stitch), produces=0.

**Pattern-DSL bør have**:

- `repeat(stitches, n)`: gentagelse → bruges overalt.
- `in_corner(stitch_or_cluster)`: arbejder i corner ch-sp.
- `between(stitch_or_cluster, target=ch_sp)`: arbejder mellem stitches.
- `staggered_increase(round_n)`: amigurumi-stagger logik.

**Tunisian** bryder modellen mest. Anbefaling: separat sub-modul
`croclib.tunisian` med `TunisianRow`-klasse i stedet for at presse
forward+return ind i den fælles Stitch-model.

---

## Kilder

- shelleyhusbandcrochet.com (UK/US conversion + circle formula)
- supergurumi.com, pocketyarnlings.com, buddyrumi.com (amigurumi shapes)
- raffamusadesigns.com (hexagon→circle staggering)
- crochet365knittoo.com, sarahmaker.com, mariasbluecrayon.com (granny)
- yarnspirations.com, crochet.com, crochetistheway.blogspot.com (filet)
- moralefiber.blog, crochet.com (Tunisian)
- furlscrochet.com, crochetverse.com (freeform/scrumbling)
- rito.dk, haekleskolen.dk/ordbog/ (danske forkortelser)
- craftyarncouncil.com (US standard abbreviations)
