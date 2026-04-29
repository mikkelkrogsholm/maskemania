"""Danish prose fragment library, keyed by construction and slot.

Each entry maps a "slot" (intro / size / yarn / difficulty / closing) to
a list of variant sentence templates. ``{...}`` placeholders are
replaced via ``str.format(**facts)``. The RNG picks one template from
each slot, in order.

The "_default" group is a generic fallback used for unknown constructions.
"""

from __future__ import annotations


FRAGMENTS_DA: dict[str, dict[str, list[str]]] = {
    "_default": {
        "intro": [
            "Denne {construction_label} er beregnet ud fra dine egne mål "
            "og din egen strikkefasthed — så den passer, første gang.",
            "{construction_label}: en konstruktion bygget op fra "
            "{stitch_count_total} masker, beregnet på din strikkefasthed.",
            "Vi har taget {construction_label} og oversat den til "
            "ren matematik — ingen påklistret skabelon-størrelse.",
        ],
        "size": [
            "Færdige mål er udregnet til {sts_total} m × {gauge_summary} "
            "med {ease_note}.",
            "Det giver {sts_total} m i alt på {gauge_summary} — "
            "den slags tal kan du stole på, fordi de er valideret omg for omg.",
        ],
        "yarn": [
            "Garnforbrug er ca. {meters} meter, hvilket svarer til "
            "ca. {balls} nøgle(r) hvis du bruger et standard 50 g-garn.",
            "Beregn ca. {meters} m garn — typisk {balls} nøgle(r) à 50 g.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
            "Niveau: {difficulty_label} — opskriften antager du har styr på "
            "de mest brugte forkortelser i ordlisten.",
        ],
        "closing": [
            "Strik en prøvelap først, og glæd dig til at se din egen version "
            "vokse frem.",
            "God fornøjelse — og husk: prøvelappen er din ven.",
        ],
    },
    "hue": {
        "intro": [
            "En klassisk hue, strikket bottom-up med rib og en sektor-delt "
            "krone. Den her har {sectors} sektorer og er beregnet til en "
            "hovedomkreds på {head_cm} cm.",
            "Huen her starter som en tube i rib, fortsætter i glatstrik, "
            "og lukker symmetrisk i {sectors} sektorer mod en lille top.",
        ],
        "size": [
            "Færdige mål: {finished_circ} cm i omkreds × {height} cm i højde, "
            "med {rib_height} cm rib. Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — én nøgle 50 g-garn rækker som "
            "regel til en voksenstørrelse, hvis løbelængden er over 150 m.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Hvis du allerede kan rib + "
            "glatstrik + 2 r sm, har du alle byggesten.",
        ],
        "closing": [
            "God strikketid.",
        ],
    },
    "tørklæde": {
        "intro": [
            "Et fladt tørklæde i {pattern} — det enkleste sted at "
            "starte, hvis du vil teste et nyt garn eller en ny rapport.",
            "Tørklædet her er en perfekt anledning til at vænne sig til "
            "rytmen i et nyt mønster: ingen ærmer, ingen forøgelser, "
            "kun glatte cm efter cm.",
        ],
        "size": [
            "Færdige mål: {width} × {length} cm. Det er {sts_total} m bredt og "
            "lavet på en strikkefasthed på {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — typisk {balls} nøgle(r) à 50 g.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Tag dig god tid — et tørklæde er et fantastisk projekt at have "
            "på pinden hele vinteren.",
        ],
    },
    "raglan_topdown": {
        "intro": [
            "En klassisk top-down raglan: en konstruktion hvor du kan prøve "
            "trøjen på undervejs og justere længden i farten.",
            "Top-down raglan i ét stykke. Du kaster {sts_total} m op i halsen "
            "og øger ud mod 4 raglanlinjer indtil bærestykket har "
            "{yoke_depth} cm dybde.",
        ],
        "size": [
            "Færdige mål: brystmål {bust} cm med {ease_note}, kropslængde "
            "{body_length} cm, ærmelængde {sleeve_length} cm. "
            "Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — typisk {balls} nøgle(r) à 50 g, "
            "afhængigt af løbelængden.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Har du strikket en hue før, "
            "kan du raglanen — det er bare flere udtagninger.",
        ],
        "closing": [
            "Prøv den på undervejs. Det er hele pointen med top-down.",
        ],
    },
    "sokker": {
        "intro": [
            "Top-down sokker med kilehæl og gusset — den klassiske "
            "skandinaviske sok, opbygget i ét stræk fra skaft til tå.",
        ],
        "size": [
            "Færdige mål: fodlængde {foot_length} cm, fodomkreds "
            "{foot_circ} cm med negativ ease. Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m sokkegarn — en standard 100 g "
            "sokkegarns-nøgle rækker næsten altid til ét par.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Kilehælen er den lærerige del; "
            "den er værd at prøve mindst én gang i livet.",
        ],
        "closing": [
            "Sokker er et perfekt rejseprojekt — små, transportable, addictive.",
        ],
    },
    "bottom_up_sweater": {
        "intro": [
            "Bottom-up sweater i Zimmermann's EPS-tradition. Krop og ærmer "
            "strikkes hver for sig op til ærmegab og samles i et bærestykke.",
        ],
        "size": [
            "Færdige mål: brystmål {bust} cm med {ease_note}, kropslængde "
            "{body_length} cm, ærmelængde {sleeve_length} cm. "
            "Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — afsæt rigeligt; en sweater er "
            "ikke stedet at løbe tør.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Tag tid til at måle løbende — bottom-up giver dig ikke samme "
            "feedback-loop som top-down.",
        ],
    },
    "compound_raglan": {
        "intro": [
            "Compound raglan: krop og ærme har hver sin grading-rytme, "
            "så bærestykket passer perfekt på både kropsbygning og "
            "overarms-omkreds.",
        ],
        "size": [
            "Færdige mål: brystmål {bust} cm, overarm {upper_arm} cm. "
            "Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — typisk {balls} nøgle(r) à 50 g.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Hvis du har strikket en "
            "almindelig raglan, har du tricks til den her — bare med to "
            "uafhængige udtagningstakter i stedet for én.",
        ],
        "closing": [
            "Markér de to takter med farvede markører. Det redder dit hovede.",
        ],
    },
    "half_pi_shawl": {
        "intro": [
            "Elizabeth Zimmermanns half-pi shawl — en halvcirkel bygget på "
            "en simpel matematisk observation: hver gang du fordobler "
            "antallet af masker, fordobler du også radius.",
        ],
        "size": [
            "Sjalet udvider sig over {doublings} fordoblinger og slutter "
            "med {sts_total} masker langs den buede yderkant.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — laceweight giver det mest æteriske "
            "drape, men 4-trådet sport-vægt fungerer også fint.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Hovedudfordringen er "
            "vedligeholdsen af kant-stitches, ikke selve fordoblingen.",
        ],
        "closing": [
            "Block aggressivt. Et lace-sjal vågner først rigtigt op i "
            "blokningen.",
        ],
    },
    "yoke_stranded": {
        "intro": [
            "Top-down yoke-sweater med stranded mønster i bærestykket — "
            "Icelandic / lopapeysa-stilen. Mønstret bæres af et fast "
            "rapport-bredde-tal på {repeat_width} masker.",
        ],
        "size": [
            "Færdige mål: brystmål {bust} cm med {ease_note}, kropslængde "
            "{body_length} cm. Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m fordelt på 2-3 farver — afsæt "
            "rigeligt af kontrastfarven til mønsteret.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Stranding kræver let hånd; "
            "tjek at strækket bagside ikke trækker sammen.",
        ],
        "closing": [
            "Block sweateren — strandwork ser altid bedst ud efter en blokning.",
        ],
    },
    "short_rows_shawl": {
        "intro": [
            "Korte rækker crescent shawl — formen kommer udelukkende af "
            "kortere og kortere rækker, ingen forøgelser inde i rækkerne.",
        ],
        "size": [
            "Sjalet ender med {sts_total} masker på pinden og er bygget over "
            "{increase_rows} forøgelses-rækker.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — perfekt til ét enkelt skein "
            "højkvalitets-garn.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Tysk-stil korte rækker er "
            "den mindst tricky teknik for begyndere.",
        ],
        "closing": [
            "Block i halvmåne-form med t-pins.",
        ],
    },
    "lace_shawl": {
        "intro": [
            "Et aflang lace shawl med rapport-mønster. Strikket fladt, "
            "med garter-bånd top og bund og en symmetrisk lace-rapport "
            "i midten.",
        ],
        "size": [
            "Færdige mål (efter blokning): {width} × {length} cm. "
            "Strikkefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — laceweight til mest dramatisk "
            "blokning, sport-weight til mere hverdagstung version.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Læs altid lace-diagrammet nedefra og op, højre mod venstre på "
            "rs-pinde.",
        ],
    },
    "amigurumi_sphere": {
        "intro": [
            "En amigurumi-kugle, hæklet i spiralrunder fra magic ring. "
            "Klassisk start: 6 fm i ringen, derefter 6 udtagninger pr. omg "
            "indtil kuglen har sin maks. omkreds.",
            "Hæklet kugle — den mest fundamentale amigurumi-form. "
            "Symmetrisk, beregnelig, og perfekt til at lære udtagnings- og "
            "indtagnings-rytmen.",
        ],
        "size": [
            "Færdig diameter ca. {actual_diameter} cm med {sts_total} m i alt "
            "fordelt på {rounds} omg. Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m bomuld eller akryl — vælg et garn "
            "der ikke fnugger, så maskerne forbliver tætte.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Den eneste tekniske "
            "udfordring er en lukket magic ring der ikke åbner sig igen.",
        ],
        "closing": [
            "Stop fast undervejs — fyldningen skal være jævn og tæt, "
            "ikke klumpet.",
        ],
    },
    "amigurumi_cylinder": {
        "intro": [
            "En cylindrisk amigurumi-form — bunden bygges som en cirkel, "
            "kroppen som en lige tube, og toppen lukkes med indtagninger.",
        ],
        "size": [
            "Diameter {actual_diameter} cm, højde {height} cm. "
            "Tubehøjden er {tube_rounds} omg. Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Cylinder-formen er fundamentet for kroppe, ben og halse — "
            "lær den, og du kan amigurumi alt.",
        ],
    },
    "amigurumi_figur": {
        "intro": [
            "En sammensat amigurumi-figur: krop, hoved, ører, arme og ben "
            "hækles hver for sig og syes sammen til sidst.",
        ],
        "size": [
            "Samlet højde ca. {scale} cm. Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — afsæt mest til kroppen.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Den lærerige del er "
            "samlingen, ikke selve hæklingen.",
        ],
        "closing": [
            "Sy øjnene sidst — så kan du justere personligheden til allersidst.",
        ],
    },
    "granny_square": {
        "intro": [
            "Klassisk granny square — 3-stm-clusters, 4 hjørner, "
            "{rounds} omg. Det grundlæggende byggeklods i hækling.",
            "En granny square i {rounds} omgange. Stables 9 sammen og du "
            "har et tæppe; stables 4 sammen og du har en pude.",
        ],
        "size": [
            "Færdig kantlængde ca. {actual_side} cm pr. side. "
            "Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — typisk {balls} nøgle(r) à 50 g hvis "
            "du bruger flere farver.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Den perfekte introduktion "
            "til hækling i runder.",
        ],
        "closing": [
            "Grannies skifter farve i hver omg — gør dem mere visuelt "
            "interessante og bruger op stash-rester.",
        ],
    },
    "haekle_tørklæde": {
        "intro": [
            "Et fladt hæklet tørklæde i {stitch_type}-masker. "
            "Den mest tilgivende konstruktion at starte med.",
        ],
        "size": [
            "Færdige mål: {width} × {length} cm. Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — typisk {balls} nøgle(r) à 50 g.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Tag det med dig overalt — hækling er det mest transportable "
            "håndarbejde der findes.",
        ],
    },
    "filet": {
        "intro": [
            "Filet hækling — pixel-grafik i tråd. Hver celle er enten "
            "åben (1 stm + 2 lm) eller fyldt (3 stm), og sammen danner "
            "de et motiv.",
        ],
        "size": [
            "Grid: {width_cells} × {height_cells} celler. "
            "Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — bomuld giver skarpest "
            "pixel-definition.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Filet kræver præcision; "
            "tæl celler oftere end du tror er nødvendigt.",
        ],
        "closing": [
            "Block hårdt og firkantet til sidst — filet skal være rektangulært "
            "for at motivet læses.",
        ],
    },
    "tunisian": {
        "intro": [
            "Tunisian hækling — en hybrid mellem strik og hækling. Hver "
            "række består af en forward pass (saml løkker på nålen) og en "
            "return pass (luk dem af én efter én).",
        ],
        "size": [
            "Færdige mål: {width} × {length} cm. Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — Tunisian bruger typisk 30 % mere "
            "garn end almindelig hækling for samme areal.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Du har brug for en lang "
            "Tunisian-nål, ikke en standard hæklenål.",
        ],
        "closing": [
            "Tunisian curler. Block hårdt til sidst.",
        ],
    },
    "c2c_blanket": {
        "intro": [
            "Corner-to-corner tæppe — hækles diagonalt fra hjørne til hjørne "
            "i blokke. Hver blok er 3 lm + 3 stm.",
        ],
        "size": [
            "Grid: {width_blocks} × {height_blocks} blokke. "
            "Hæklefasthed: {gauge_summary}.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — afsæt rigeligt; tæpper er garnet "
            "værste fjende.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}. Selve blokken er let; "
            "udfordringen er at holde styr på diagonalrytmen i øgnings- "
            "vs. mindskningsfasen.",
        ],
        "closing": [
            "C2C er det mest taknemmelige format til pixel-grafiske motiver.",
        ],
    },
    "mandala": {
        "intro": [
            "En rund mandala — hver omgang skifter rytme og farve, og "
            "tilsammen tegner de et symmetrisk geometrisk motiv.",
        ],
        "size": [
            "Mandalaen har {rounds} omgange og {sts_total} masker i den "
            "yderste runde.",
        ],
        "yarn": [
            "Garnforbrug ca. {meters} m — vælg 4-6 kontrastfarver til "
            "mest dramatisk effekt.",
        ],
        "difficulty": [
            "Sværhedsgrad: {difficulty_label}.",
        ],
        "closing": [
            "Block fladt og rundt med t-pins, ellers buler den.",
        ],
    },
}
