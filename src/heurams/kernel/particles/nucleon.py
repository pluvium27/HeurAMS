from copy import deepcopy
from logging import config

from heurams.services.logger import get_logger
from heurams.utils.evalizor import Evalizer
from heurams.context import config_var

logger = get_logger(__name__)


class Nucleon:
    """原子核: 带有运行时隔离的模板化只读材料元数据容器"""

    def __init__(self, ident, payload, common):
        self.ident = ident
        env = {"payload": payload,
               "default": config_var.get()['puzzles'],
               "nucleon": (payload | common)}
        self.evalizer = Evalizer(environment=env)
        self.data: dict = self.evalizer(deepcopy((payload | common)))  # type: ignore

    def __getitem__(self, key):
        if isinstance(key, str):
            if key == "ident":
                return self.ident
            return self.data[key]
        else:
            raise AttributeError

    def __setitem__(self, key, value):
        raise AttributeError("应为只读")

    def __delitem__(self, key):
        raise AttributeError("应为只读")

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        return key in (self.data)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        from pprint import pformat

        s = pformat(self.data, indent=4)
        return s

    @staticmethod
    def create_on_nucleonic_data(nucleonic_data: tuple):
        _data = nucleonic_data
        payload = _data[1][0]
        common = _data[1][1]
        ident = _data[0]  # TODO:实现eval
        return Nucleon(ident, payload, common)
