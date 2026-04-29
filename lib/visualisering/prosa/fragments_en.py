"""English prose fragment library, keyed by construction and slot.

Mirrors :mod:`.fragments_da` — same structure, English copy. The renderer
selects this dict when ``lang == "en"`` is passed to ``intro_paragraphs``.
"""

from __future__ import annotations


FRAGMENTS_EN: dict[str, dict[str, list[str]]] = {
    "_default": {
        "intro": [
            "This {construction_label} is computed from your own "
            "measurements and your own gauge — so it fits, the first time.",
            "{construction_label}: a construction built up from "
            "{stitch_count_total} stitches, calculated for your gauge.",
            "We've taken {construction_label} and translated it into "
            "pure math — no off-the-rack template size.",
        ],
        "size": [
            "Finished measurements are computed at {sts_total} sts × "
            "{gauge_summary} with {ease_note}.",
            "That gives {sts_total} sts total at {gauge_summary} — "
            "numbers you can trust because they're validated round by round.",
        ],
        "yarn": [
            "Yardage runs ~{meters} m, which is roughly {balls} skein(s) of "
            "a standard 50 g yarn.",
            "Plan for ~{meters} m of yarn — typically {balls} skein(s) at 50 g.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
            "Level: {difficulty_label} — the pattern assumes you're comfortable "
            "with the abbreviations in the glossary.",
        ],
        "closing": [
            "Knit a swatch first, and enjoy watching your own version emerge.",
            "Have fun — and remember, the swatch is your friend.",
        ],
    },
    "hue": {
        "intro": [
            "A classic hat, knit bottom-up with a ribbed brim and a "
            "sectored crown. This one has {sectors} sectors and is sized "
            "for a {head_cm} cm head circumference.",
            "The hat starts as a tube in rib, continues in stockinette, "
            "and closes symmetrically across {sectors} sectors toward a "
            "small crown.",
        ],
        "size": [
            "Finished: {finished_circ} cm circumference × {height} cm "
            "tall, with a {rib_height} cm rib. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — one 50 g skein normally suffices for an "
            "adult size if length per skein is over 150 m.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. If you can do rib + stockinette "
            "+ k2tog, you have all the building blocks.",
        ],
        "closing": [
            "Happy knitting.",
        ],
    },
    "tørklæde": {
        "intro": [
            "A flat scarf in {pattern} — the simplest place to start when "
            "you want to test a new yarn or a new repeat.",
        ],
        "size": [
            "Finished: {width} × {length} cm. That's {sts_total} sts wide at "
            "a gauge of {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — typically {balls} skein(s) at 50 g.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Take your time — a scarf is a wonderful project to keep on "
            "the needles all winter.",
        ],
    },
    "raglan_topdown": {
        "intro": [
            "A classic top-down raglan: a construction where you can try "
            "the sweater on as you go and adjust length on the fly.",
        ],
        "size": [
            "Finished: bust {bust} cm with {ease_note}, body length "
            "{body_length} cm, sleeve length {sleeve_length} cm. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — typically {balls} skein(s) at 50 g.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. If you've knit a hat before, "
            "you can knit this raglan — just more increases.",
        ],
        "closing": [
            "Try it on as you go. That's the whole point of top-down.",
        ],
    },
    "sokker": {
        "intro": [
            "Top-down socks with a heel flap and gusset — the classic "
            "Scandinavian sock, knit in one piece from cuff to toe.",
        ],
        "size": [
            "Finished: foot length {foot_length} cm, foot circumference "
            "{foot_circ} cm with negative ease. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m sock yarn — a standard 100 g sock skein "
            "almost always covers one pair.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The heel flap is the "
            "instructive part; worth doing at least once.",
        ],
        "closing": [
            "Socks are the perfect travel project — small, portable, addictive.",
        ],
    },
    "bottom_up_sweater": {
        "intro": [
            "Bottom-up sweater in the Zimmermann EPS tradition. Body and "
            "sleeves are knit separately to underarm and joined into a yoke.",
        ],
        "size": [
            "Finished: bust {bust} cm with {ease_note}, body length "
            "{body_length} cm, sleeve length {sleeve_length} cm. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — buy generously; a sweater is not the "
            "place to run short.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Measure as you go — bottom-up doesn't give you the same "
            "feedback loop as top-down.",
        ],
    },
    "compound_raglan": {
        "intro": [
            "Compound raglan: body and sleeve each have their own grading "
            "cadence, so the yoke fits both your bust and your bicep.",
        ],
        "size": [
            "Finished: bust {bust} cm, upper arm {upper_arm} cm. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — typically {balls} skein(s) at 50 g.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. If you've done a regular "
            "raglan, you have the tricks for this one — just two "
            "independent increase cadences instead of one.",
        ],
        "closing": [
            "Mark the two cadences with different colored markers. It saves "
            "your sanity.",
        ],
    },
    "half_pi_shawl": {
        "intro": [
            "Elizabeth Zimmermann's half-pi shawl — a half-circle built on "
            "a simple mathematical observation: every time you double "
            "the stitch count, you double the radius.",
        ],
        "size": [
            "The shawl expands across {doublings} doublings and ends with "
            "{sts_total} sts along the curved outer edge.",
        ],
        "yarn": [
            "Yardage ~{meters} m — laceweight gives the most ethereal "
            "drape, but fingering also works.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The main challenge is "
            "maintaining the edge stitches, not the doubling itself.",
        ],
        "closing": [
            "Block aggressively. A lace shawl really only wakes up under "
            "blocking.",
        ],
    },
    "yoke_stranded": {
        "intro": [
            "Top-down yoke sweater with stranded colorwork in the yoke — "
            "the Icelandic / lopapeysa style. The motif rides on a fixed "
            "repeat width of {repeat_width} stitches.",
        ],
        "size": [
            "Finished: bust {bust} cm with {ease_note}, body length "
            "{body_length} cm. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m across 2-3 colors — set aside extra of "
            "the contrast color for the motif.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. Stranding requires a light "
            "hand; check that the floats on the back aren't pulling tight.",
        ],
        "closing": [
            "Block the sweater — stranded work always looks better after a "
            "wet block.",
        ],
    },
    "short_rows_shawl": {
        "intro": [
            "Short-row crescent shawl — the shape comes purely from "
            "increasingly shorter rows, no in-row increases.",
        ],
        "size": [
            "The shawl ends with {sts_total} sts on the needle and is built "
            "across {increase_rows} increase rows.",
        ],
        "yarn": [
            "Yardage ~{meters} m — perfect for a single skein of "
            "high-quality yarn.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. German short rows are the "
            "least tricky technique for beginners.",
        ],
        "closing": [
            "Block in a crescent shape with t-pins.",
        ],
    },
    "lace_shawl": {
        "intro": [
            "A rectangular lace shawl with a repeating motif. Worked flat, "
            "with garter borders top and bottom and a symmetric lace "
            "repeat in the middle.",
        ],
        "size": [
            "Finished (after blocking): {width} × {length} cm. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — laceweight for the most dramatic "
            "blocking, sport for an everyday version.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Read the lace chart bottom-up, right-to-left on RS rows.",
        ],
    },
    "amigurumi_sphere": {
        "intro": [
            "An amigurumi sphere, crocheted in spiral rounds from a magic "
            "ring. Classic start: 6 sc in the ring, then 6 increases per "
            "round until the sphere reaches its max circumference.",
        ],
        "size": [
            "Finished diameter ~{actual_diameter} cm with {sts_total} sts "
            "total across {rounds} rounds. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m of cotton or acrylic — pick a yarn that "
            "doesn't fuzz so the stitches stay tight.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The only technical challenge "
            "is a magic ring that stays closed.",
        ],
        "closing": [
            "Stuff firmly as you go — filling should be even and dense, "
            "not lumpy.",
        ],
    },
    "amigurumi_cylinder": {
        "intro": [
            "A cylindrical amigurumi shape — base built as a circle, body "
            "as a straight tube, top closed with decreases.",
        ],
        "size": [
            "Diameter {actual_diameter} cm, height {height} cm. Tube "
            "height is {tube_rounds} rounds. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Cylinders are the foundation for bodies, legs and necks — "
            "learn this and you can amigurumi anything.",
        ],
    },
    "amigurumi_figur": {
        "intro": [
            "A composite amigurumi figure: body, head, ears, arms and "
            "legs are crocheted separately and sewn together.",
        ],
        "size": [
            "Total height ~{scale} cm. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — set aside the most for the body.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The instructive part is the "
            "assembly, not the crochet itself.",
        ],
        "closing": [
            "Sew the eyes last — that lets you tweak the personality at "
            "the end.",
        ],
    },
    "granny_square": {
        "intro": [
            "Classic granny square — 3-dc clusters, 4 corners, "
            "{rounds} rounds. The fundamental building block of crochet.",
        ],
        "size": [
            "Finished side length ~{actual_side} cm per side. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — typically {balls} skein(s) at 50 g if "
            "you use multiple colors.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The perfect introduction to "
            "crochet in the round.",
        ],
        "closing": [
            "Grannies that change color every round are visually richer "
            "and use up stash leftovers.",
        ],
    },
    "haekle_tørklæde": {
        "intro": [
            "A flat crochet scarf in {stitch_type} stitches. The most "
            "forgiving construction to start with.",
        ],
        "size": [
            "Finished: {width} × {length} cm. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — typically {balls} skein(s) at 50 g.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Take it everywhere — crochet is the most portable handcraft "
            "there is.",
        ],
    },
    "filet": {
        "intro": [
            "Filet crochet — pixel graphics in thread. Each cell is either "
            "open (1 dc + 2 ch) or filled (3 dc), and together they form "
            "the motif.",
        ],
        "size": [
            "Grid: {width_cells} × {height_cells} cells. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — cotton gives the sharpest pixel "
            "definition.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. Filet rewards precision; "
            "count cells more often than you think you need to.",
        ],
        "closing": [
            "Block hard and square at the end — filet must be rectangular "
            "for the motif to read.",
        ],
    },
    "tunisian": {
        "intro": [
            "Tunisian crochet — a hybrid between knit and crochet. Each "
            "row has a forward pass (collect loops on the hook) and a "
            "return pass (close them off one by one).",
        ],
        "size": [
            "Finished: {width} × {length} cm. Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — Tunisian uses ~30 % more yarn than "
            "regular crochet for the same area.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. You'll need a long Tunisian "
            "hook, not a regular crochet hook.",
        ],
        "closing": [
            "Tunisian curls. Block firmly at the end.",
        ],
    },
    "c2c_blanket": {
        "intro": [
            "Corner-to-corner blanket — crocheted diagonally from corner to "
            "corner in blocks. Each block is 3 ch + 3 dc.",
        ],
        "size": [
            "Grid: {width_blocks} × {height_blocks} blocks. "
            "Gauge: {gauge_summary}.",
        ],
        "yarn": [
            "Yardage ~{meters} m — buy generously; blankets devour yarn.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}. The block itself is easy; "
            "the challenge is keeping track of the diagonal in increase- "
            "vs. decrease-phase.",
        ],
        "closing": [
            "C2C is the most satisfying format for pixel-graphic motifs.",
        ],
    },
    "mandala": {
        "intro": [
            "A round mandala — each round changes rhythm and color, and "
            "together they trace a symmetric geometric motif.",
        ],
        "size": [
            "The mandala has {rounds} rounds and {sts_total} sts in the "
            "outermost round.",
        ],
        "yarn": [
            "Yardage ~{meters} m — pick 4-6 contrasting colors for the "
            "most dramatic effect.",
        ],
        "difficulty": [
            "Difficulty: {difficulty_label}.",
        ],
        "closing": [
            "Block flat and round with t-pins, otherwise it cups.",
        ],
    },
}
