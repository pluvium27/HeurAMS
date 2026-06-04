import random
from functools import reduce

from tabulate import tabulate as tabu
from transitions import Machine

import heurams.kernel.particles as pt
import heurams.kernel.puzzles as puz
from heurams.services.logger import get_logger

from .states import ExpanderState, RouterState

logger = get_logger(__name__)


class Expander(Machine):
    """单原子调度展开器

    根据轨道策略 (orbital) 将单个原子展开为谜题序列. 
    包含 exammode (考试模式) 和 retronly (回溯模式) 两个阶段. 

    Attributes:
        atom: 关联的 Atom 实例
        route: 当前路由阶段
        puzzles_inf: 展开后的谜题信息列表
        min_ratings: 每个谜题的最低评分记录
    """

    def __init__(self, atom: pt.Atom, route=RouterState.RECOGNITION):
        self.route = route
        self.cursor = 0
        self.atom = atom
        self.current_puzzle_inf: dict
        # route 为 RouterState 枚举实例, 需要获取其value
        route_value = route.value
        states = [
            {"name": ExpanderState.EXAMMODE.value},
            {"name": ExpanderState.RETRONLY.value},
        ]

        transitions = [
            {
                "trigger": "finish",
                "source": ExpanderState.EXAMMODE.value,
                "dest": ExpanderState.RETRONLY.value,
            },
        ]
        if route == RouterState.FINISHED:
            Machine.__init__(
                self,
                states=states,
                transitions=transitions,
                initial=ExpanderState.EXAMMODE.value,
            )
            return
        orbital_schedule = atom.registry["orbital"]["routes"][route_value]  # type: ignore
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
            self.min_ratings.append(float("inf"))

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial=ExpanderState.EXAMMODE.value,
        )

    def get_puzzles_inf(self):
        """获取谜题信息列表

        回溯模式下返回识别谜题, 否则返回展开的谜题列表. 

        Returns:
            谜题信息字典列表
        """
        if self.state == "retronly":
            return [{"puzzle": puz.puzzles["recognition"], "alia": "Recognition"}]
        return self.puzzles_inf

    def get_current_puzzle_inf(self):
        """获取当前谜题信息

        Returns:
            当前谜题的信息字典
        """
        if self.state == "retronly":
            return {"puzzle": puz.puzzles["recognition"], "alia": "Recognition"}
        return self.current_puzzle_inf

    def report(self, rating):
        """报告当前谜题的评分

        Args:
            rating: 用户评分 (0-5)
        """
        if self.puzzles_inf:
            self.min_ratings[self.cursor] = min(rating, self.min_ratings[self.cursor])

    def get_quality(self):
        """获取所有谜题的最低评分

        仅在回溯模式 (retronly) 下可用. 

        Returns:
            所有谜题评分的最小值

        Raises:
            IndexError: 非回溯模式下调用
        """
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
                "Type": "Expander",
                "Atom": truncate(self.atom.ident),
                "State": self.state,
                "Progress": f"{self.cursor + 1} / {len(self.puzzles_inf)}",
                "Procession": list(
                    map(lambda f: truncate(f["alia"]), self.puzzles_inf)
                ),
                "Current Puzzle": f"{self.current_puzzle_inf['alia']}@{self.current_puzzle_inf['puzzle'].__name__}",  # type: ignore
            }
        ]
        return str(tabu(dic, headers="keys", tablefmt=style)) + ends
