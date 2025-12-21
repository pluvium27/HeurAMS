# 版本控制集成服务
from heurams.services.logger import get_logger

logger = get_logger(__name__)

ver = "0.4.3"
stage = "prototype"
codename = "fledge"  # 雏鸟, 0.4.x 版本

logger.info("HeurAMS 版本: %s (%s), 阶段: %s", ver, codename, stage)
