"""识别谜题模块"""

from heurams.services.logger import get_logger

from .base import BasePuzzle

logger = get_logger(__name__)


class RecognitionPuzzle(BasePuzzle):
    """识别型谜题

    展示内容供用户识别确认, 无需主动回忆. 
    常用于复习流程的最后阶段 (retronly 回溯模式). 
    """

    def __init__(self) -> None:
        super().__init__()

    def refresh(self):
        """刷新谜题 (识别型无需生成内容)"""
