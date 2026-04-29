# Fase 1 — Agent A: Avancerede strik-konstruktioner

Variabel-navne: `gauge_st` = masker/10 cm, `gauge_row` = pinde/10 cm,
`bust_cm` = brystmål. Formlerne er beskrevet så de kan oversættes 1:1
til Python.

---

## 1. Bottom-up sweater (klassisk + modificeret)

### Variabler der skal opspørges
- `bust_cm`, `ease_cm` (positivt = løs pasform)
- `body_length_cm`, `sleeve_length_cm`
- `wrist_cm`, `upper_arm_cm`
- `gauge_st`, `gauge_row`

### Klassisk EPS (Elizabeth Zimmermann)

EPS = Elizabeth's Percentage System. `K` er "key number":

```
K = round( (bust_cm + ease_cm) / 10 * gauge_st )   # body sts at chest
```

Procenter (yoke-style sweater):

| Element              | % af K       | Note |
|----------------------|--------------|------|
| Body cast-on         | 90 %         | lidt smallere ved hofte; eller 100 % |
| Sleeve cast-on (cuff)| 20 %         | 50/250 i Zimmermanns eksempel |
| Sleeve top (upper arm)| 35–40 %     | 88–100/250 |
| Underarm hold        | 8 %          | 4 steder: 8 % af K aftages som "underarm" |
| Neck                 | 40 %         | ca. 100/250 |
| Yoke depth           | (bust_cm+ease)/4 | dybde fra underarmsskel til neck |

Kilde: KnitPicks tutorial om EPS, suppleret af "Knitter's Almanac".

### Konstruktionsforløb

1. **Krop**: cast on `body_sts = round(K * 0.9)`. Strik til
   `body_length_cm - yoke_depth_cm`.
2. **Ærme**: cast on `cuff_sts = round(K * 0.20)`. Øg jævnt til
   `arm_top_sts = round(K * 0.35)` (magic formula nedenfor).
3. **Underarm**: aflæg `under_sts = round(K * 0.08)` på begge sider af
   krop og hvert ærme. Skal være ens på krop og ærme (graft).
4. **Join til yoke**:
   ```
   yoke_sts = body_sts - 2*under_sts + 2*(arm_top_sts - 2*under_sts)
   ```
5. **Yoke-shaping**: raglan (4 markører, 8 dec/2. omg) eller circular
   yoke (3 dec-runder, se §5).

### Modificeret moderne (PetiteKnit/Sandnes)

Forskelle fra ren EPS: boksigere silhuet (`body_sts ≈ K * 1.0`),
dybere yoke (`yoke_depth ≈ bust_cm/4 + 2 cm`), underarm hold 5–6 %
(tight) eller 10 % (slouchy).

### Magic formula (jævnt fordelte indtagninger)

Givet: vil øge `inc` masker over `n` masker (eller pinde).

```
base_interval = n // inc
remainder     = n % inc
# Brug "base_interval+1" remainder gange, "base_interval" (inc-remainder) gange.
```

Eksempel: 8 indtagninger over 40 masker → hver 5. maske, glat løb.
8 over 41 → 1× hver 6. maske + 7× hver 5. maske.

### Gotchas

- **Magic-formula off-by-one**: lad ikke første/sidste maske få ekstra
  shaping — fordel rates inde i intervallet.
- **Underarm-graft mismatch**: `under_sts_body == under_sts_sleeve`.
  Afrund samme vej.
- **For lille ærme**: tjek `arm_top - 2*under ≥ 0` for små størrelser.

### Danske referencer

- Önling Easy Peasy raglan (gratis, top-down): https://www.oenling.dk
- Tryllemasken Islandsk raglan (gratis, bottom-up):
  https://tryllemasken.dk/vare/islandsk-raglansweater/
- DROPS Design gratis raglan: https://www.garnstudio.com
- PetiteKnit Sunday Sweater (købes; top-down yoke + short rows).

---

## 2. Top-down half-pi shawl (Elizabeth Zimmermann)

### Princip

Cirkelens omkreds = `2π * r`. Når radius fordobles, fordobles antal
masker. Pi-sjalet udnytter dette ved at fordoble både masker OG antal
"plain" pinde efter hver dobblings-pind.

