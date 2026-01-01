import json
from functools import reduce
from pathlib import Path

import toml

import heurams.kernel.particles as pt

from ...utils.lict import Lict


class Repo:
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
        self.manifest: dict = manifest
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
        self.generate_particles_data()

    def generate_particles_data(self):

        self.nucleonic_data_lict = Lict(
            initlist=list(map(
                self._nucleonic_proc,
                self.payload))
        )
        self.electronic_data_lict = self.algodata
        self.orbitic_data = self.schedule

    def _nucleonic_proc(self, unit):
        ident = unit[0]
        common = self.typedef["common"]
        return (ident, (unit[1], common))

    @staticmethod
    def _merge(value):
        def inner(x):
            return (x, value)

        return inner

    def __len__(self):
        return len(self.payload)

    def persist_to_repodir(
        self, save_list: list | None = None, source: Path | None = None
    ):
        if save_list == None:
            save_list = self.default_save_list
        if self.source != None and source == None:
            source = self.source
        if source == None:
            raise FileNotFoundError("不存在仓库到文件的映射")
        source.mkdir(parents=True, exist_ok=False)
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
                    json.dump(dict_data, f)
                else:
                    raise ValueError(f"不支持的文件类型: {filename}")

    def export_to_single_dict(self):
        return self.database

    @classmethod
    def create_new_repo(cls, source=None):
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
    def create_from_repodir(cls, source: Path):
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
    def create_from_single_dict(cls, dictdata, source: Path | None = None):
        database = dictdata
        database["source"] = source
        return Repo(**database)

    @classmethod
    def check_repodir(cls, source: Path):
        try:
            cls.create_from_repodir(source)
            return 1
        except:
            return 0
