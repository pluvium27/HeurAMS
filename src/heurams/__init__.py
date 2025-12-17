print("欢迎使用 HeurAMS 及其组件!")

# 补充日志记录
from heurams.services.logger import get_logger

logger = get_logger(__name__)
logger.info("欢迎使用 HeurAMS 及其组件!")