### Half-pi (halvcirkel) — formel-progression (verificeret)

Cast-on garter tab → 3 m → pickup giver typisk 8 m (4 + center 0 + 4).

| Pind     | Antal   | Indt-pind?  | Center-masker |
|----------|---------|-------------|---------------|
| 1        |  1      | nej         | 8 (0 center)  |
| 2        |  1      | **ja**      | 11 (3+5+3)    |
| 3–5      |  3      | nej         | 11            |
| 6        |  1      | **ja**      | 17            |
| 7–12     |  6      | nej         | 17            |
| 13       |  1      | **ja**      | 29            |
| 14–25    | 12      | nej         | 29            |
| 26       |  1      | **ja**      | 53            |
| 27–50    | 24      | nej         | 53            |
| 51       |  1      | **ja**      | 101           |
| 52–99    | 48      | nej         | 101           |
| 100      |  1      | **ja**      | 197           |

Mønster: indtagningspinde ligger ved `n=2, 6, 12, 24, 48, 96, 192…`
(altid det dobbelte af forrige). På indtagningspinden: `(yo, k1)` over
center-stitches → fordobler antallet.

### Generel formel

```
center_after_double(k) = 2 * center_before(k) + 1   # +1 fra YO mod kant
inc_row(n)             = 2 * inc_row(n-1)           # 2,6,12,24,48,...
```
hvor `center_before` afhænger af edge-stitches (typisk 4 hver side i
garter-stitch, indgår ikke i fordobling).

### Full circle-pi (radius/360°)

Samme princip men cast-on i magic ring 9 m og fordobl ved hver
indtagningspind: 9 → 18 → 36 → 72 → 144 → 288 → 576. Plain rounds
mellem fordoblinger: 3 → 6 → 12 → 24 → 48.

### Variabler at opspørge

- Endeligt diameter (radius i cm) eller "antal indt-cykler" (typisk 5–7).
- `gauge_st` (af lace efter blocking ≠ stockinette gauge).

### Gotchas

- **Edge-stitches (garter band) skal IKKE fordobles**. Vi double kun
  center-masker. Ellers vokser kanten skævt.
- **Lace-rapport skal passe ind i center_after_double**. Hvis ens lace
  har rapport 12 og man står på 53, går regnestykket ikke op. Løsning:
  fudge rounds (rul 1–2 plain-rounds frem/tilbage) — Andrea Rangel
  bekræfter at half-pi er meget tilgivende.
- **Block-faktor**: lace blocker typisk 30–40 % større end strikket
  diameter. Mål mod blocked diameter, ikke off-needle.

### Danske referencer

Pi-sjalet er ikke et populært dansk format — primært engelsk/amerikansk
tradition (Zimmermann). DROPS har dog flere half-circle sjaler:
https://www.garnstudio.com (søg "shawl half").

---

## 3. Strømper top-down med hæl (heel flap + gusset)

### Variabler

- `foot_circ_cm` (om foden, bredeste sted), `foot_length_cm`
- `gauge_st`, `gauge_row`
- Negativ ease: 10 % (sok skal sidde stramt).

### Sektioner og math

```
total_sts = round(foot_circ_cm * 0.9 / 10 * gauge_st)
total_sts = round_to_multiple(total_sts, 4)   # delelig med 4
```

#### Skaft (cuff + leg)
- Cast-on `total_sts`, rib 2×2 i 4–6 cm, glat til ankel.

#### Hælklap (heel flap)
- Halvdelen af masker: `flap_sts = total_sts / 2`.
- Antal pinde: `flap_rows = flap_sts` (for kvadratisk klap).
  Slip-stitch-pattern: heel stitch.
- Standard: hvis `flap_sts` er ulige → strik `flap_sts - 1` pinde.

#### Heel turn (klassisk)
Variabler:
- `F = flap_sts`
- `h ≈ floor(0.10 * total_sts)` (centrale "bottom" sts før første dec)

Setup: strik halvvejs + halv-h + 1 → ssk → vend → p halv-h + 1 → p2tog
→ vend… Alle gap-sts forbruges.

