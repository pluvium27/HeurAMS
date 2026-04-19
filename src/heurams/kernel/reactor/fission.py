import random
from functools import reduce

from tabulate import tabulate as tabu
from transitions import Machine

import heurams.kernel.particles as pt
import heurams.kernel.puzzles as puz
from heurams.services.logger import get_logger

from .states import FissionState, PhaserState

logger = get_logger(__name__)


class Fission(Machine):
    """单原子调度展开器"""

    def __init__(self, atom: pt.Atom, phase=PhaserState.RECOGNITION):
        self.phase = phase
        self.cursor = 0
        self.atom = atom
        self.current_puzzle_inf: dict
        # phase 为 PhaserState 枚举实例, 需要获取其value
        phase_value = phase.value
        states = [
            {"name": FissionState.EXAMMODE.value},
            {"name": FissionState.RETRONLY.value},
        ]

        transitions = [
            {
                "trigger": "finish",
                "source": FissionState.EXAMMODE.value,
                "dest": FissionState.RETRONLY.value,
            },
        ]
        if phase == PhaserState.FINISHED:
            Machine.__init__(
                self,
                states=states,
                transitions=transitions,
                initial=FissionState.EXAMMODE.value,
            )
            return
        orbital_schedule = atom.registry["orbital"]["phases"][phase_value]  # type: ignore
        orbital_puzzles = atom.registry["nucleon"]["puzzles"]
        self.puzzles_inf = list()
        self.min_ratings = []
        for item, possibility in orbital_schedule:  # type: ignore
            logger.debug(f"开始处理: {item}")

            puzzle = puz.puzzles[orbital_puzzles[item]["__origin__"]]

            if not isinstance(possibility, float):
                possibility = float(possibility)

            while possibility > 1:
                self.puzzles_inf.append(
                    {
                        "puzzle": puzzle,
                        "alia": item,
                    }
                )
                possibility -= 1

            if random.random() <= possibility:
                self.puzzles_inf.append(
                    {
                        "puzzle": puzzle,
                        "alia": item,
                    }
                )
        if self.puzzles_inf:
            self.current_puzzle_inf = self.puzzles_inf[0]

        for i in range(len(self.puzzles_inf)):
            self.min_ratings.append(float('inf'))

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial=FissionState.EXAMMODE.value,
        )

    def get_puzzles_inf(self):
        if self.state == "retronly":
            return [{"puzzle": puz.puzzles["recognition"], "alia": "Recognition"}]
        return self.puzzles_inf

    def get_current_puzzle_inf(self):
        if self.state == "retronly":
            return {"puzzle": puz.puzzles["recognition"], "alia": "Recognition"}
        return self.current_puzzle_inf

    def report(self, rating):
        if self.puzzles_inf:
            self.min_ratings[self.cursor] = min(rating, self.min_ratings[self.cursor])

    def get_quality(self):
        if self.puzzles_inf:
            if self.is_state("retronly", self):
                return reduce(lambda x, y: min(x, y), self.min_ratings)
            raise IndexError

    def forward(self, step=1):
        """将谜题指针向前移动并依情况更新或完成"""
        self.cursor += step
        if self.cursor >= len(self.puzzles_inf):
            if self.state != "retronly":
                self.finish()
        else:
            self.current_puzzle_inf = self.puzzles_inf[self.cursor]

    def __repr__(self, style="pipe", ends="\n") -> str:
        from heurams.services.textproc import truncate

        dic = [
            {
                "Type": "Fission",
                "Atom": truncate(self.atom.ident),
                "State": self.state,
                "Progress": f"{self.cursor + 1} / {len(self.puzzles_inf)}",
                "Queue": list(map(lambda f: truncate(f["alia"]), self.puzzles_inf)),
                "Current Puzzle": f"{self.current_puzzle_inf['alia']}@{self.current_puzzle_inf['puzzle'].__name__}",  # type: ignore
            }
        ]
        return str(tabu(dic, headers="keys", tablefmt=style)) + ends
