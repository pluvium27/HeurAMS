import json
import pathlib
import typing
from typing import TypedDict

import toml

from heurams.context import config_var
from heurams.services.logger import get_logger

from .electron import Electron
from .nucleon import Nucleon

logger = get_logger(__name__)


class AtomRegister_runtime(TypedDict):
    locked: bool  # 只读锁定标识符
    min_rate: int  # 最低评分
    new_activation: bool  # 新激活

class AtomRegister(TypedDict):
    nucleon: Nucleon
    electron: Electron
    runtime: AtomRegister_runtime

class Atom:
    """
    统一处理一系列对象的所有信息与持久化:
        关联电子 (算法数据)
        关联核子 (内容数据)
        关联轨道 (策略数据)
        以及关联路径
    """

    default_runtime = {
        "locked": False,
        "min_rate": 0x3F3F3F3F,
        "new_activation": False,
    }

    def __init__(self, nucleon_obj = None, electron_obj = None, orbital_obj = None):
        self.ident = nucleon_obj["ident"] # type: ignore
        self.registry: AtomRegister = {  # type: ignore
            "ident": nucleon_obj["ident"], # type: ignore
            "nucleon": nucleon_obj,
            "electron": electron_obj,
            "orbital": orbital_obj,
            "runtime": dict(),
        }
        self.init_runtime()
        if self.registry["electron"].is_activated() == 0:
            self.registry["runtime"]["new_activation"] = True

    def init_runtime(self):
        self.registry['runtime'] = AtomRegister_runtime(**self.default_runtime)

    def minimize(self, rating):
        """效果等同于 self.registry['runtime']['min_rate'] = min(rating, self.registry['runtime']['min_rate'])

        Args:
            rating (int): 评分
        """
        self.registry["runtime"]["min_rate"] = min(
            rating, self.registry["runtime"]["min_rate"]
        )

    def lock(self, locked=-1):
        logger.debug(f"锁定参数 {locked}")
        """锁定, 效果等同于 self.registry['runtime']['locked'] = locked 或者返回是否锁定"""
        if locked == 1:
            self.registry["runtime"]["locked"] = True
            return 1
        elif locked == 0:
            self.registry["runtime"]["locked"] = False
            return 1
        elif locked == -1:
            return self.registry["runtime"]["locked"]
        return 0

    def revise(self):
        """执行最终评分
        PuzzleWidget 的 handler 除了测试, 严禁直接执行 Electron 的 revisor 函数, 否则造成逻辑混乱
        """
        if self.registry["runtime"]["locked"]:
            logger.debug(f"允许总评分: {self.registry['runtime']['min_rate']}")
            self.registry["electron"].revisor(
                self.registry["runtime"]["min_rate"],
                is_new_activation=self.registry["runtime"]["new_activation"],
            )
        else:
            logger.debug("禁止总评分")

    def __getitem__(self, key):
        return self.registry[key]

    def __setitem__(self, key, value):
        if key == "ident":
            raise AttributeError("应为只读")
        self.registry[key] = value