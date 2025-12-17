"""
Particle 模块 - 粒子对象系统

提供闪卡所需对象, 使用物理学粒子的领域驱动设计
"""

from heurams.services.logger import get_logger

logger = get_logger(__name__)
logger.debug("粒子模块已加载")

from .electron import Electron
from .nucleon import Nucleon
from .orbital import Orbital
from .atom import Atom, atom_registry
from .probe import probe_all, probe_by_filename
from .loader import load_nucleon, load_electron

__all__ = [
    "Electron",
    "Nucleon",
    "Orbital",
    "Atom",
    "probe_all",
    "probe_by_filename",
    "load_nucleon",
    "load_electron",
    "atom_registry",
]