Resterende masker efter heel turn:

```
if (F - h) / 2 is even:
    H = h + (F - h) / 2
else:
    H = h + ((F - h) - 2) / 2 + 2
```

Kilde: Sara Morris ("Mathematics of a Traditional Heel").

#### Gusset (kile)
- **Pickup pr. side**: `pick = flap_rows / 2 + 1`. (+1 ekstra for at
  undgå hul ved samling).
- **Sts efter pickup**: `H + 2*pick + (total_sts/2)` (instep urørt).
- **Decreases** hver 2. omgang (k2tog højre side, ssk venstre) indtil
  back to `total_sts`.

#### Fod
- Strik glat indtil samlet fodlængde = `foot_length_cm - toe_length_cm`.
- `toe_length_cm ≈ foot_circ_cm / 4` (rule-of-thumb).

#### Tå (rounded toe)
- Decrease 4 sts hver 2. omg, derefter 4 sts hver omg, til ca. 16–20 sts.
- Kitchener graft.

### Gotchas

- **Heel turn off-by-one** (bryderiet for nye designere): paritets-
  formlen ovenfor afhænger af om `(F-h)/2` er lige. Skal kodes
  eksplicit, ikke "kør indtil maske er væk".
- **Pickup ulige**: hvis flap_rows er ulige → afrund pickup op for én
  side, ned for den anden, og indrøm en ekstra ssk i første gusset-omg.
- **Total skal være delelig med 4** (eller 8 for 2×2 rib symmetri).

### Danske referencer

- DROPS Design: gratis hæl-tutorial-video og masser af sokke-opskrifter
  med kilehæl. https://www.garnstudio.com/video.php?id=307&lang=dk
- DROPS sokker dame: https://www.garnstudio.com/search.php?c=women-socks
- Strikkeglad.dk og hobbyhygge.com har danske beregnere.

---

## 4. Vanter (mittens) — top-down med tommelkile

### Variabler
- `hand_circ_cm` (rundt om hånden, ikke tommel), `hand_length_cm`
- `thumb_circ_cm`
- `gauge_st`, `gauge_row`

### Math

```
hand_sts  = round_to_multiple(hand_circ_cm/10 * gauge_st, 4)
thumb_sts = round_to_multiple(thumb_circ_cm/10 * gauge_st, 2)
gusset_max_sts = thumb_sts - 2     # vi tager 2 fra håndfladen
```

### Konstruktion

1. **Cuff**: cast-on `hand_sts`, rib 5–7 cm.
2. **Underhånd til gusset-start**: 2–3 cm glat.
3. **Gusset-start**: placér 2 markører, M1R + 1 + M1L mellem dem
   (3 sts mellem markører).
4. **Gusset-vækst**: hver 3. omgang: M1R, knit til 1 før m, M1L. Gentag
   indtil masker mellem markører = `gusset_max_sts` (typisk 13–17 i
   fingering).
5. **Sæt tommel på hold**: aflæg gusset-masker på waste-yarn, cast-on
   2 nye masker over åbningen. Stsantal nu = `hand_sts`.
6. **Hånd**: strik glat til 2 cm før fingerspids (= 4 cm før dec for
   afrundet top).
7. **Top-decrease**: 4 dec/omg på "rund" toptype, eller flat-top
   sammensyet med Kitchener (8 dec hver 2. omg, 4 hver omg).
8. **Tommel**: pickup `gusset_max_sts + 2` (de to nye fra håndflade) +
   1 i hver hjørne for at undgå hul → strik glat indtil 1 cm før
   tommelspids → dec til ~6 sts → træk garn igennem.

### Variant: bottom-up
Samme math omvendt: cast-on 8 sts magic-loop, øg 4/omg til `hand_sts`,
kile aftager, cuff rib til sidst.

### Gotchas

- **Gusset hul**: hvis ikke man picker op én ekstra i hvert hjørne af
  tommelhullet, får man hul. Skal kodes som `pickup += 2`, dec første
  omg via k2tog over hjørnerne.
- **Højre/venstre vante er IKKE ens** når der er mønster med kile.
  Spejl gusset-position.
