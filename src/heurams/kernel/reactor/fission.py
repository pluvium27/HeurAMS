from functools import reduce
import random

import heurams.kernel.puzzles as puz
import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from transitions import Machine
from .states import FissionState, PhaserState

logger = get_logger(__name__)

class Fission(Machine):
    """单原子调度展开器"""

    def __init__(self, atom: pt.Atom, phase=PhaserState.RECOGNITION):
        self.phase = phase
        self.cursor = 0
        self.atom = atom
        self.current_puzzle: puz.BasePuzzle
        # phase 为 PhaserState 枚举实例, 需要获取其value
        phase_value = phase.value
        orbital_schedule = atom.registry["orbital"]["phases"][phase_value]  # type: ignore
        orbital_puzzles = atom.registry["nucleon"]["puzzles"]
        self.puzzles = list()
        self.min_ratings = []
        for item, possibility in orbital_schedule:  # type: ignore
            self.logger.debug(f"开始处理: {item}")
            if not isinstance(possibility, float):
                possibility = float(possibility)

            while possibility > 1:
                self.puzzles.append(
                    {
                        "puzzle": puz.puzzles[orbital_puzzles[item]["__origin__"]],
                        "alia": item,
                    }
                )
                possibility -= 1

            if random.random() <= possibility:
                self.puzzles.append(
                    {
                        "puzzle": puz.puzzles[orbital_puzzles[item]["__origin__"]],
                        "alia": item,
                    }
                )
        
        states = [
            {"name": FissionState.EXAMMODE.value, "on_enter": "on_exammode"},
            {"name": FissionState.RETRONLY.value, "on_enter": "on_retronly"},
        ]

        transitions = [
            {
                "trigger": "finish",
                "source": FissionState.EXAMMODE.value,
                "dest": FissionState.RETRONLY.value,
            },
        ]

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial="Evaluator_0",
        )

    def get_puzzles(self):
        if self.state == 'retronly':
            return [puz.puzzles['recognition']]
        return self.puzzles

    def get_current_puzzle(self):
        if self.state == 'retronly':
            return puz.puzzles['recognition']
        return self.current_puzzle
    
    def report(self, rating):
        self.min_ratings[self.cursor] = min(rating, self.min_ratings[self.cursor])
    
    def get_quality(self):
        if self.is_state("exammode", self):
            return reduce(lambda x,y: min(x, y), self.min_ratings)
        return -1

    def forward(self, step=1):
        """将谜题指针向前移动并依情况更新或完成"""
        logger.debug("Procession.forward: step=%d, 当前 cursor=%d", step, self.cursor)
        self.cursor += step
        if self.cursor >= len(self.puzzles):
            if self.state != 'retronly':
                self.finish()
        else:
            self.current_puzzle = self.puzzles[self.cursor]