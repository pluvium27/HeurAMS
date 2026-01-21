"""
全局上下文管理模块
以及基准路径
"""

import pathlib
from contextvars import ContextVar

from heurams.services.config import ConfigFile
from heurams.services.logger import get_logger

# 默认配置文件路径规定: 以包目录为准
# 用户配置文件路径规定: 以运行目录为准
# 数据文件路径规定: 以运行目录为准

rootdir = pathlib.Path(__file__).parent
workdir = pathlib.Path.cwd()
#print(f"项目根目录: {rootdir}")
#print(f"工作目录: {workdir}")
logger = get_logger(__name__)
logger.debug(f"项目根目录: {rootdir}")
logger.debug(f"工作目录: {workdir}")

(workdir / "data" / "config").mkdir(parents=True, exist_ok=True)

config_var: ContextVar[ConfigFile] = ContextVar(
    "config_var",
    default=ConfigFile(workdir / "data" / "config" / "config.toml"),
)

class ConfigContext:
    """
    功能完备的上下文管理器
    用于临时切换配置的作用域, 支持嵌套使用

    Example:
        >>> with ConfigContext(test_config):
        ...     get_daystamp()  # 使用 test_config
        >>> get_daystamp()  # 恢复原配置
    """

    def __init__(self, config_provider: ConfigFile):
        self.config_provider = config_provider
        self._token = None

    def __enter__(self):
        self._token = config_var.set(self.config_provider)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        config_var.reset(self._token)  # type: ignore
