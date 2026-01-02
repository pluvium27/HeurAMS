from collections import UserList
from typing import Any, Iterator


class Lict(UserList):  # TODO: 优化同步(惰性同步), 当前性能为 O(n)
    """ "列典" 对象

    同时兼容字典和列表大多数 API, 两边数据同步的容器
    列表数据是 dictobj.items() 的格式
    支持根据字典或列表初始化
    限制要求:
    - 键名一定唯一, 且仅能为字符串
    - 值一定是引用对象
    - 不使用并发
    - 不在乎列表顺序语义(严格按键名字符序排列)和列表索引查找, 因此外部的 sort, index 等功能不可用
    - append 的元组中, 表示键名的元素不能重复, 否则会导致覆盖行为

    只有在 Python 3.7+ 中, forced_order 行为才能被取消.
    """

    def __init__(
        self,
        initlist: list | None = None,
        initdict: dict | None = None,
        forced_order=True,
    ):
        self.dicted_data = {}
        if initdict != None:
            initlist = list(initdict.items())
        super().__init__(initlist=initlist)
        self.forced_order = forced_order
        self._sync_based_on_list()
        if self.forced_order:
            self.data.sort()

    def _sync_based_on_dict(self):
        self.data = list(self.dicted_data.items())
        if self.forced_order:
            self.data.sort()

    def _sync_based_on_list(self):
        self.dicted_data = {}
        for i in self.data:
            self.dicted_data[i[0]] = i[1]

    def __iter__(self) -> Iterator:
        return self.data.__iter__()

    def __getitem__(self, i):
        if isinstance(i, str):
            return self.dicted_data[i]
        else:
            return super().__getitem__(i)

    def get_itemic_unit(self, ident):
        return (ident, self.dicted_data[ident])

    def __setitem__(self, i, item):
        if isinstance(i, str):
            self.dicted_data[i] = item
            self._sync_based_on_dict()
        else:
            if item != (item[0], item[1]):
                raise NotImplementedError
            super().__setitem__(i, item)
            self._sync_based_on_list()

    def __delitem__(self, i):
        if isinstance(i, str):
            del self.dicted_data[i]
            self._sync_based_on_dict()
        else:
            super().__delitem__(i)
            self._sync_based_on_list()

    def __contains__(self, item):
        return item in self.data or item in self.keys() or item in self.values()

    def append(self, item: Any) -> None:
        if item != (item[0], item[1]):
            raise NotImplementedError
        super().append(item)
        self._sync_based_on_list()
        if self.forced_order:
            self.data.sort()

    def append_new(self, item: Any):
        if item != (item[0], item[1]):
            raise NotImplementedError
        if item[0] not in self:
            super().append(item)
            self._sync_based_on_list()
            if self.forced_order:
                self.data.sort()

    def insert(self, i: int, item: Any) -> None:
        if item != (item[0], item[1]):  # 确保 item 是遵从限制的元组
            raise NotImplementedError
        super().insert(i, item)
        self._sync_based_on_list()
        if self.forced_order:
            self.data.sort()

    def pop(self, i: int = -1) -> Any:
        res = super().pop(i)
        self._sync_based_on_list()
        return res

    def remove(self, item: Any) -> None:
        if isinstance(item, str):
            item = (item, self.dicted_data[item])
        if item != (item[0], item[1]):
            raise NotImplementedError
        super().remove(item)
        self._sync_based_on_list()
        if self.forced_order:
            self.data.sort()

    def clear(self) -> None:
        super().clear()
        self._sync_based_on_list()

    def index(self):
        raise NotImplementedError

    def extend(self):
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError

    def reverse(self):
        raise NotImplementedError

    def keys(self):
        return self.dicted_data.keys()

    def values(self):
        return self.dicted_data.values()

    def items(self):
        return self.data

    def keys_equal_with(self, other):
        return self.key_equality(self, other)

    @classmethod
    def key_equality(cls, a, b):
        return a.keys() == b.keys()
