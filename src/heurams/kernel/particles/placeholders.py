from heurams.kernel.particles import orbital
from .electron import Electron
from .nucleon import Nucleon
from .atom import Atom

orbital_placeholder = {
    "schedule": ["quick_review", "recognition", "final_review"],
    "phases": {
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
    def __init__(self):
        super().__init__("__placeholder__", {}, {})

    def __getitem__(self, key):
        return f"__placeholder__ attempted {key}"


class ElectronPlaceholder(Electron):
    def __init__(self):
        super().__init__("__placeholder__", {"": {"": ""}}, "")


class AtomPlaceholder(Atom):
    def __init__(self):
        super().__init__(
            NucleonPlaceholder(), ElectronPlaceholder(), orbital_placeholder
        )
