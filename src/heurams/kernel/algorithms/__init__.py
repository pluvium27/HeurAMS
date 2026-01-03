from .base import BaseAlgorithm
from .sm2 import SM2Algorithm
from .sm15m import SM15MAlgorithm

__all__ = [
    "SM2Algorithm",
    "BaseAlgorithm",
    "SM15MAlgorithm",
]

algorithms = {
    "SM-2": SM2Algorithm,
    "SM-15M": SM15MAlgorithm,
    "Base": BaseAlgorithm,
}
