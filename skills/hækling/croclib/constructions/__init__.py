"""Crochet constructions.

Each generator returns a :class:`Pattern` (list of validated sections).
"""

from lib.visualisering import Pattern, Section
from .amigurumi import (
    AmigurumiSphereSpec, amigurumi_sphere,
    AmigurumiCylinderSpec, amigurumi_cylinder,
    AmigurumiTaperSpec, amigurumi_taper,
)
from .amigurumi_figur import (
    AmigurumiFigurSpec, amigurumi_figur,
    amigurumi_bjørn, amigurumi_kanin,
)
from .granny_square import GrannySquareSpec, generate_granny_square
from .tørklæde import CrochetTørklædeSpec, generate_tørklæde
from .filet import (
    FiletSpec, generate_filet,
    filet_stitches_per_row, filet_foundation_chain,
)
from .tunisian import TunisianSpec, generate_tunisian, TunisianRow
from .c2c_blanket import (
    C2CBlanketSpec, generate_c2c_blanket,
    c2c_total_blocks, c2c_total_dc, c2c_blocks_per_row,
)
from .mandala import (
    MandalaSpec, RoundSpec, generate_mandala, default_round_progression,
)

__all__ = [
    "Pattern", "Section",
    "AmigurumiSphereSpec", "amigurumi_sphere",
    "AmigurumiCylinderSpec", "amigurumi_cylinder",
    "AmigurumiTaperSpec", "amigurumi_taper",
    "AmigurumiFigurSpec", "amigurumi_figur",
    "amigurumi_bjørn", "amigurumi_kanin",
    "GrannySquareSpec", "generate_granny_square",
    "CrochetTørklædeSpec", "generate_tørklæde",
    "FiletSpec", "generate_filet",
    "filet_stitches_per_row", "filet_foundation_chain",
    "TunisianSpec", "generate_tunisian", "TunisianRow",
    "C2CBlanketSpec", "generate_c2c_blanket",
    "c2c_total_blocks", "c2c_total_dc", "c2c_blocks_per_row",
    "MandalaSpec", "RoundSpec", "generate_mandala",
    "default_round_progression",
]
