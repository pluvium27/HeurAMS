# 版本控制集成服务
from heurams.services.logger import get_logger

logger = get_logger(__name__)

ver = "0.5.0"
stage = "rc.1"
codename = "fulcrum"
codename_cn = "支点"

logger.info("HeurAMS 版本: %s (%s), 阶段: %s", ver, codename, stage)
