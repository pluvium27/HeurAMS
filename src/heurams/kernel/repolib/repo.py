import json
from functools import reduce
from pathlib import Path
from typing import TypedDict

import toml

import heurams.kernel.particles as pt

from heurams.context import config_var
from heurams.kernel.auxiliary.lict import Lict


class RepoManifest(TypedDict):
    title: str
    author: str
    package: str
    desc: str


class Repo:
    """只维护仓库本身
    上层 API 请访问此对象下粒子对象列表"""

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
            "algorithm": config_var.get()['interface']['global']['algorithm'],
            "scheduled_num": config_var.get()['interface']['global']['scheduled_num'],
        }
        try:
            self.config.update(dict(config_var.get()['repo'][self.manifest['package']]))
        except:
            pass
        self._generate_particles_data()

    def _generate_particles_data(self):
        """生成上层的粒子对象组和 API 交互, 会在 init 后自动调用"""
        self.nucleonic_data_lict = Lict(
            initlist=list(map(self._nucleonic_proc, self.payload))
        )
        self.orbitic_data = self.schedule
        self.data_length = len(self.nucleonic_data_lict)
        self.ident_index = self.nucleonic_data_lict.keys()
        for i in self.ident_index:
            self.algodata.append_new((i, {}))
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
                except:
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
        """创建新的空单元集"""
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
        """从目录创建单元集"""
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
        """从单一字典创建单元集"""
        database = dictdata
        database["source"] = source
        return Repo(**database)

    @classmethod
    def check_repodir(cls, source: Path):
        """检测单元集目录合法性"""
        try:
            cls.from_repodir(source)
            return True
        except:
            return False

    @classmethod
    def probe_valid_repos_in_dir(cls, folder: Path):
        """返回一个合法的子目录 Path() 列表"""
        lst = list()
        for i in folder.iterdir():
            if i.is_dir():
                if cls.check_repodir(i):
                    lst.append(i)
        return lst
