from typing import Any, Iterable, TypedDict
from typing_extensions import Self
from .lict import Lict

class ParticalsContainer(TypedDict):
    nucleons: Lict
    electrons: Lict
    atoms: Lict