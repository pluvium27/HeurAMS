import pathlib

from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)


def probe_by_filename(filename):
    """探测指定文件 (无扩展名) 的所有信息"""
    logger.debug("probe_by_filename: 探测文件 '%s'", filename)
    paths: dict = config_var.get().get("paths")
    logger.debug("配置路径: %s", paths)
    formats = ["toml", "json"]
    result = {}
    for item, attr in paths.items():
        for i in formats:
            attr: pathlib.Path = pathlib.Path(attr) / filename + "." + i
            if attr.exists():
                logger.debug("找到文件: %s", attr)
                result[item.replace("_dir", "")] = str(attr)
            else:
                logger.debug("文件不存在: %s", attr)
    logger.debug("probe_by_filename 结果: %s", result)
    return result


def probe_all(is_stem=1):
    """依据目录探测所有信息

    Args:
        is_stem (boolean): 是否**删除**文件扩展名

    Returns:
        dict: 有三项, 每一项的键名都是文件组类型, 值都是文件组列表, 只包含文件名
    """
    logger.debug("probe_all: 开始探测, is_stem=%d", is_stem)
    paths: dict = config_var.get().get("paths")
    logger.debug("配置路径: %s", paths)
    result = {}
    for item, attr in paths.items():
        attr: pathlib.Path = pathlib.Path(attr)
        result[item.replace("_dir", "")] = list()
        logger.debug("扫描目录: %s", attr)
        file_count = 0
        for i in attr.iterdir():
            if not i.is_dir():
                file_count += 1
                if is_stem:
                    result[item.replace("_dir", "")].append(str(i.stem))
                else:
                    result[item.replace("_dir", "")].append(str(i.name))
        logger.debug("目录 %s 中找到 %d 个文件", attr, file_count)
    logger.debug("probe_all 完成, 结果 keys: %s", list(result.keys()))
    return result


if __name__ == "__main__":
    import os

    print(os.getcwd())
    print(probe_all())
