from copy import deepcopy
from typing import TypedDict

import heurams.kernel.algorithms as algolib
import heurams.services.timer as timer
from heurams.kernel.algorithms import algorithms
from heurams.services.logger import get_logger
from heurams.context import config_var

logger = get_logger(__name__)


class Electron:
    """电子: 单算法支持的记忆数据包装"""

    def __init__(self, ident: str, algodata: dict = {}, algo_name: str = ""):
        """初始化电子对象 (记忆数据)

        Args:
            ident: 算法的唯一标识符, 用于区分不同的算法实例, 使用 algodata[ident] 获取
            algodata: 算法数据字典引用, 包含算法的各项参数和设置
            algo_name: 使用的算法模块标识
        """
        if algo_name == "":
            algo_name = "SM-2"
        self.algodata = algodata
        self.ident = ident
        self.algoname = algo_name
        self.algo: algolib.BaseAlgorithm = algorithms[algo_name]

        if not self.algo.check_integrity(self.algodata):
            self.algodata[self.algo.algo_name] = deepcopy(self.algo.defaults)

    def __repr__(self):
        from pprint import pformat

        s = pformat(self.algodata, indent=4)
        return s

    def activate(self):
        """激活此电子"""
        self.algodata[self.algo.algo_name]["is_activated"] = 1
        self.algodata[self.algo.algo_name]["last_modify"] = timer.get_timestamp()

    def modify(self, key, value):
        """修改 algodata[algo] 中子字典数据"""
        if key in self.algodata[self.algo.algo_name]:
            self.algodata[self.algo.algo_name][key] = value
            self.algodata[self.algo.algo_name]["last_modify"] = timer.get_timestamp()
        else:
            raise AttributeError("不存在的子键")

    def is_due(self):
        """是否应该复习"""
        result = self.algo.is_due(self.algodata)
        return result and self.is_activated()

    def rept(self, real_rept=False):
        if real_rept:
            return self.algodata[self.algo.algo_name]["real_rept"]
        return self.algodata[self.algo.algo_name]["rept"]

    def is_activated(self):
        result = self.algodata[self.algo.algo_name]["is_activated"]
        return result

    def last_modify(self):
        result = self.algodata[self.algo.algo_name]["last_modify"]
        return result

    def get_rating(self):
        try:
            result = self.algo.get_rating(self.algodata)
            return result
        except:
            return 0

    def nextdate(self) -> int:
        result = self.algo.nextdate(self.algodata)
        return result

    def lastdate(self) -> int:
        result = self.algodata[self.algo.algo_name]["lastdate"]
        return result

    def revisor(self, quality: int = 5, is_new_activation: bool = False):
        """算法迭代决策机制实现

        Args:
            quality (int): 记忆保留率量化参数 (0-5)
            is_new_activation (bool): 是否为初次激活
        """
        self.algo.revisor(self.algodata, quality, is_new_activation)

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
    def from_data(electronic_data: tuple, algo_name: str = ""):
        _data = electronic_data
        ident = _data[0]
        algodata = _data[1]
        ident = ident
        return Electron(ident, algodata, algo_name)
