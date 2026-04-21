"""
HeurAMS 日志服务模块
基于Python标准logging库, 提供统一的日志记录功能
"""

import logging
import logging.handlers
import pathlib
from typing import Optional, Union

# 默认配置
DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FILE = pathlib.Path("heurams.log")
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 全局logger缓存
_loggers = {}


def setup_logging(
    log_file: Union[str, pathlib.Path] = DEFAULT_LOG_FILE,
    log_level: int = DEFAULT_LOG_LEVEL,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    配置全局日志系统

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

    # 创建文件handler(使用RotatingFileHandler防止日志过大)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # 配置root logger - 设置为 WARNING 级别(只记录重要信息)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # 这里改为 WARNING

    # 移除所有现有handler
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建自己的应用logger(单独设置DEBUG级别)
    app_logger = logging.getLogger("heurams")
    app_logger.setLevel(log_level)  # 保持DEBUG级别
    app_logger.addHandler(file_handler)

    # 禁止传播到root logger, 避免双重记录
    app_logger.propagate = False

    # 设置第三方库的日志级别为WARNING, 避免调试信息干扰
    third_party_loggers = [
        "markdown_it",
        "markdown_it.rules_block",
        "markdown_it.rules_core",
        "markdown_it.rules_inline",
        "asyncio",
    ]

    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # 记录日志系统初始化
    app_logger.info("日志系统已初始化, 日志文件: %s", log_path)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取指定名称的logger

    Args:
        name: logger名称, 通常使用模块名(__name__)
              如果为None, 返回root logger

    Returns:
        logging.Logger实例
    """
    if name is None:
        return logging.getLogger()

    # 确保使用 heurams 作为前缀, 继承应用logger的配置
    if not name.startswith("heurams") and name != "":
        logger_name = f"heurams.{name}"
    else:
        logger_name = name

    # 缓存logger以提高性能
    if logger_name not in _loggers:
        logger = logging.getLogger(logger_name)
        _loggers[logger_name] = logger

    return _loggers[logger_name]


# 便捷函数
def debug(msg: str, *args, **kwargs) -> None:
    """DEBUG级别日志"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """INFO级别日志"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """WARNING级别日志"""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """ERROR级别日志"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """CRITICAL级别日志"""
    get_logger().critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """记录异常信息 (ERROR级别)"""
    get_logger().exception(msg, *args, **kwargs)


# 初始化日志系统(硬编码配置)
setup_logging()


# 模块级别的logger实例
logger = get_logger(__name__)
logger.info("HeurAMS日志服务模块已加载")
