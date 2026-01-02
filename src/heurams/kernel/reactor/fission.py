import random

import heurams.kernel.evaluators as puz
import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .states import PhaserState


class Fission:
    """裂变器: 单原子调度展开器"""

    def __init__(self, atom: pt.Atom, phase_state=PhaserState.RECOGNITION):
        self.logger = get_logger(__name__)
        self.atom = atom
        
        #NOTE: phase 为 PhaserState 枚举实例，需要获取其value
        phase_value = phase_state.value if isinstance(phase_state, PhaserState) else phase_state
        
        self.orbital_schedule = atom.registry["orbital"]["schedule"][phase_value]  # type: ignore
        self.orbital_puzzles = atom.registry["orbital"]["puzzles"]
        
        self.puzzles = list()
        for item, possibility in self.orbital_schedule:  # type: ignore
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
            
            self.logger.debug(f"orbital 项处理完成: {item}")

    def generate(self):
        yield from self.puzzles