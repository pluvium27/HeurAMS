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
        logger.debug(
            "Procession.__init__: 原子数量=%d, route=%s, name='%s'",
            len(atoms),
            route_state.value,
            name_,
        )
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

        logger.debug("Procession 初始化完成, 队列长度=%d", len(self.atoms))

    def on_active(self):
        """进入active状态时的回调"""
        logger.debug("Procession 进入 active 状态")

    def on_finished(self):
        """进入FINISHED状态时的回调"""
        logger.debug("Procession 进入 FINISHED 状态")

    def forward(self, step=1):
        """将记忆原子指针向前移动并依情况更新原子(返回 1)或完成队列(返回 0)"""
        logger.debug("Procession.forward: step=%d, 当前 cursor=%d", step, self.cursor)
        self.cursor += step
        if self.cursor >= len(self.atoms):
            if self.state != ProcessionState.FINISHED.value:
                self.finish()  # 触发状态转换
            logger.debug("Procession 已完成")
        else:
            if self.state != ProcessionState.ACTIVE.value:
                self.restart()  # 确保在active状态
            self.current_atom = self.atoms[self.cursor]
            logger.debug("cursor 更新为: %d", self.cursor)
            logger.debug(
                "当前原子更新为: %s",
                self.current_atom.ident if self.current_atom else "None",
            )

    def append(self, atom=None):
        """追加(回忆失败的)原子(默认为当前原子)到队列末端"""
        if atom is None:
            atom = self.current_atom
        logger.debug("Procession.append: atom=%s", atom.ident if atom else "None")

        if not self.atoms or self.atoms[-1] != atom or len(self) <= 1:
            self.atoms.append(atom)
            logger.debug("原子已追加到队列, 新队列长度=%d", len(self.atoms))
        else:
            logger.debug("原子未追加(重复或队列长度<=1)")

    def __len__(self):
        if not self.atoms:
            return 0
        length = len(self.atoms) - self.cursor
        logger.debug("Procession.__len__: 剩余长度=%d", length)
        return length

    def process(self):
        logger.debug("Procession.process: cursor=%d", self.cursor)
        return self.cursor

    def total_length(self):
        total = len(self.atoms)
        logger.debug("Procession.total_length: %d", total)
        return total

    def is_empty(self):
        empty = len(self.atoms) == 0
        logger.debug("Procession.is_empty: %s", empty)
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
