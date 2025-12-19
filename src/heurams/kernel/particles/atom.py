from .electron import Electron
from .nucleon import Nucleon
from .orbital import Orbital
from typing import TypedDict
import pathlib
import typing
import toml
import json
import bidict
from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class AtomRegister_runtime(TypedDict):
    locked: bool  # 只读锁定标识符
    min_rate: int  # 最低评分
    newact: bool  # 新激活


class AtomRegister(TypedDict):
    nucleon: Nucleon
    nucleon_path: pathlib.Path
    nucleon_fmt: str
    electron: Electron
    electron_path: pathlib.Path
    electron_fmt: str
    orbital: Orbital
    orbital_path: pathlib.Path
    orbital_fmt: str
    runtime: AtomRegister_runtime


class Atom:
    """
    统一处理一系列对象的所有信息与持久化:
        关联电子 (算法数据)
        关联核子 (内容数据)
        关联轨道 (策略数据)
        以及关联路径
    """

    def __init__(self, ident=""):
        logger.debug("创建 Atom 实例, ident: '%s'", ident)
        self.ident = ident
        atom_registry[ident] = self
        logger.debug("Atom 已注册到全局注册表, 当前注册表大小: %d", len(atom_registry))
        # self.is_evaled = False
        self.registry: AtomRegister = {  # type: ignore
            "nucleon": None,
            "nucleon_path": None,
            "nucleon_fmt": "toml",
            "electron": None,
            "electron_path": None,
            "electron_fmt": "json",
            "orbital": None,
            "orbital_path": None,  # 允许设置为 None, 此时使用 nucleon 文件内的推荐配置
            "orbital_fmt": "toml",
            "runtime": {"locked": False, "min_rate": 0x3F3F3F3F, "newact": False},
        }
        self.do_eval()
        logger.debug("Atom 初始化完成")

    def link(self, key, value):
        logger.debug("Atom.link: key='%s', value type: %s", key, type(value).__name__)
        if key in self.registry.keys():
            self.registry[key] = value
            logger.debug("键 '%s' 已链接, 触发 do_eval", key)
            self.do_eval()
            if key == "electron":
                if self.registry["electron"].is_activated() == 0:
                    self.registry["runtime"]["newact"] = True
        else:
            logger.error("尝试链接不受支持的键: '%s'", key)
            raise ValueError("不受支持的原子元数据链接操作")

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
                is_new_activation=self.registry["runtime"]["newact"],
            )
        else:
            logger.debug("禁止总评分")

    def do_eval(self):
        """
        执行并以结果替换当前单元的所有 eval 语句
        TODO: 带有限制的 eval, 异步/多线程执行避免堵塞
        """
        logger.debug("Atom.do_eval 开始")

        # eval 环境设置
        def eval_with_env(s: str):
            # 初始化默认值
            nucleon = self.registry["nucleon"]
            default = {}
            metadata = {}
            try:
                default = config_var.get()["puzzles"]
                metadata = nucleon.metadata
            except Exception:
                # 如果无法获取配置或元数据, 使用空字典
                logger.debug("无法获取配置或元数据, 使用空字典")
                pass
            try:
                eval_value = eval(s)
                if isinstance(eval_value, (list, dict)):
                    ret = eval_value
                else:
                    ret = str(eval_value)
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

        # 如果 nucleon 存在且有 do_eval 方法, 调用它
        nucleon = self.registry["nucleon"]
        if nucleon is not None and hasattr(nucleon, "do_eval"):
            nucleon.do_eval()
            logger.debug("已调用 nucleon.do_eval")

        # 如果 electron 存在且其 algodata 包含 eval 字符串, 遍历它
        electron = self.registry["electron"]
        if electron is not None and hasattr(electron, "algodata"):
            traverse(electron.algodata, eval_with_env)
            logger.debug("已处理 electron algodata eval")

        # 如果 orbital 存在且是字典, 遍历它
        orbital = self.registry["orbital"]
        if orbital is not None and isinstance(orbital, dict):
            traverse(orbital, eval_with_env)
            logger.debug("orbital eval 完成")

        logger.debug("Atom.do_eval 完成")

    def persist(self, key):
        logger.debug("Atom.persist: key='%s'", key)
        path: pathlib.Path | None = self.registry[key + "_path"]
        if isinstance(path, pathlib.Path):
            path = typing.cast(pathlib.Path, path)
            logger.debug("持久化路径: %s, 格式: %s", path, self.registry[key + "_fmt"])
            path.parent.mkdir(parents=True, exist_ok=True)
            if self.registry[key + "_fmt"] == "toml":
                with open(path, "r+") as f:
                    f.seek(0)
                    f.truncate()
                    toml.dump(self.registry[key], f)
                logger.debug("TOML 数据已保存到: %s", path)
            elif self.registry[key + "_fmt"] == "json":
                with open(path, "r+") as f:
                    origin = json.load(f)
                    f.seek(0)
                    f.truncate()
                    origin[self.ident] = self.registry[key].algodata
                    json.dump(origin, f, indent=2, ensure_ascii=False)
                logger.debug("JSON 数据已保存到: %s", path)
            else:
                logger.error("不受支持的持久化格式: %s", self.registry[key + "_fmt"])
                raise KeyError("不受支持的持久化格式")
        else:
            logger.error("路径未初始化: %s_path", key)
            raise TypeError("对未初始化的路径对象操作")

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

    @staticmethod
    def placeholder():
        return (Electron.placeholder(), Nucleon.placeholder(), {})


atom_registry: bidict.bidict[str, Atom] = bidict.bidict()
