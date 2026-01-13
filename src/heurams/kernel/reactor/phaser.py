from transitions import Machine

import heurams.kernel.particles as pt
from heurams.kernel.particles.placeholders import AtomPlaceholder
from heurams.services.logger import get_logger

from .procession import Procession
from .states import PhaserState, ProcessionState

logger = get_logger(__name__)


class Phaser(Machine):
    """全局调度阶段管理器"""

    def __init__(self, atoms: list[pt.Atom]) -> None:
        logger.debug("Phaser.__init__: 原子数量=%d", len(atoms))

        self.atoms = atoms
        new_atoms = list()
        old_atoms = list()

        for i in atoms:
            if not i.registry["electron"].is_activated():
                new_atoms.append(i)
            else:
                old_atoms.append(i)

        logger.debug("新原子数量=%d, 旧原子数量=%d", len(new_atoms), len(old_atoms))

        self.processions = list()
        # TODO: 改进为基于配置文件的可选复习阶段
        if len(old_atoms):
            self.processions.append(
                Procession(old_atoms, PhaserState.QUICK_REVIEW, "初始复习")
            )
            logger.debug("创建初始复习 Procession")

        if len(new_atoms):
            self.processions.append(
                Procession(new_atoms, PhaserState.RECOGNITION, "新记忆")
            )
            logger.debug("创建新记忆 Procession")

        self.processions.append(Procession(atoms, PhaserState.FINAL_REVIEW, "总体复习"))
        logger.debug("创建总体复习 Procession")
        logger.debug("Phaser 初始化完成, processions 数量=%d", len(self.processions))

        # 设置transitions状态机
        states = [
            {"name": PhaserState.UNSURE.value, "on_enter": "on_unsure"},
            {"name": PhaserState.QUICK_REVIEW.value, "on_enter": "on_quick_review"},
            {"name": PhaserState.RECOGNITION.value, "on_enter": "on_recognition"},
            {"name": PhaserState.FINAL_REVIEW.value, "on_enter": "on_final_review"},
            {"name": PhaserState.FINISHED.value, "on_enter": "on_finished"},
        ]

        transitions = [
            {"trigger": "to_unsure", "source": "*", "dest": PhaserState.UNSURE.value},
            {
                "trigger": "to_quick_review",
                "source": "*",
                "dest": PhaserState.QUICK_REVIEW.value,
            },
            {
                "trigger": "to_recognition",
                "source": "*",
                "dest": PhaserState.RECOGNITION.value,
            },
            {
                "trigger": "to_final_review",
                "source": "*",
                "dest": PhaserState.FINAL_REVIEW.value,
            },
            {
                "trigger": "to_finished",
                "source": "*",
                "dest": PhaserState.FINISHED.value,
            },
        ]

        Machine.__init__(
            self,
            states=states,
            transitions=transitions,
            initial=PhaserState.UNSURE.value,
        )

        self.to_unsure()

    def on_unsure(self):
        """进入UNSURE状态时的回调"""
        logger.debug("Phaser 进入 UNSURE 状态")

    def on_quick_review(self):
        """进入QUICK_REVIEW状态时的回调"""
        logger.debug("Phaser 进入 QUICK_REVIEW 状态")

    def on_recognition(self):
        """进入RECOGNITION状态时的回调"""
        logger.debug("Phaser 进入 RECOGNITION 状态")

    def on_final_review(self):
        """进入FINAL_REVIEW状态时的回调"""
        logger.debug("Phaser 进入 FINAL_REVIEW 状态")

    def on_finished(self):
        """进入FINISHED状态时的回调"""
        for i in self.atoms:
            i.lock(1)
            i.revise()
        logger.debug("Phaser 进入 FINISHED 状态")

    def current_procession(self):
        logger.debug("Phaser.current_procession 被调用")
        for i in self.processions:
            i: Procession
            if i.state != ProcessionState.FINISHED.value:
                # if i.phase == PhaserState.UNSURE: 此判断是不必要的 因为没有这种 Procession
                if i.phase == PhaserState.QUICK_REVIEW:
                    self.to_quick_review()
                elif i.phase == PhaserState.RECOGNITION:
                    self.to_recognition()
                elif i.phase == PhaserState.FINAL_REVIEW:
                    self.to_final_review()

                logger.debug("找到未完成的 Procession: phase=%s", i.phase)
                return i

        # 所有Procession都已完成
        self.to_finished()
        logger.debug("所有 Procession 已完成, 状态设置为 FINISHED")
        return Procession([AtomPlaceholder()], PhaserState.FINISHED)

    def __repr__(self, style="pipe", ends="\n"):
        from tabulate import tabulate as tabu

        from heurams.services.textproc import truncate

        lst = [
            {
                "Type": "Phaser",
                "State": self.state,
                "Processions": list(map(lambda f: (f.name_), self.processions)),
                "Current Procession": "None" if not self.current_procession() else self.current_procession().name_,  # type: ignore
            },
        ]
        return str(tabu(tabular_data=lst, headers="keys", tablefmt=style)) + ends
