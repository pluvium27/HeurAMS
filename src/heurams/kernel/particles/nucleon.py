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

    def do_eval(self):
        """
        执行并以结果替换当前单元的所有 eval 语句
        TODO: 带有限制的 eval, 异步/多线程执行避免堵塞
        """
        logger.debug("Nucleon.do_eval 开始")

        # eval 环境设置
        def eval_with_env(s: str):
            try:
                nucleon = self
                eval_value = eval(s)
                if isinstance(eval_value, (int, float)):
                    ret = str(eval_value)
                else:
                    ret = eval_value
                logger.debug(
                    "eval 执行成功: '%s' -> '%s'",
                    s,
                    str(ret)[:50] + "..." if len(ret) > 50 else ret,
                )
            except Exception as e:
                ret = f"此 eval 实例发生错误: {e}"
                logger.warning("eval 执行错误: '%s' -> %s", s, e)
            return ret

        def traverse(data, modifier):
            if isinstance(data, dict):
                for key, value in data.items():
                    data[key] = traverse(value, modifier)
                return data
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    data[i] = traverse(item, modifier)
                return data
            elif isinstance(data, tuple):
                return tuple(traverse(item, modifier) for item in data)
            else:
                if isinstance(data, str):
                    if data.startswith("eval:"):
                        logger.debug("发现 eval 表达式: '%s'", data[5:])
                        return modifier(data[5:])
                return data

        traverse(self.payload, eval_with_env)
        traverse(self.metadata, eval_with_env)
        logger.debug("Nucleon.do_eval 完成")

    @staticmethod
    def placeholder():
        """生成一个占位原子核"""
        logger.debug("创建 Nucleon 占位符")
        return Nucleon("核子对象样例内容", {})
