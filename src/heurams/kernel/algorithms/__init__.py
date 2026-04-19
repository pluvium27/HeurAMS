from .base import BaseAlgorithm
from .sm2 import SM2Algorithm
from .sm15m import SM15MAlgorithm
from .nsp0 import NSP0Algorithm

__all__ = [
    "SM2Algorithm",
    "BaseAlgorithm",
    "SM15MAlgorithm",
    "NSP0Algorithm",
]

algorithms = {
    "SM-2": SM2Algorithm,
    "NSP-0": NSP0Algorithm,
    "SM-15M": SM15MAlgorithm,
    "Base": BaseAlgorithm,
}
