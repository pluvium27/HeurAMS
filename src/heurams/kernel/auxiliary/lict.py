from collections.abc import MutableSequence
from typing import Any, Iterator, Optional


class Lict(MutableSequence):
    """ "列典" 对象

    同时兼容字典和列表大多数 API, 两边数据同步的容器, 性能与 list/dict 大体相当
    列表数据是 dictobj.items() 的格式
    支持根据字典或列表初始化
    限制要求:
    - 键名一定唯一, 且仅能为字符串
    - append 的元组中, 表示键名的元素不能重复, 否则会导致覆盖行为

    """

    def __init__(
        self,
        initlist: Optional[list] = None,
        initdict: Optional[dict] = None,
        forced_order: bool = False,
    ):
        self._dict = {}
        self._list = []
        self._dict_dirty = False
        self._list_dirty = False
        self.forced_order = forced_order

        if initdict:  # initdict 更优先
            self._dict = initdict.copy()
            self._list_dirty = True
        elif initlist:
            self._list = initlist.copy()
            self._dict_dirty = True

        self._sync_if_needed()

    def _sync_if_needed(self):
        """只在需要时同步"""
        if self._dict_dirty:
            self._dict = {k: v for k, v in self._list}
            if self.forced_order:
                self._list.sort()
            self._dict_dirty = False

        if self._list_dirty:
            self._list = list(self._dict.items())
            if self.forced_order:
                self._list.sort()
            self._list_dirty = False

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._dict[key]
        else:
            self._sync_if_needed()
            return self._list[key]

    def __setitem__(self, key, value):
        """传入键值对时等同于操作字典, 传入索引+元组时等用于替换某索引的列表值为新元组"""
        if isinstance(key, str):
            self._dict[key] = value
            self._list_dirty = True
        else:
            if value != (value[0], value[1]):
                raise NotImplementedError
            self._sync_if_needed()
            old_key = self._list[key][0]
            self._dict.pop(old_key)
            self._list[key] = value
            self._dict[value[0]] = value[1]  # 避免全量同步

    def __delitem__(self, key):
        if isinstance(key, str):  # 字符串键
            del self._dict[key]
            self._list_dirty = True
        else:  # 数字索引
            self._sync_if_needed()
            del_key = self._list[key][0]
            del self._list[key]
            del self._dict[del_key]

    def keys(self):
        self._sync_if_needed()
        return self._dict.keys()

    def values(self):
        self._sync_if_needed()
        return self._dict.values()

    def items(self):
        self._sync_if_needed()
        return self._list

    def __len__(self):
        self._sync_if_needed()
        return len(self._list)

    def __iter__(self):
        self._sync_if_needed()
        return iter(self._list)

    def __contains__(self, item):
        self._sync_if_needed()
        return item in self._list or item in self.keys() or item in self.values()

    def append(self, item):
        if item != (item[0], item[1]):
            raise NotImplementedError
        self._sync_if_needed()  # 以防 forced_order
        key, value = item
        self._dict[key] = value
        self._list.append(item)  # 两端都已同步
        self._sync_if_needed()  # 以防 forced_order

    def append_if_it_doesnt_exist_before(self, item: Any):
        if item != (item[0], item[1]):
            raise NotImplementedError
        self._sync_if_needed()
        if item[0] not in self:
            self.append(item)
        self._sync_if_needed()

    def insert(self, i: int, item: Any) -> None:
        if item != (item[0], item[1]):
            raise NotImplementedError
        self._sync_if_needed()
        self._list.insert(i, item)
        self._dict_dirty = True

    def pop(self, i: int = -1) -> Any:
        self._sync_if_needed()
        res = self._list.pop(i)
        self._dict_dirty = True
        return res

    def remove(self, item: Any) -> None:
        if isinstance(item, str):
            item = (item, self._dict[item])
        if item != (item[0], item[1]):
            raise NotImplementedError
        self._sync_if_needed()
        self._list.remove(item)
        self._dict_dirty = True

    def clear(self) -> None:
        self._dict.clear()
        self._list.clear()
        self._dict_dirty = False
        self._list_dirty = False

    def index(self):
        raise NotImplementedError

    def extend(self):
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError

    def reverse(self):
        raise NotImplementedError

    def get_itemic_unit(self, ident):
        return (ident, self._dict[ident])

    def keys_equal_with(self, other):
        self._sync_if_needed()
        return self.key_equality(self, other)

    @classmethod
    def key_equality(cls, a, b):
        return a.keys() == b.keys()
