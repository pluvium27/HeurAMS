import heurams.services.timer as timer
from heurams.context import config_var
from heurams.kernel.algorithms import algorithms
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class Electron:
    """电子: 记忆分析元数据及算法"""

    def __init__(self, ident: str, algodata: dict = {}, algo_name: str = "supermemo2"):
        """初始化电子对象 (记忆数据)

        Args:
            ident: 算法的唯一标识符, 用于区分不同的算法实例, 使用 algodata[ident] 获取
            algodata: 算法数据字典, 包含算法的各项参数和设置
            algo: 使用的算法模块标识
        """
        logger.debug(
            "创建 Electron 实例, ident: '%s', algo_name: '%s'", ident, algo_name
        )
        self.algodata = algodata
        self.ident = ident
        self.algo = algorithms[algo_name]
        logger.debug("使用的算法类: %s", self.algo.__name__)

        if self.algo not in self.algodata.keys():
            self.algodata[self.algo.algo_name] = {}
            logger.debug("算法键 '%s' 不存在, 已创建空字典", self.algo)
        if not self.algodata[self.algo.algo_name]:
            logger.debug("算法数据为空, 使用默认值初始化")
            self._default_init(self.algo.defaults)
        else:
            logger.debug("算法数据已存在, 跳过默认初始化")
        logger.debug(
            "Electron 初始化完成, algodata keys: %s", list(self.algodata.keys())
        )

    def _default_init(self, defaults: dict):
        """默认初始化包装"""
        logger.debug(
            "Electron._default_init: 使用默认值, keys: %s", list(defaults.keys())
        )
        self.algodata[self.algo.algo_name] = defaults.copy()

    def activate(self):
        """激活此电子"""
        logger.debug("Electron.activate: 激活 ident='%s'", self.ident)
        self.algodata[self.algo.algo_name]["is_activated"] = 1
        self.algodata[self.algo.algo_name]["last_modify"] = timer.get_timestamp()
        logger.debug("电子已激活, is_activated=1")

    def modify(self, var: str, value):
        """修改 algodata[algo] 中子字典数据"""
        logger.debug("Electron.modify: var='%s', value=%s", var, value)
        if var in self.algodata[self.algo.algo_name]:
            self.algodata[self.algo.algo_name][var] = value
            self.algodata[self.algo.algo_name]["last_modify"] = timer.get_timestamp()
            logger.debug("变量 '%s' 已修改, 更新 last_modify", var)
        else:
            logger.warning("'%s' 非已知元数据字段", var)
            print(f"警告: '{var}' 非已知元数据字段")

    def is_due(self):
        """是否应该复习"""
        logger.debug("Electron.is_due: 检查 ident='%s'", self.ident)
        result = self.algo.is_due(self.algodata)
        logger.debug("is_due 结果: %s", result)
        return result and self.is_activated()

    def is_activated(self):
        result = self.algodata[self.algo.algo_name]["is_activated"]
        logger.debug("Electron.is_activated: ident='%s', 结果: %d", self.ident, result)
        return result

    def get_rate(self):
        "评价"
        try:
            logger.debug("Electron.rate: ident='%s'", self.ident)
            result = self.algo.rate(self.algodata)
            logger.debug("rate 结果: %s", result)
            return result
        except:
            return 0

    def nextdate(self) -> int:
        logger.debug("Electron.nextdate: ident='%s'", self.ident)
        result = self.algo.nextdate(self.algodata)
        logger.debug("nextdate 结果: %d", result)
        return result

    def revisor(self, quality: int = 5, is_new_activation: bool = False):
        """算法迭代决策机制实现

        Args:
            quality (int): 记忆保留率量化参数 (0-5)
            is_new_activation (bool): 是否为初次激活
        """
        logger.debug(
            "Electron.revisor: ident='%s', quality=%d, is_new_activation=%s",
            self.ident,
            quality,
            is_new_activation,
        )
        self.algo.revisor(self.algodata, quality, is_new_activation)
        logger.debug(
            "revisor 完成, 更新后的 algodata: %s", self.algodata.get(self.algo, {})
        )

    def __str__(self):
        return (
            f"记忆单元预览 \n"
            f"标识符: '{self.ident}' \n"
            f"算法: {self.algo} \n"
            f"易度系数: {self.algodata[self.algo.algo_name]['efactor']:.2f} \n"
            f"已经重复的次数: {self.algodata[self.algo.algo_name]['rept']} \n"
            f"下次间隔: {self.algodata[self.algo.algo_name]['interval']} 天 \n"
            f"下次复习日期时间戳: {self.algodata[self.algo.algo_name]['next_date']}"
        )

    def __eq__(self, other):
        if self.ident == other.ident:
            return True
        return False

    def __hash__(self):
        return hash(self.ident)

    def __getitem__(self, key):
        if key == "ident":
            return self.ident
        if key in self.algodata[self.algo.algo_name]:
            return self.algodata[self.algo.algo_name][key]
        else:
            raise KeyError(f"键 '{key}' 未在 algodata[self.algo] 中")

    def __setitem__(self, key, value):
        if key == "ident":
            raise AttributeError("ident 应为只读")
        self.algodata[self.algo.algo_name][key] = value
        self.algodata[self.algo.algo_name]["last_modify"] = timer.get_timestamp()

    def __len__(self):
        """仅返回当前算法的配置数量"""
        return len(self.algodata[self.algo.algo_name])

    @staticmethod
    def placeholder():
        """生成一个电子占位符"""
        return Electron("电子对象样例内容", {})
