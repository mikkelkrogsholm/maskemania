"""Construction generators.

Each construction takes structured inputs and returns a Pattern (a list of
sections, each with a label, instruction text, and validated stitch counts).
The Pattern is then handed to a formatter (in templates/) to produce final
prose. Constructions never write prose themselves.
"""
from lib.visualisering import Pattern, Section
from .hue import generate_hue, HueSpec
from .tørklæde import generate_tørklæde, TørklædeSpec
from .raglan_topdown import generate_raglan, RaglanSpec
from .sokker import generate_sokker, SokkerSpec, heel_turn
from .bottom_up_sweater import (
    generate_bottom_up_sweater, BottomUpSweaterSpec,
    eps_percentages,
)
from .compound_raglan import (
    generate_compound_raglan, CompoundRaglanSpec,
)
from .half_pi_shawl import (
    generate_half_pi_shawl, HalfPiShawlSpec, pi_shawl_progression,
)
from .yoke_stranded import (
    generate_yoke_stranded, YokeStrandedSpec, repeat_fit, render_color_chart,
    DEFAULT_MOTIF,
)
from .short_rows_shawl import (
    generate_short_rows_shawl, ShortRowsShawlSpec,
)
from .lace_shawl import (
    generate_lace_shawl, LaceShawlSpec, LaceRepeat, REPEATS as LACE_REPEATS,
    validate_repeat_balance,
)
from .colorwork_swatch import (
    generate_colorwork_swatch, ColorworkSwatchSpec,
)

__all__ = [
    "Pattern", "Section",
    "generate_hue", "HueSpec",
    "generate_tørklæde", "TørklædeSpec",
    "generate_raglan", "RaglanSpec",
    "generate_sokker", "SokkerSpec", "heel_turn",
    "generate_bottom_up_sweater", "BottomUpSweaterSpec",
    "eps_percentages",
    "generate_compound_raglan", "CompoundRaglanSpec",
    "generate_half_pi_shawl", "HalfPiShawlSpec", "pi_shawl_progression",
    "generate_yoke_stranded", "YokeStrandedSpec", "repeat_fit",
    "render_color_chart", "DEFAULT_MOTIF",
    "generate_short_rows_shawl", "ShortRowsShawlSpec",
    "generate_lace_shawl", "LaceShawlSpec", "LaceRepeat", "LACE_REPEATS",
    "validate_repeat_balance",
    "generate_colorwork_swatch", "ColorworkSwatchSpec",
]