- **Round-to-multiple**: rib 2×2 kræver mod 4; rib 1×1 kun mod 2.

### Danske referencer

- Önling: https://oenling.com/collections/gratis-strikkeopskrifter/huer-og-vanter
- Sandnes Garn: gratis vante-opskrifter via Saturnia Garn-shop.
- DROPS Design: et hav af vanter på dansk.

---

## 5. Yoke-sweaters med stranded mønster (Icelandic style)

### Variabler

- `bust_cm`, `ease_cm` → `body_sts = K`
- `gauge_st`, `gauge_row` (stranded-gauge ≠ glat-gauge, vigtigt!)
- Mønster-rapport `R` (typisk 4, 6, 8, 12, 24)
- Mål for halsåbning: `neck_cm` → `neck_sts ≈ K * 0.40`

### Yoke-skelet

3-decrease yoke (klassisk Icelandic, fx Lopapeysa):

```
yoke_start_sts = K - 2*under_sts + 2*(arm_top - 2*under_sts)
                ≈ 1.45 * K       (faustregel for voksen)
yoke_depth_cm  ≈ (bust_cm + ease) / 4
```

Decrease-rounds (Tin Can Knits "Strange Brew" & Zimmermann):

| Decrease # | Position i yoke (% fra underarm) | Faktor |
|------------|----------------------------------|--------|
| Dec 1      | 30 %                             | × 0.75 |
| Dec 2      | 60 %                             | × 0.66–0.75 |
| Dec 3      | 85–90 % (lige før neck-rib)      | rest til neck_sts |

Faktorerne giver typisk:
```
after_dec1 = round(yoke_start_sts * 0.75)
after_dec2 = round(after_dec1     * 0.70)
after_dec3 = neck_sts
```

### Pattern-repeat alignment (kritisk)

Hvert mønster-bånd skal have et maskeantal som er multiplum af `R`.

```
def fit_to_repeat(sts, R):
    return sts - (sts % R)   # dec til nærmeste multiplum
```

Praktisk metode (Tin Can Knits):
1. Beregn ønsket post-dec antal (fx 0.75 × yoke_start).
2. Round til nærmeste multiplum af `R` for det nye bånd.
3. Juster decrease-faktoren bagud så regnestykket går op.

Eksempel: yoke_start = 240, R = 8, dec1 ønsket 0.75 → 180.
180 mod 8 = 4 → juster til 176 (dec 64) eller 184 (dec 56).

Multiplum-trick: design yoke-start som multiplum af 24. 24 er deleligt
med 2,3,4,6,8,12 → matcher næsten alle Icelandic-rapporter.

### Gradering på tværs af størrelser

Hver størrelse: egen `K` (proportional til bust), `yoke_start_sts` =
nærmeste multiplum af `R` (helst også af 24), decrease-faktorer 0.75
/ 0.70 konstante. Med 24-st rapport: `yoke_start = 24 × n`, n = 7–14
for XS–5XL. Hvis rapporten ikke kan passe i en størrelse, "fudge" med
ekstra plain round — kan kodes som warning.

### Gotchas

- **Stranded gauge ≠ stockinette gauge**: spørg eksplicit efter
  stranded-gauge til yoke-beregningen, glat-gauge til ærmer/krop.
- **Neckline for stram**: hvis dec3 lander præcis på `0.40*K` får man
  ofte for stram hals. Pad med +5–10 % og afslut i rib der trækker.
- **Repeat-mismatch i mindste/største størrelse**: hvis rapport er 24
  og K er lille, kan der ikke være 24×n. Workaround: lille størrelse
  bruger kun halvrapport (12), eller pattern bytter motiv.
- **Yoke-depth for kort**: hvis `yoke_depth_cm * gauge_row` < 3
  decrease-zoner + plain-bands → mønster bliver komprimeret. Min
  yoke_depth ≈ 18 cm for voksen.

### Danske referencer

- Tryllemasken: gratis Islandsk raglansweater (top-down).
  https://tryllemasken.dk/vare/islandsk-raglansweater/
