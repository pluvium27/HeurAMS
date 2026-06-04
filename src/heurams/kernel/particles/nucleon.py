from copy import deepcopy

from heurams.context import config_var
from heurams.services.logger import get_logger
from heurams.kernel.auxiliary.evalizor import Evalizer

logger = get_logger(__name__)


class Nucleon:
    """原子核: 带有运行时隔离的模板化只读材料元数据容器

    封装记忆单元的内容数据, 通过 Evalizer 模板系统展开 payload 和 common
    中的动态表达式. 创建后数据不可修改. 

    Attributes:
        ident: 记忆单元的唯一标识
        data: 展开后的内容字典 (只读)
    """

    def __init__(self, ident, payload, common):
        """初始化核子

        合并 payload 和 common, 通过 Evalizer 展开模板表达式. 
        展开失败时静默降级为原始数据. 

        Args:
            ident: 记忆单元标识
            payload: 记忆内容字典
            common: 通用元数据字典
        """
        self.ident = ident
        try:
            data_safe = deepcopy((payload | common))
            data_puz = deepcopy(data_safe["puzzles"])
            data_safe["puzzles"] = {}
            env = {
                "payload": data_safe,
                "default": config_var.get()["interface"]["puzzles"],
                "nucleon": data_safe,
            }
            self.evalizer = Evalizer(environment=env)
            data_safe = self.evalizer(deepcopy(data_safe))
            env = {
                "payload": data_safe,
                "default": config_var.get()["interface"]["puzzles"],
                "nucleon": data_safe,
            }
            self.evalizer = Evalizer(environment=env)
            data_puz = self.evalizer(deepcopy(data_puz))
            data_safe["puzzles"] = data_puz  # type: ignore
            self.data: dict = data_safe  # type: ignore
        except Exception:
            self.data = payload | common

    def __getitem__(self, key):
        """按字符串键获取数据

        Args:
            key: 字符串键名, "ident" 返回标识

        Returns:
            对应键的值

        Raises:
            AttributeError: 键类型不是字符串
        """
        if isinstance(key, str):
            if key == "ident":
                return self.ident
            return self.data[key]
        else:
            raise AttributeError(f"Nucleon 仅支持字符串键访问, 收到: {type(key).__name__}")

    def __setitem__(self, key, value):
        """禁止修改 (只读容器)

        Raises:
            AttributeError: 始终抛出
        """
        raise AttributeError("应为只读")

    def __delitem__(self, key):
        """禁止删除 (只读容器)

        Raises:
            AttributeError: 始终抛出
        """
        raise AttributeError("应为只读")

    def __iter__(self):
        """迭代数据字典的键"""
        return iter(self.data)

    def __contains__(self, key):
        """检查键是否存在于数据中"""
        return key in (self.data)

    def get(self, key, default=None):
        """安全获取数据值

        Args:
            key: 键名
            default: 键不存在时的默认值

        Returns:
            键对应的值或默认值
        """
        if key in self:
            return self[key]
        return default

    def __len__(self):
        """返回数据字典的长度"""
        return len(self.data)

    def __repr__(self):
        from pprint import pformat

        s = pformat(self.data, indent=4)
        return s

    @staticmethod
    def from_data(nucleonic_data: tuple):
        """从元组数据创建核子

        Args:
            nucleonic_data: 格式为 (ident, (payload, common)) 的元组

        Returns:
            Nucleon 实例
        """
        _data = nucleonic_data
        payload = _data[1][0]
        common = _data[1][1]
        ident = _data[0]  # TODO:实现eval
        return Nucleon(ident, payload, common)
