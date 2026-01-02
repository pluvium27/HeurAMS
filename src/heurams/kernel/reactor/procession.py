import heurams.kernel.particles as pt
from heurams.services.logger import get_logger
from transitions import Machine

from .states import PhaserState, ProcessionState

logger = get_logger(__name__)


class Procession(Machine):
    """队列: 标识单次记忆流程"""

    def __init__(self, atoms: list, phase_state: PhaserState, name: str = ""):
        logger.debug(
            "Procession.__init__: 原子数量=%d, phase=%s, name='%s'",
            len(atoms),
            phase_state.value,
            name,
        )
        
        # 初始化原子队列
        self.atoms = atoms
        self.queue = atoms.copy()
        self.current_atom = atoms[0] if atoms else None
        self.cursor = 0
        self.name = name
        self.phase = phase_state
        
        # 设置transitions状态机
        states = [{'name': ProcessionState.RUNNING.value, 'on_enter': 'on_running'},
                  {'name': ProcessionState.FINISHED.value, 'on_enter': 'on_finished'}]
        
        transitions = [
            {'trigger': 'finish', 'source': ProcessionState.RUNNING.value, 'dest': ProcessionState.FINISHED.value},
            {'trigger': 'restart', 'source': ProcessionState.FINISHED.value, 'dest': ProcessionState.RUNNING.value}
        ]
        
        Machine.__init__(self, states=states, transitions=transitions, 
                        initial=ProcessionState.RUNNING.value)
        
        logger.debug("Procession 初始化完成, 队列长度=%d", len(self.queue))

    def on_running(self):
        """进入RUNNING状态时的回调"""
        logger.debug("Procession 进入 RUNNING 状态")

    def on_finished(self):
        """进入FINISHED状态时的回调"""
        logger.debug("Procession 进入 FINISHED 状态")

    def forward(self, step=1):
        logger.debug("Procession.forward: step=%d, 当前 cursor=%d", step, self.cursor)
        self.cursor += step
        
        if self.cursor >= len(self.queue):
            if self.state != ProcessionState.FINISHED.value:
                self.finish()  # 触发状态转换
            logger.debug("Procession 已完成")
        else:
            if self.state != ProcessionState.RUNNING.value:
                self.restart()  # 确保在RUNNING状态
            self.current_atom = self.queue[self.cursor]
            logger.debug("cursor 更新为: %d", self.cursor)
            logger.debug("当前原子更新为: %s", self.current_atom.ident if self.current_atom else "None")
            return 1  # 成功
        
        return 0

    def append(self, atom=None):
        if atom is None:
            atom = self.current_atom
        logger.debug("Procession.append: atom=%s", atom.ident if atom else "None")
        
        if not self.queue or self.queue[-1] != atom or len(self) <= 1:
            self.queue.append(atom)
            logger.debug("原子已追加到队列, 新队列长度=%d", len(self.queue))
        else:
            logger.debug("原子未追加(重复或队列长度<=1)")

    def __len__(self):
        if not self.queue:
            return 0
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
        empty = len(self.queue) == 0
        logger.debug("Procession.is_empty: %s", empty)
        return empty
    
    @property
    def state(self):
        """获取当前状态值"""
        return self.get_model_state(self)
    
    @state.setter
    def state(self, value):
        """设置状态值"""
        if value == ProcessionState.RUNNING.value:
            self.restart()
        elif value == ProcessionState.FINISHED.value:
            self.finish()