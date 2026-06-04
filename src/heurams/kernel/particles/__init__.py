"""粒子数据模型模块

定义记忆单元的核心数据结构: Nucleon (内容)、Electron (状态)、Atom (组装). 
"""

from .atom import Atom
from .electron import Electron
from .nucleon import Nucleon
from .placeholders import (
    AtomPlaceholder,
    ElectronPlaceholder,
    NucleonPlaceholder,
    orbital_placeholder,
)

# from .orbital import Orbital

__all__ = [
    "Atom",
    "Electron",
    "Nucleon",
    "AtomPlaceholder",
    "NucleonPlaceholder",
    "ElectronPlaceholder",
    "orbital_placeholder",
]
