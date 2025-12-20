from heurams.services.logger import get_logger

logger = get_logger(__name__)


class Nucleon:
    """原子核: 材料元数据"""

    def __init__(self, ident: str, payload: dict, metadata: dict = {}):
        """初始化原子核 (记忆内容)

        Args:
            ident: 唯一标识符
            payload: 记忆内容信息
            metadata: 可选元数据信息
        """
        logger.debug(
            "创建 Nucleon 实例, ident: '%s', payload keys: %s, metadata keys: %s",
            ident,
            list(payload.keys()) if payload else [],
            list(metadata.keys()) if metadata else [],
        )
        self.metadata = metadata
        self.payload = payload
        self.ident = ident
        logger.debug("Nucleon 初始化完成")

    def __getitem__(self, key):
        logger.debug("Nucleon.__getitem__: key='%s'", key)
        if key == "ident":
            logger.debug("返回 ident: '%s'", self.ident)
            return self.ident
        if key in self.payload:
            value = self.payload[key]
            logger.debug(
                "返回 payload['%s'], value type: %s", key, type(value).__name__
            )
            return value
        else:
            logger.error("键 '%s' 未在 payload 中找到", key)
            raise KeyError(f"Key '{key}' not found in payload.")

    def __iter__(self):
        yield from self.payload.keys()

    def __len__(self):
        return len(self.payload)

    def __hash__(self):
        return hash(self.ident)

    @staticmethod
    def placeholder():
        """生成一个占位原子核"""
        logger.debug("创建 Nucleon 占位符")
        return Nucleon("核子对象样例内容", {})