- Sandnes Garn "Islender" (klassisk lopi-stil) — sælges via Idestova.
- Hélène Magnússon (Icelandic Knitter): autoritativ, mønstre købes.
- DROPS har snesevis af Icelandic-yoke gratis.

---

## Implementation hints (til Fase 2+)

### Genbruger eksisterende `lib/visualisering`

Disse bruger samme schematic-grammatik som klassisk top-down raglan
(rektangler + målpile + masketal), så de kræver primært nye
*beregnings*-moduler:

- **Bottom-up sweater** — schematic er ren rektangel-kombi (krop +
  ærmer + yoke), samme som top-down raglan i spejling.
- **Vanter** — 2 rektangler (hånd + tommel) + cuff. Kan genbruge
  hue/halstørklæde-baseret SVG.
- **Strømper** — krop + hælklap (rektangel) + tå (trapez). Trapez er
  ny form, men additivt — kan tilføjes som ny SVG-primitiv.

### Kræver nye SVG-skematik-typer

- **Half-pi shawl**: halvcirkel-skematik med inkrementelle radius-
  markeringer ved hver indt-pind. Kræver SVG `<path d="A …">` arc-
  primitive vi sandsynligvis ikke har.
- **Yoke-sweater (Icelandic)**: kegleformet yoke-skematik med
  decrease-rounds markeret som vandrette linjer + colorwork-chart-blok.
  Trapezformet schematic + chart-grid SVG.
- **Sok-konstruktion**: L-formet skematik (skaft 90° til fod). Kræver
  knæk-line eller sammensat figur — kan modelleres som to rektangler
  forbundet ved hælen.

### Beregningsmoduler der kan deles

- `magic_formula(n_changes, n_stitches) -> [(rate, count), ...]`
- `round_to_multiple(x, m, prefer="up"|"down"|"nearest")`
- `eps_percentages(K, style="yoke"|"raglan"|"drop")` — returnerer
  body, sleeve_cuff, sleeve_top, neck, underarm, yoke_depth.
- `repeat_fit(sts, R) -> int` (juster sts til multiplum)
- `pi_shawl_progression(n_doublings, edge=4) -> list[(row, sts)]`
- `heel_turn(F, h) -> H` (paritetshåndtering)

### Test-strategi

1. Verificér kendte eksempler (Zimmermann 9-st pi: 9 → 18 → 36 → …).
2. Invarianter: yoke-cast-on = `body - 2u + 2*(arm_top - 2u)`;
   `underarm_body == underarm_sleeve`.
3. Edge-cases: meget små størrelser hvor `arm_top < 2*under`.

---

## Kilder

- KnitPicks tutorial: https://tutorials.knitpicks.com/percentage-system/
- Ysolda magic formula: https://ysolda.com/blogs/journal/a-magic-formula-for-evenly-distributing-shaping
- Tin Can Knits Strange Brew: https://blog.tincanknits.com/2018/11/09/how-to-design-a-strange-brew-yoke/
- Tin Can Knits bottom-up: https://blog.tincanknits.com/2017/03/28/lets-knit-a-bottom-up-sweater/
- Sara Morris heel-math: https://fyberduck.wordpress.com/writing/tutorials/mathematics-of-a-traditional-heel/
- Andrea Rangel half-pi: https://www.andrearangel.com/andrearangelblog/half-pi-shawls
- The Snugglery half-pi: https://thesnugglery.net/how-to-knit-the-half-pi-shawl/
- Knitgrammer top-down mittens: https://www.knitgrammer.com/blog/basic-thumb-gusset-pattern-for-top-down-mittens/
- Interweave pi shawl: https://www.interweave.com/article/knitting/demystifying-the-pi-shawl-create-your-own-one-of-a-kind-circular-shawl/
- Interweave yoke shaping: https://www.interweave.com/article/knitting/circular-yoke-shaping/
- Önling gratis: https://www.oenling.dk/collections/gratis-strikkeopskrifter
- DROPS Design: https://www.garnstudio.com/
- Tryllemasken: https://tryllemasken.dk/vare/islandsk-raglansweater/
- PetiteKnit Sunday: https://www.petiteknit.com/en/products/sunday-sweater
