import json
import pathlib
import typing
from typing import TypedDict

import bidict
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
        self.registry: AtomRegister = {  # type: ignore
            "ident": nucleon_obj["ident"], # type: ignore
            "nucleon": nucleon_obj,
            "electron": electron_obj,
            "orbital": orbital_obj,
            "runtime": dict(),
        }
        if self.registry["electron"].is_activated() == 0:
            self.registry["runtime"]["new_activation"] = True

    def init_runtime(self):
        self.registry['runtime'] = AtomRegister_runtime(**self.default_runtime)
    
    def do_eval(self):
        """
        执行并以结果替换当前单元的所有 eval 语句
        TODO: 带有限制的 eval, 异步/多线程执行避免堵塞
        """
        # eval 环境设置
        def eval_with_env(s: str):
            default = config_var.get()["puzzles"]
            nucleon = self.registry["nucleon"]
            payload = nucleon # 兼容历史遗留问题
            metadata = nucleon # 兼容历史遗留问题
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

        try:
            traverse(self.registry["nucleon"].payload, eval_with_env)
            traverse(self.registry["nucleon"].metadata, eval_with_env)
            traverse(self.registry["orbital"], eval_with_env)
        except Exception as e:
            ret = f"此 eval 实例发生错误: {e}"
            logger.warning(ret)
        logger.debug("EVAL 完成")

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
        logger.debug("Atom.__getitem__: key='%s'", key)
        if key in self.registry:
            value = self.registry[key]
            logger.debug("返回 value type: %s", type(value).__name__)
            return value
        logger.error("不支持的键: '%s'", key)
        raise KeyError(f"不支持的键: {key}")

    def __setitem__(self, key, value):
        logger.debug(
            "Atom.__setitem__: key='%s', value type: %s", key, type(value).__name__
        )
        if key in self.registry:
            self.registry[key] = value
            logger.debug("键 '%s' 已设置", key)
        else:
            logger.error("不支持的键: '%s'", key)
            raise KeyError(f"不支持的键: {key}")

