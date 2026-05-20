"""原子信息 REST 路由"""

from fastapi import APIRouter, HTTPException

import heurams.kernel.particles as pt
import heurams.services.timer as timer
from heurams.context import config_var
from heurams.services.favorite_service import favorite_manager
from heurams.services.logger import get_logger

from ..dependencies import get_repo, compute_repo_progress

logger = get_logger(__name__)
router = APIRouter(prefix="/api/repos/{package}", tags=["atoms"])


def _safe_lastdate(e) -> int:
    try:
        return e.lastdate()
    except (KeyError, TypeError):
        return 0


@router.get("/atoms")
def list_atoms(package: str, page: int = 1, page_size: int = 50) -> dict:
    """获取仓库的原子列表"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404, detail=f"仓库 '{package}' 未找到")

    idents = list(repo.ident_index)
    total = len(idents)
    start = (page - 1) * page_size
    end = start + page_size
    page_idents = idents[start:end]

    items = []
    for ident in page_idents:
        e = pt.Electron.from_data(
            electronic_data=repo.electronic_data_lict.get_itemic_unit(ident),
            algo_name=repo.config["algorithm"],
        )
        items.append({
            "ident": ident,
            "activated": bool(e.is_activated()),
            "due": e.is_due(),
            "rept": e.rept(real_rept=True),
            "interval": e["interval"],
            "next_date": e.nextdate(),
            "last_date": _safe_lastdate(e),
        })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/atoms/{ident}")
def get_atom(package: str, ident: str) -> dict:
    """获取单个原子的完整信息"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404, detail=f"仓库 '{package}' 未找到")
    if ident not in repo.ident_index:
        raise HTTPException(status_code=404, detail=f"原子 '{ident}' 未找到")

    n = pt.Nucleon.from_data(
        nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(ident)
    )
    e = pt.Electron.from_data(
        electronic_data=repo.electronic_data_lict.get_itemic_unit(ident),
        algo_name=repo.config["algorithm"],
    )

    nucleon_data = {}
    for key in n:
        if key in ("puzzles",):
            continue
        try:
            nucleon_data[key] = n[key]
        except Exception:
            pass

    return {
        "ident": ident,
        "electron": {
            "activated": bool(e.is_activated()),
            "due": e.is_due(),
            "rept": e.rept(real_rept=True),
            "interval": e["interval"],
            "next_date": e.nextdate(),
            "last_date": _safe_lastdate(e),
            "last_modify": e.last_modify(),
            "algodata": e.algodata.get(e.algoname, {}),
        },
        "nucleon": nucleon_data,
    }


@router.get("/prepare")
def prepare_repo(package: str) -> dict:
    """获取仓库复习准备数据（repo 信息 + 所有原子状态预览）"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404, detail=f"仓库 '{package}' 未找到")

    progress = compute_repo_progress(repo)
    today = timer.get_daystamp()

    atoms = []
    review_count = 0
    new_count = 0
    for i in repo.ident_index:
        e = pt.Electron.from_data(
            electronic_data=repo.electronic_data_lict.get_itemic_unit(i),
            algo_name=repo.config["algorithm"],
        )
        activated = bool(e.is_activated())
        due = e.is_due()
        if activated and due:
            status = "R"
            review_count += 1
        elif activated:
            status = "A"
        else:
            status = "U"
            new_count += 1

        n = pt.Nucleon.from_data(
            nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i)
        )
        content = n.get("content", "") or n.get("tts_text", "") or i
        atoms.append({
            "ident": i,
            "status": status,
            "rept": e.rept(real_rept=True),
            "interval": e["interval"],
            "next_date": e.nextdate(),
            "content": str(content)[:60],
        })

    schedule_num = repo.config["scheduled_num"]

    return {
        "repo": {
            "package": repo.manifest.get("package", package),
            "title": repo.manifest.get("title", package),
            "author": repo.manifest.get("author", ""),
            "desc": repo.manifest.get("desc", ""),
            "source": str(repo.source),
            "algorithm": repo.config["algorithm"],
            "scheduled_num": schedule_num,
        },
        "progress": progress,
        "preview": {"review": review_count, "new": new_count},
        "today": today,
        "atoms": atoms,
        "total_atoms": len(atoms),
    }


@router.get("/atoms/{ident}/favorite")
def get_favorite(package: str, ident: str) -> dict:
    """检查原子是否已收藏"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404)
    rel_path = _rel_repo_path(repo)
    return {"favorited": favorite_manager.has(rel_path, ident)}


@router.post("/atoms/{ident}/favorite")
def toggle_favorite(package: str, ident: str) -> dict:
    """切换收藏状态"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404)
    rel_path = _rel_repo_path(repo)
    if favorite_manager.has(rel_path, ident):
        favorite_manager.remove(rel_path, ident)
        return {"favorited": False, "action": "removed"}
    else:
        favorite_manager.add(rel_path, ident)
        return {"favorited": True, "action": "added"}


def _rel_repo_path(repo) -> str:
    """获取仓库相对路径"""
    from heurams.context import workdir
    data_repo = workdir / "data" / "repo"
    try:
        return str(repo.source.relative_to(data_repo))
    except (ValueError, AttributeError):
        return str(repo.source)
