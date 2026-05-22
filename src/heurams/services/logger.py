"""日志服务模块

基于 logging 库, 提供统一日志记录功能
"""

import logging
import logging.handlers
import pathlib
from typing import Optional, Union

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FILE = pathlib.Path("heurams.log")
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 全局logger缓存
_loggers = {}

def setup_logging(
    log_file: Union[str, pathlib.Path] = DEFAULT_LOG_FILE,
    log_level: int = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    max_bytes: int = 16 * 1024 * 1024,  # 16MB
    backup_count: int = 5,
) -> None:
    """
    设置全局日志服务

    Args:
        log_file: 日志文件路径
        log_level: 日志级别 (logging.DEBUG, logging.INFO等)
        log_format: 日志格式字符串
        date_format: 日期时间格式
        max_bytes: 单个日志文件最大字节数
        backup_count: 备份文件数量
    """
    # 确保日志目录存在
    log_path = pathlib.Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建formatter
    formatter = logging.Formatter(log_format, date_format)

    # 创建文件 handler (RotatingFileHandler)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # 这里改为 WARNING

    # 移除所有现有handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建 heurams logger 并单独设置 DEBUG 级别
    app_logger = logging.getLogger("heurams")
    app_logger.setLevel(log_level)  # 保持DEBUG级别
    app_logger.addHandler(file_handler)

    # 禁止传播到 root logger, 避免双重记录
    app_logger.propagate = False

    # 记录日志系统初始化
    app_logger.debug("HeurAMS logger inited, path: %s", log_path.resolve())


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取指定名称的 logger

    Args:
        name: logger名称, 通常使用模块名(__name__)
              如果为None, 返回 root logger

    Returns:
        logging.Logger 实例
    """
    if name is None:
        return logging.getLogger()

    # 确保使用 heurams 作为前缀, 继承应用logger的配置
    if not name.startswith("heurams") and name != "":
        logger_name = f"heurams.{name}"
    else:
        logger_name = name

    # 缓存 logger 以提高性能, 以模块为单位的单例
    if logger_name not in _loggers:
        logger = logging.getLogger(logger_name)
        _loggers[logger_name] = logger

    return _loggers[logger_name]

# 初始化日志系统
setup_logging()