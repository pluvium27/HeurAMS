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
print(f"rootdir: {rootdir}")
logger = get_logger(__name__)
logger.debug(f"项目根目录: {rootdir}")
workdir = pathlib.Path.cwd()
print(f"workdir: {workdir}")
logger.debug(f"工作目录: {workdir}")
config_var: ContextVar[ConfigFile] = ContextVar(
    "config_var", default=ConfigFile(rootdir / "default" / "config" / "config.toml")
)
try:
    config_var: ContextVar[ConfigFile] = ContextVar(
        "config_var", default=ConfigFile(workdir / "config" / "config.toml")
    )  # 配置文件
    print("已加载自定义用户配置")
    logger.info("已加载自定义用户配置, 路径: %s", workdir / "config" / "config.toml")
except Exception as e:
    print("未能加载自定义用户配置")
    logger.warning("未能加载自定义用户配置, 错误: %s", e)

# runtime_var: ContextVar = ContextVar('runtime_var', default=dict()) # 运行时共享数据


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
