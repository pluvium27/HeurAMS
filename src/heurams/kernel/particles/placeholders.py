"""占位符模块

提供用于 UI 预览和测试的占位粒子对象, 避免空值错误. 
"""

from .atom import Atom
from .electron import Electron
from .nucleon import Nucleon

orbital_placeholder = {
    "schedule": ["quick_review", "recognition", "final_review"],
    "routes": {
        "quick_review": [
            ["FillBlank", 1.0],
            ["SelectMeaning", 0.5],
            ["Recognition", 1.0],
        ],
        "recognition": [["Recognition", 1.0]],
        "final_review": [
            ["FillBlank", 0.7],
            ["SelectMeaning", 0.7],
            ["Recognition", 1.0],
        ],
    },
}


class NucleonPlaceholder(Nucleon):
    """核子占位符, 用于 UI 预览"""

    def __init__(self):
        super().__init__("__placeholder__", {}, {})

    def __getitem__(self, key):
        return f"__placeholder__ attempted {key}"


class ElectronPlaceholder(Electron):
    """电子占位符, 用于 UI 预览"""

    def __init__(self):
        super().__init__("__placeholder__", {"": {"": ""}}, "")


class AtomPlaceholder(Atom):
    """原子占位符, 用于 UI 预览"""

    def __init__(self):
        super().__init__(
            NucleonPlaceholder(), ElectronPlaceholder(), orbital_placeholder
        )
