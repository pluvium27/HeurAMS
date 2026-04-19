import pathlib
import typing

import toml
from collections import UserDict
import atexit

from heurams.services.logger import get_logger
from heurams.services.exceptions import WTFException

# 我们的流程是: 找到文件名: 返回文件名里头的数据; 找不到: 继续查索引; 所以 self.data 除了存本级各种索引球用没得
# 递归就是这么吊
class ConfigDict(UserDict): # 舒服了
    def __init__(self, config_path: pathlib.Path, dict = None): # 需要自己把自己提起来
        if dict:
            raise WTFException("不要放默认值...")
        super().__init__(dict)
        self.logger = get_logger(__name__)
        self.path = config_path
        self.is_dir = self.path.is_dir()
        if self.is_dir:
            self.update_index() # 狗儿要唱狗儿歌
        else:
            with open(self.path, 'r+') as f: #TODO: 给这个做缓存
                try:
                    self.data = toml.load(f)
                except:
                    self.data = {}
                    self.persist = lambda: False # 不修改错误的配置文件
    
    def __getitem__(self, key):
        # 我们实现了先进的懒狗加载
        value = super().__getitem__(key)
        if isinstance(value, pathlib.Path):
            return ConfigDict(value)
        return value

    def converter(self, s):
        if (self.path / s).exists:
            return self.path / s
        return self.path / s+'.toml'

    def __contains__(self, key):
        return super().__contains__(key)

    def __setitem__(self, key, value):
        origvalue = super().__getitem__(key) # 所以你不该访问不存在的对象
        if isinstance(origvalue, ConfigDict):
            if origvalue.path.is_dir():
                raise WTFException("你怎么能变更目录配置的内容呢?!")
            else:
                # 对文件, 我们允许这种覆写存在
                # 但是不准变类型
                origvalue.data = value
        super().__setitem__(key, value)

    def update_index(self): # 如果有人没事干在config里面创建指向config的符号链接 这玩意会崩溃 但是不要修复: 需要这个符号链接特性
        for i in self.path.iterdir():
            if i.is_dir():
                self.data[i.name] = i
            else:
                if i.suffix == '.toml':
                    self.data[i.stem] = i
                else:
                    self.logger.log(f"配置目录中有无效的文件 {i.stem}") # what's up bro

    def persist(self):
        if self.is_dir:
            raise WTFException("不准这样浪费性能...")

        with open(self.path, 'w+') as f:
            toml.dump(self.data, f)
    
    def __del__(self):
        if not self.is_dir:
            self.persist() # 不准循环引用, 懂了吧
    
    @staticmethod
    def titleize(objt):
        if isinstance(objt, pathlib.Path):
            return objt.stem
        else:
            return objt