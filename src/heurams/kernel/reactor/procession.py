from tabulate import tabulate as tabu
from transitions import Machine

import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .expander import Expander
from .states import RouterState, ProcessionState

logger = get_logger(__name__)


class Procession(Machine):
    """队列: 标识单次记忆流程"""

    def __init__(self, atoms: list, route_state: RouterState, name_: str = ""):
        self.current_atom: pt.Atom | None
        self.atoms = atoms
        self.current_atom = atoms[0] if atoms else None
        self.cursor = 0
        self.name_ = name_
        self.route = route_state

        states = [
            {"name": ProcessionState.ACTIVE.value, "on_enter": "on_active"},
            {"name": ProcessionState.FINISHED.value, "on_enter": "on_finished"},
        ]

        transitions = [
            {
                "trigger": "finish",
                "source": ProcessionState.ACTIVE.value,
                "dest": ProcessionState.FINISHED.value,
            },
            {
                "trigger": "restart",
                "source": ProcessionState.FINISHED.value,
                "dest": ProcessionState.ACTIVE.value,
            },
        ]

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial=ProcessionState.ACTIVE.value,
        )

    def on_active(self):
        """进入active状态时的回调"""
        pass

    def on_finished(self):
        """进入FINISHED状态时的回调"""
        pass

    def forward(self, step=1):
        """将记忆原子指针向前移动并依情况更新原子(返回 1)或完成队列(返回 0)"""
        self.cursor += step
        if self.cursor >= len(self.atoms):
            if self.state != ProcessionState.FINISHED.value:
                self.finish()  # 触发状态转换
        else:
            if self.state != ProcessionState.ACTIVE.value:
                self.restart()  # 确保在active状态
            self.current_atom = self.atoms[self.cursor]

    def append(self, atom=None):
        """追加(回忆失败的)原子(默认为当前原子)到队列末端"""
        if atom is None:
            atom = self.current_atom

        if not self.atoms or self.atoms[-1] != atom or len(self) <= 1:
            self.atoms.append(atom)

    def __len__(self):
        if not self.atoms:
            return 0
        length = len(self.atoms) - self.cursor
        return length

    def process(self):
        return self.cursor

    def total_length(self):
        total = len(self.atoms)
        return total

    def is_empty(self):
        empty = len(self.atoms) == 0
        return empty

    def get_expander(self):
        return Expander(atom=self.current_atom, route=self.route)  # type: ignore

    def __repr__(self, style="pipe", ends="\n"):
        from heurams.services.textproc import truncate

        dic = [
            {
                "Type": "Procession",
                "Name": self.name_,
                "State": self.state,
                "Progress": f"{self.cursor + 1} / {len(self.atoms)}",
                "Procession": list(map(lambda f: truncate(f.ident), self.atoms)),
                "Current Atom": self.current_atom.ident,  # type: ignore
            }
        ]
        return str(tabu(dic, headers="keys", tablefmt=style)) + ends
