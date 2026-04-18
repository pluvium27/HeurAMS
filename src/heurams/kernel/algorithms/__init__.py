from .base import BaseAlgorithm
from .sm2 import SM2Algorithm
from .sm15m import SM15MAlgorithm
from .fast0 import FAST0Algorithm

__all__ = [
    "SM2Algorithm",
    "BaseAlgorithm",
    "SM15MAlgorithm",
    "FAST0Algorithm",
]

algorithms = {
    "SM-2": SM2Algorithm,
    "FAST-0": FAST0Algorithm,
    "SM-15M": SM15MAlgorithm,
    "Base": BaseAlgorithm,
}
