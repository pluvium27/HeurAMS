"""配置查询与修改 REST 路由"""

from fastapi import APIRouter, HTTPException

from heurams.services.config import ConfigDict
from heurams.services.epath import epath

from ..dependencies import get_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
def get_config_tree():
    """获取完整配置树"""
    config = get_config()
    return _build_tree(config)


def _build_tree(node, prefix: str = "") -> list[dict]:
    """通过 ConfigDict 的 __getitem__ 展开配置树"""
    result = []
    for key in node:
        if key.startswith("_"):
            continue
        full_key = f"{prefix}.{key}" if prefix else key
        child = node[key]
        if isinstance(child, ConfigDict):
            children = _build_tree(child, full_key)
            result.append({"key": full_key, "type": "branch", "children": children})
            # 收集_meta数据
            for mk, mv in node.items():
                if mk == f"_{key}_desc" and isinstance(mv, str):
                    if children:
                        children[0]["_meta_desc"] = mv
        else:
            item = {"key": full_key, "type": type(child).__name__, "value": child}
            cand_key = f"_{key}_candidate"
            desc_key = f"_{key}_desc"
            if desc_key in node:
                item["desc"] = node[desc_key]
            if cand_key in node:
                item["candidates"] = node[cand_key]
            result.append(item)
    return result


@router.get("/{section:path}")
def get_config_section(section: str):
    """获取指定配置节的详细数据（含元数据）"""
    config = get_config()
    keys = section.split("/")
    current = config
    for key in keys:
        if key not in current:
            return {}
        current = current[key]

    result = {}
    for k, v in current.items():
        if k.startswith("_"):
            continue
        item = {"value": v, "type": type(v).__name__}
        cand_key = f"_{k}_candidate"
        desc_key = f"_{k}_desc"
        if cand_key in current:
            item["candidates"] = current[cand_key]
        if desc_key in current:
            item["desc"] = current[desc_key]
        result[k] = item
    return result


@router.put("/{section:path}")
def update_config(section: str, body: dict):
    """更新单个配置项

    body: {"value": ..., "path": "..."}
    path 是可选的完整路径，默认为 section
    """
    config = get_config()
    # 将 / 分隔的路径转为 . 分隔的 epath
    path = body.get("path", section.replace("/", "."))
    new_value = body.get("value")
    if new_value is None:
        raise HTTPException(status_code=400, detail="缺少 value")

    # 尝试类型转换：保持原类型
    old_val = epath(config, path)
    if old_val is not None and type(old_val) != type(new_value):
        try:
            new_value = type(old_val)(new_value)
        except (ValueError, TypeError):
            pass

    epath(config, path, enable_modify=True, new_value=new_value)
    # 自动持久化
    config.persist()
    return {"ok": True, "path": path, "value": new_value}
