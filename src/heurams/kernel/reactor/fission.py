import random

import heurams.kernel.evaluators as puz
import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .states import PhaserState


class Fission:
    """单原子调度展开器"""

    def __init__(self, atom: pt.Atom, phase_state=PhaserState.RECOGNITION):
        self.cursor = 0
        self.logger = get_logger(__name__)
        self.atom = atom

        # NOTE: phase 为 PhaserState 枚举实例，需要获取其value
        phase_value = (
            phase_state.value if isinstance(phase_state, PhaserState) else phase_state
        )

        self.orbital_schedule = atom.registry["orbital"]["phases"][phase_value]  # type: ignore
        self.orbital_puzzles = atom.registry["nucleon"]["puzzles"]

        self.puzzles = list()
        for item, possibility in self.orbital_schedule:  # type: ignore
            self.logger.debug(f"开始处理: {item}")
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

            self.logger.debug(f"orbital 项处理完成: {item}")

    def get_puzzles(self):
        return self.puzzles

    def get_current_puzzle(self, forward=0):
        if forward:
            if len(self.puzzles) <= self.cursor + 1:
                return 0
            self.cursor += 1
            return self.puzzles[self.cursor]
        else:
            return self.puzzles[self.cursor]

    def check_passed(self):
        for i in self.puzzles:
            if i["finished"] == 0:
                return 0
        return 1
