# 移相器类定义

import heurams.kernel.particles as pt
from heurams.services.logger import get_logger

from .procession import Procession
from .states import PhaserState, ProcessionState

logger = get_logger(__name__)


class Phaser:
    """全局调度阶段管理器"""

    def __init__(self, atoms: list[pt.Atom]) -> None:
        logger.debug("Phaser.__init__: 原子数量=%d", len(atoms))
        new_atoms = list()
        old_atoms = list()
        self.state = PhaserState.UNSURE
        for i in atoms:
            if not i.registry["electron"].is_activated():
                new_atoms.append(i)
            else:
                old_atoms.append(i)
        logger.debug("新原子数量=%d, 旧原子数量=%d", len(new_atoms), len(old_atoms))
        self.processions = list()
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

    def current_procession(self):
        logger.debug("Phaser.current_procession 被调用")
        for i in self.processions:
            i: Procession
            if not i.state == ProcessionState.FINISHED:
                self.state = i.phase
                logger.debug("找到未完成的 Procession: phase=%s", i.phase)
                return i
        self.state = PhaserState.FINISHED
        logger.debug("所有 Procession 已完成, 状态设置为 FINISHED")
        return 0
