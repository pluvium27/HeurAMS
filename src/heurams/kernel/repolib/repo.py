import json
from pathlib import Path
from typing import TypedDict

import toml


from heurams.context import config_var
from heurams.kernel.auxiliary.lict import Lict


class RepoManifest(TypedDict):
    """仓库清单数据结构

    Attributes:
        title: 仓库标题
        author: 作者名称
        package: 包名标识
        desc: 仓库描述
    """

    title: str
    author: str
    package: str
    desc: str


class Repo:
    """记忆单元仓库

    管理单个记忆单元集的所有数据, 包括内容 (payload)、算法状态 (algodata)、
    复习策略 (schedule) 和元信息 (manifest/typedef). 

    上层 API 请访问此对象下的粒子对象列表 (nucleonic_data_lict 等). 

    Attributes:
        schedule: 复习策略字典 (轨道定义)
        payload: 记忆内容 (Lict)
        algodata: 算法状态数据 (Lict)
        manifest: 仓库清单信息
        typedef: 类型定义和谜题配置
        source: 仓库来源目录路径
    """

    file_mapping = {
        "schedule": "schedule.toml",
        "payload": "payload.toml",
        "algodata": "algodata.json",
        "manifest": "manifest.toml",
        "typedef": "typedef.toml",
    }

    type_mapping = {
        "schedule": "dict",
        "payload": "lict",
        "algodata": "lict",
        "manifest": "dict",
        "typedef": "dict",
    }

    default_save_list = ["algodata"]

    def __init__(
        self,
        schedule: dict,
        payload: Lict,
        manifest: dict,
        typedef: dict,
        algodata: Lict,
        source=None,
    ) -> None:
        self.schedule: dict = schedule
        self.manifest: RepoManifest = manifest  # type: ignore
        self.typedef: dict = typedef
        self.payload: Lict = payload
        self.algodata: Lict = algodata
        self.source: Path | None = source  # 若存在, 指向 repo 所在 dir
        self.database = {
            "schedule": self.schedule,
            "payload": self.payload,
            "manifest": self.manifest,
            "typedef": self.typedef,
            "algodata": self.algodata,
            "source": self.source,
        }
        self.config = {
            "algorithm": config_var.get()["interface"]["global"]["algorithm"],
            "scheduled_num": config_var.get()["interface"]["global"]["scheduled_num"],
        }
        try:
            self.config.update(dict(config_var.get()["repo"][self.manifest["package"]]))
        except (KeyError, TypeError, ValueError):
            pass
        self._generate_particles_data()

    def _generate_particles_data(self):
        """生成上层的粒子数据

        将 payload 转换为 Nucleon 所需格式, 并为每个 ident 初始化
        algodata 条目. 会在 __init__ 后自动调用. 
        """
        self.nucleonic_data_lict = Lict(
            initlist=list(map(self._nucleonic_proc, self.payload))
        )
        self.orbitic_data = self.schedule
        self.data_length = len(self.nucleonic_data_lict)
        self.ident_index = self.nucleonic_data_lict.keys()
        for i in self.ident_index:
            self.algodata.append_if_it_doesnt_exist_before((i, {}))
        self.electronic_data_lict = self.algodata

    def _nucleonic_proc(self, unit):
        ident = unit[0]
        common = self.typedef["common"]
        return (ident, (unit[1], common))

    def __len__(self):
        return len(self.payload)

    def __repr__(self):
        from pprint import pformat

        s = pformat(self.database, indent=4)
        return s

    def persist_to_repodir(
        self, save_list: list | None = None, source: Path | None = None
    ):
        """保存单元集数据到目录"""
        if save_list == None:
            save_list = self.default_save_list
        if self.source != None and source == None:
            source = self.source
        if source == None:
            raise FileNotFoundError("不存在仓库到文件的映射")
        source.mkdir(parents=True, exist_ok=True)
        for keyname in save_list:
            filename = self.file_mapping[keyname]
            with open(source / filename, "w") as f:
                try:
                    dict_data = self.database[keyname].dicted_data
                except AttributeError:
                    dict_data = dict(self.database[keyname])
                if filename.endswith("toml"):
                    toml.dump(dict_data, f)
                elif filename.endswith("json"):
                    json.dump(dict_data, f, ensure_ascii=False, indent=4)
                else:
                    raise ValueError(f"不支持的文件类型: {filename}")

    def export_to_dict(self):
        """导出至单个字典"""
        return self.database

    @classmethod
    def create_new_repo(cls, source=None):
        """创建新的空单元集

        Args:
            source: 可选的仓库目录路径

        Returns:
            包含空数据的 Repo 实例
        """
        default_database = {
            "schedule": {},
            "payload": Lict([]),
            "algodata": Lict([]),
            "manifest": {},
            "typedef": {},
            "source": source,
        }
        return Repo(**default_database)

    @classmethod
    def from_repodir(cls, source: Path):
        """从目录创建单元集

        读取目录中的 TOML/JSON 文件并构建 Repo 实例. 

        Args:
            source: 仓库目录路径

        Returns:
            Repo 实例

        Raises:
            FileNotFoundError: 目录缺少必要的文件
            ValueError: 文件格式不支持
        """
        database = {}
        for keyname, filename in cls.file_mapping.items():
            with open(source / filename, "r") as f:
                loaded: dict
                if filename.endswith("toml"):
                    loaded = toml.load(f)
                elif filename.endswith("json"):
                    loaded = json.load(f)
                else:
                    raise ValueError(f"不支持的文件类型: {filename}")
                if cls.type_mapping[keyname] == "lict":
                    database[keyname] = Lict(list(loaded.items()))
                elif cls.type_mapping[keyname] == "dict":
                    database[keyname] = loaded
                else:
                    raise ValueError(f"不支持的数据容器: {cls.type_mapping[keyname]}")
        database["source"] = source
        return Repo(**database)

    @classmethod
    def from_dict(cls, dictdata, source: Path | None = None):
        """从单一字典创建单元集

        Args:
            dictdata: 包含 schedule/payload/algodata/manifest/typedef 的字典
            source: 可选的仓库目录路径

        Returns:
            Repo 实例
        """
        database = dictdata
        database["source"] = source
        return Repo(**database)

    @classmethod
    def check_repodir(cls, source: Path):
        """检测单元集目录合法性

        尝试从目录加载 Repo, 成功则视为合法. 

        Args:
            source: 待检测的目录路径

        Returns:
            True 表示合法, False 表示不合法
        """
        try:
            cls.from_repodir(source)
            return True
        except (FileNotFoundError, KeyError, ValueError, toml.TomlDecodeError):
            return False

    @classmethod
    def probe_valid_repos_in_dir(cls, folder: Path):
        """扫描目录中的所有合法仓库子目录

        Args:
            folder: 待扫描的父目录路径

        Returns:
            合法仓库子目录的 Path 列表
        """
        lst = list()
        for i in folder.iterdir():
            if i.is_dir():
                if cls.check_repodir(i):
                    lst.append(i)
        return lst
