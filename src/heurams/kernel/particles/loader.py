from .nucleon import Nucleon
from .electron import Electron
import heurams.services.hasher as hasher
import pathlib
import toml
import json
from copy import deepcopy
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def load_nucleon(path: pathlib.Path, fmt="toml"):
    logger.debug("load_nucleon: 加载文件 %s, 格式: %s", path, fmt)
    with open(path, "r") as f:
        dictdata = dict()
        dictdata = toml.load(f)  # type: ignore
        logger.debug("TOML 解析成功, keys: %s", list(dictdata.keys()))
        lst = list()
        nested_data = dict()
        # 修正 toml 解析器的不管嵌套行为
        for key, value in dictdata.items():
            if "__metadata__" in key:  # 以免影响句号
                if "." in key:
                    parts = key.split(".")
                    current = nested_data
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                logger.debug("处理元数据键: %s", key)
            else:
                nested_data[key] = value
        logger.debug("嵌套数据处理完成, keys: %s", list(nested_data.keys()))
        # print(nested_data)
        for item, attr in nested_data.items():
            if item == "__metadata__":
                continue
            logger.debug("处理项目: %s", item)
            lst.append(
                (
                    Nucleon(item, attr, deepcopy(nested_data["__metadata__"])),
                    deepcopy(nested_data["__metadata__"]["orbital"]),
                )
            )
        logger.debug("load_nucleon 完成, 加载了 %d 个 Nucleon 对象", len(lst))
        return lst


def load_electron(path: pathlib.Path, fmt="json") -> dict:
    """从文件路径加载电子对象

    Args:
        path (pathlib.Path): 路径
        fmt (str): 文件格式(可选, 默认 json)

    Returns:
        dict: 键名是电子对象名称, 值是电子对象
    """
    logger.debug("load_electron: 加载文件 %s, 格式: %s", path, fmt)
    with open(path, "r") as f:
        dictdata = dict()
        dictdata = json.load(f)  # type: ignore
        logger.debug("JSON 解析成功, keys: %s", list(dictdata.keys()))
        dic = dict()
        for item, attr in dictdata.items():
            logger.debug("处理电子项目: %s", item)
            dic[item] = Electron(item, attr)
        logger.debug("load_electron 完成, 加载了 %d 个 Electron 对象", len(dic))
        return dic
