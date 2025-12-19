# 配置文件服务
import pathlib
import typing

import toml

from heurams.services.logger import get_logger


class ConfigFile:
    def __init__(self, path: pathlib.Path):
        self.logger = get_logger(__name__)
        self.path = path
        if not self.path.exists():
            self.path.touch()
            self.logger.debug("创建配置文件: %s", self.path)
        self.data = dict()
        self._load()

    def _load(self):
        """从文件加载配置数据"""
        with open(self.path, "r") as f:
            try:
                self.data = toml.load(f)
                self.logger.debug("配置文件加载成功: %s", self.path)
            except toml.TomlDecodeError as e:
                print(f"{e}")
                self.logger.error("TOML解析错误: %s", e)
                self.data = {}

    def modify(self, key: str, value: typing.Any):
        """修改配置值并保存"""
        self.data[key] = value
        self.logger.debug("修改配置项: %s = %s", key, value)
        self.save()

    def save(self, path: typing.Union[str, pathlib.Path] = ""):
        """保存配置到文件"""
        save_path = pathlib.Path(path) if path else self.path
        with open(save_path, "w") as f:
            toml.dump(self.data, f)
        self.logger.debug("配置文件已保存: %s", save_path)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """获取配置值, 如果不存在返回默认值"""
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> typing.Any:
        return self.data[key]

    def __setitem__(self, key: str, value: typing.Any):
        self.data[key] = value
        self.save()

    def __contains__(self, key: str) -> bool:
        """支持 in 语法"""
        return key in self.data
