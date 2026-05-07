"""
全局上下文管理模块
以及基准路径
"""

import pathlib
from contextvars import ContextVar

from heurams.services.config import ConfigDict
from heurams.services.logger import get_logger

# 默认数据目录, 以包目录下的 data 为准
# 用户数据目录, 以运行目录下的 data 为准

rootdir: pathlib.Path = pathlib.Path(__file__).parent
"""包目录路径, 也就是 heurams 目录."""

workdir = pathlib.Path.cwd()
"""工作目录路径."""

logger = get_logger(__name__)
logger.debug(f"包目录: {rootdir}")
logger.debug(f"工作目录: {workdir}")

default_data = rootdir / "assets" / "data"
user_data = workdir / "data"
if not user_data.exists():
    logger.info("初始化数据目录: %s", user_data)
    import shutil

    shutil.copytree(default_data, user_data)
else:
    (workdir / "data" / "config").mkdir(parents=True, exist_ok=True)

config_var: ContextVar[ConfigDict] = ContextVar(
    "config_var",
    default=ConfigDict(workdir / "data" / "config"),
)
"""配置对象的全局引用对象."""


class ConfigContext:
    """
    功能完备的上下文管理器
    用于临时切换配置引用对象的作用域, 支持嵌套使用

    Example:
        >>> with ConfigContext(test_config):
        ...     get_daystamp()  # 使用 test_config
        >>> get_daystamp()  # 恢复原配置
    """

    def __init__(self, config_provider: ConfigDict):
        self.config_provider = config_provider
        self._token = None

    def __enter__(self):
        self._token = config_var.set(self.config_provider)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        config_var.reset(self._token)  # type: ignore
