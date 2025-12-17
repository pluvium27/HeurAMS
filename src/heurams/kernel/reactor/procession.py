import heurams.kernel.particles as pt
from .states import PhaserState, ProcessionState
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class Procession:
    """队列: 标识单次记忆流程"""

    def __init__(self, atoms: list, phase: PhaserState, name: str = ""):
        logger.debug(
            "Procession.__init__: 原子数量=%d, phase=%s, name='%s'",
            len(atoms),
            phase.value,
            name,
        )
        self.atoms = atoms
        self.queue = atoms.copy()
        self.current_atom = atoms[0]
        self.cursor = 0
        self.name = name
        self.phase = phase
        self.state: ProcessionState = ProcessionState.RUNNING
        logger.debug("Procession 初始化完成, 队列长度=%d", len(self.queue))

    def forward(self, step=1):
        logger.debug("Procession.forward: step=%d, 当前 cursor=%d", step, self.cursor)
        self.cursor += step
        if self.cursor == len(self.queue):
            self.state = ProcessionState.FINISHED
            logger.debug("Procession 已完成")
        else:
            self.state = ProcessionState.RUNNING
        try:
            logger.debug("cursor 更新为: %d", self.cursor)
            self.current_atom = self.queue[self.cursor]
            logger.debug("当前原子更新为: %s", self.current_atom.ident)
            return 1  # 成功
        except IndexError as e:
            logger.debug("IndexError: %s", e)
            self.state = ProcessionState.FINISHED
            logger.debug("Procession 因索引错误而完成")
            return 0

    def append(self, atom=None):
        if atom == None:
            atom = self.current_atom
        logger.debug("Procession.append: atom=%s", atom.ident if atom else "None")
        if self.queue[len(self.queue) - 1] != atom or len(self) <= 1:
            self.queue.append(atom)
            logger.debug("原子已追加到队列, 新队列长度=%d", len(self.queue))
        else:
            logger.debug("原子未追加（重复或队列长度<=1）")

    def __len__(self):
        length = len(self.queue) - self.cursor
        logger.debug("Procession.__len__: 剩余长度=%d", length)
        return length

    def process(self):
        logger.debug("Procession.process: cursor=%d", self.cursor)
        return self.cursor

    def total_length(self):
        total = len(self.queue)
        logger.debug("Procession.total_length: %d", total)
        return total

    def is_empty(self):
        empty = len(self.queue)
        logger.debug("Procession.is_empty: %d", empty)
        return empty
