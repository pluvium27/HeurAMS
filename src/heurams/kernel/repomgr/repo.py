from pathlib import Path
import heurams.kernel.particles as pt
import toml
import json
from .lict import Lict
class Repo():
    file_mapping = {
        "orbital": "orbital.toml",
        "payload": "payload.toml",
        "algodata": "algodata.json",
        "manifest": "manifest.toml",
        "formation": "formation.toml",
    }

    default_save_list = ["algodata"]

    def __init__(self, orbital, payload, manifest, formation, algodata, source = None) -> None:
        self.orbital: pt.Orbital = orbital
        self.payload: dict = payload
        self.manifest: dict = manifest
        self.formation: dict = formation
        self.algodata: dict = algodata
        self.source: Path | None = source # 若存在, 指向 repo 所在 dir
        self.database = {
            "orbital": self.orbital,
            "payload": self.payload,
            "manifest": self.manifest,
            "formation": self.formation,
            "algodata": self.algodata,
            "source": self.source,
        }
        self.particles = dict()

    def __len__(self):
        return len(self.payload)

    def persist_to_repodir(self, save_list: list | None = None, source: Path | None= None):
        if save_list == None:
            save_list = self.default_save_list
        if self.source != None and source == None:
            source = self.source
        if source == None:
            raise FileNotFoundError("不存在仓库到文件的映射")
        for keyname in save_list:
            filename = self.file_mapping[keyname]
            with open(source / filename, 'w') as f:
                if filename.endswith("toml"):
                    toml.dump(self.database[keyname], f)
                elif filename.endswith("json"):
                    json.dump(self.database[keyname], f)
                else:
                    raise ValueError(f"不支持的文件类型: {filename}")
    
    def export_to_single_dict(self):
        return self.database
    
    @classmethod
    def create_new_repo(cls, source = None):
        default_database = {
            "orbital": {"puzzles": {}, "schedule": {}},
            "payload": {},
            "algodata": {},
            "manifest": {},
            "formation": {"annotation": {}, "unified": {}},
            "source": source
        }
        return Repo(**default_database)
    
    @classmethod
    def create_from_repodir(cls, source: Path):
        database = {}
        for keyname, filename in cls.file_mapping.items():
            with open(source / filename, "r") as f:
                if filename.endswith("toml"):
                    database[keyname] = toml.load(f)
                elif filename.endswith("json"):
                    database[keyname] = json.load(f)
                else:
                    raise ValueError(f"不支持的文件类型: {filename}")
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

    def _load(self):
        pass

    def _load_nucleons(self):
        self.particles["nucleons"] = Lict(initdict = self.payload)
        self.particles["electrons"] = Lict(initdict = self.algodata)
        
        mtx["list"] = 
        for ident, payload in self.payload:
            res.append()

