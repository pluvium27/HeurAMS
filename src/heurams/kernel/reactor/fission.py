import heurams.kernel.particles as pt
import heurams.kernel.puzzles as puz
import random
from .states import PhaserState
from heurams.services.logger import get_logger


class Fission:
    """裂变器: 单原子调度展开器"""

    def __init__(self, atom: pt.Atom, phase=PhaserState.RECOGNITION):
        self.logger = get_logger(__name__)
        self.atom = atom
        # print(f"{phase.value}")
        self.orbital_schedule = atom.registry["orbital"]["schedule"][phase.value]  # type: ignore
        self.orbital_puzzles = atom.registry["orbital"]["puzzles"]
        # print(self.orbital_schedule)
        self.puzzles = list()
        for item, possibility in self.orbital_schedule:  # type: ignore
            print(f"ad:{item}")
            self.logger.debug(f"开始处理 orbital 项: {item}")
            if not isinstance(possibility, float):
                possibility = float(possibility)
            while possibility > 1:
                self.puzzles.append(
                    {
                        "puzzle": puz.puzzles[self.orbital_puzzles[item]["__origin__"]],
                        "alia": item,
                    }
                )
                possibility -= 1
            if random.random() <= possibility:
                self.puzzles.append(
                    {
                        "puzzle": puz.puzzles[self.orbital_puzzles[item]["__origin__"]],
                        "alia": item,
                    }
                )
            print(f"ok:{item}")
            self.logger.debug(f"orbital 项处理完成: {item}")

    def generate(self):
        yield from self.puzzles
