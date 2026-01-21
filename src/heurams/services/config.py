# 配置文件服务
import pathlib
import typing

import toml

from heurams.services.logger import get_logger

default_config = {
    "persist_to_file": 1, # 将更改保存到文件
    "daystamp_override": -1, # 覆写时间, 设为 -1 以禁用
    "timestamp_override": -1, # 覆写时间, 设为 -1 以禁用
    "quick_pass": 1, # 启用用于测试的快速通过
    "scheduled_num": 8, # 对于每个项目的默认新记忆原子数量
    "timezone_offset": 28800, # UTC 时间戳修正 仅用于 UNIX 日时间戳的生成修正, 单位为秒
    # 28800 是中国标准时间 (UTC+8)
    
    "interface": {
        "memorizor": {
            "autovoice": True  # 自动语音播放, 仅限于 recognition 组件
        }
    },
    
    "algorithm": {
        "default": "SM-2"  # 主要算法
        # 可选项: SM-2, SM-15M, FSRS
    },
    
    "puzzles": {  # 谜题默认配置
        "mcq": {
            "max_riddles_num": 2
        },
        "cloze": {
            "min_denominator": 3
        }
    },
    
    "paths": {  # 相对于配置文件的 ".." (即工作目录) 而言 或绝对路径
        "data": "./data"
    },
    
    "services": {  # 定义服务到提供者的映射
        "audio": "playsound",  # 可选项: playsound(通用), termux(仅用于 Android Termux), mpg123(TODO)
        "tts": "edgetts",  # 可选项: edgetts
        "llm": "openai",  # 可选项: openai
        "sync": "webdav"  # 可选项: 留空, webdav
    },
    
    "providers": {
        "tts": {
            "edgetts": {  # EdgeTTS 设置
                "voice": "zh-CN-XiaoxiaoNeural"  # 可选项: zh-CN-YunjianNeural (男声), zh-CN-XiaoxiaoNeural (女声)
            }
        },
        "llm": {
            "openai": {  # 与 OpenAI 相容的语言模型接口服务设置
                "url": "",
                "key": ""
            }
        },
        "sync": {
            "webdav": {  # WebDAV 同步设置
                "url": "",
                "username": "",
                "password": "",
                "remote_path": "/heurams/",
                "verify_ssl": True
            }
        }
    },
}

class ConfigFile:
    def __init__(self, path: pathlib.Path):
        self.logger = get_logger(__name__)
        self.path = path
        self.data = dict()
        if not self.path.exists():
            self.path.touch()
            self.logger.debug("创建配置文件: %s", self.path)
            self.data = default_config
        self.valid_configfile = 1
        # 考虑到可能临时编辑格式错误, 所以不覆写格式错误的配置文件, 而是提示损坏并使用默认配置
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
                self.data = default_config
                self.valid_configfile = 0

    def modify(self, key: str, value: typing.Any):
        """修改配置值并保存"""
        self.data[key] = value
        self.logger.debug("修改配置项: %s = %s", key, value)
        self.save()

    def save(self, path: typing.Union[str, pathlib.Path] = ""):
        """保存配置到文件"""
        if self.valid_configfile:
            save_path = pathlib.Path(path) if path else self.path
            with open(save_path, "w") as f:
                toml.dump(self.data, f)
            self.logger.debug("配置文件已保存: %s", save_path)
        else:
            pass

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
