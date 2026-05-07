from transitions import Machine

import heurams.kernel.particles as pt
from heurams.kernel.particles.placeholders import AtomPlaceholder
from heurams.services.logger import get_logger

from .procession import Procession
from .states import RouterState, ProcessionState

logger = get_logger(__name__)


class Router(Machine):
    """全局调度阶段路由器"""

    def __init__(self, atoms: list[pt.Atom]) -> None:
        logger.debug(f"Router.__init__: 原子数量={len(atoms)}")

        self.atoms = atoms
        new_atoms = list()
        old_atoms = list()

        for i in atoms:
            if not i.registry["electron"].is_activated():
                new_atoms.append(i)
            else:
                old_atoms.append(i)

        logger.debug(f"新原子数量={len(new_atoms)}, 旧原子数量={len(old_atoms)}")

        self.processions = list()
        """路由中的所有队列"""
        # TODO: 改进为基于配置文件的可选复习阶段
        if len(old_atoms):
            self.processions.append(
                Procession(old_atoms, RouterState.QUICK_REVIEW, "初始复习")
            )
            logger.debug("创建初始复习 Procession")

        if len(new_atoms):
            self.processions.append(
                Procession(new_atoms, RouterState.RECOGNITION, "新记忆")
            )
            logger.debug("创建新记忆 Procession")

        self.processions.append(Procession(atoms, RouterState.FINAL_REVIEW, "总体复习"))
        logger.debug("创建总体复习 Procession")
        logger.debug("Router 初始化完成, processions 数量=%d", len(self.processions))

        # 设置transitions状态机
        states = [
            {"name": RouterState.UNSURE.value, "on_enter": "on_unsure"},
            {"name": RouterState.QUICK_REVIEW.value, "on_enter": "on_quick_review"},
            {"name": RouterState.RECOGNITION.value, "on_enter": "on_recognition"},
            {"name": RouterState.FINAL_REVIEW.value, "on_enter": "on_final_review"},
            {"name": RouterState.FINISHED.value, "on_enter": "on_finished"},
        ]

        transitions = [
            {"trigger": "to_unsure", "source": "*", "dest": RouterState.UNSURE.value},
            {
                "trigger": "to_quick_review",
                "source": "*",
                "dest": RouterState.QUICK_REVIEW.value,
            },
            {
                "trigger": "to_recognition",
                "source": "*",
                "dest": RouterState.RECOGNITION.value,
            },
            {
                "trigger": "to_final_review",
                "source": "*",
                "dest": RouterState.FINAL_REVIEW.value,
            },
            {
                "trigger": "to_finished",
                "source": "*",
                "dest": RouterState.FINISHED.value,
            },
        ]

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial=RouterState.UNSURE.value,
        )

        self.to_unsure()

    def on_unsure(self):
        """进入UNSURE状态时的回调"""
        logger.debug("Router 进入 UNSURE 状态")

    def on_quick_review(self):
        """进入QUICK_REVIEW状态时的回调"""
        logger.debug("Router 进入 QUICK_REVIEW 状态")

    def on_recognition(self):
        """进入RECOGNITION状态时的回调"""
        logger.debug("Router 进入 RECOGNITION 状态")

    def on_final_review(self):
        """进入FINAL_REVIEW状态时的回调"""
        logger.debug("Router 进入 FINAL_REVIEW 状态")

    def on_finished(self):
        """进入FINISHED状态时的回调"""
        for i in self.atoms:
            i.lock(1)
            i.revise()
        logger.debug("Router 进入 FINISHED 状态")

    def current_procession(self):
        logger.debug("Router.current_procession 被调用")
        for i in self.processions:
            i: Procession
            if i.state != ProcessionState.FINISHED.value:
                # if i.route == RouterState.UNSURE: 此判断是不必要的 因为没有这种 Procession
                if i.route == RouterState.QUICK_REVIEW:
                    self.to_quick_review()
                elif i.route == RouterState.RECOGNITION:
                    self.to_recognition()
                elif i.route == RouterState.FINAL_REVIEW:
                    self.to_final_review()

                logger.debug("找到未完成的 Procession: route=%s", i.route)
                return i

        # 所有Procession都已完成
        self.to_finished()
        logger.debug("所有 Procession 已完成, 状态设置为 FINISHED")
        return Procession([AtomPlaceholder()], RouterState.FINISHED)

    def __repr__(self, style="pipe", ends="\n"):
        from tabulate import tabulate as tabu

        lst = [
            {
                "Type": "Router",
                "State": self.state,
                "Processions": list(map(lambda f: (f.name_), self.processions)),
                "Current Procession": "None" if not self.current_procession() else self.current_procession().name_,  # type: ignore
            },
        ]
        return str(tabu(tabular_data=lst, headers="keys", tablefmt=style)) + ends
