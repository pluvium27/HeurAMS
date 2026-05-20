"""收藏夹、系统信息、缓存管理与分析统计 API"""

import platform
import shutil
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from heurams.context import config_var
from heurams.services.attic import Attic
from heurams.services.favorite_service import favorite_manager
from heurams.services.logger import get_logger
from heurams.services.version import ver, stage, codename, codename_cn

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["misc"])


def _get_cache_dir() -> Path:
    paths = config_var.get()["global"]["paths"]
    cache = Path(paths.get("cache", str(Path(paths["data"]) / "cache"))) / "voice"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def _human_size(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


@router.get("/cache")
def cache_info() -> dict:
    """缓存统计信息"""
    cache_dir = _get_cache_dir()
    total_size = 0
    file_count = 0
    if cache_dir.exists():
        for f in cache_dir.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size
                file_count += 1
    return {
        "path": str(cache_dir),
        "file_count": file_count,
        "total_size": total_size,
        "human_size": _human_size(total_size),
        "exists": cache_dir.exists(),
    }


@router.delete("/cache")
def clear_cache() -> dict:
    """清空语音缓存"""
    cache_dir = _get_cache_dir()
    count = 0
    if cache_dir.exists():
        for f in cache_dir.rglob("*"):
            if f.is_file():
                f.unlink()
                count += 1
        # 移除空目录
        for d in sorted(cache_dir.rglob("*"), key=lambda p: str(p), reverse=True):
            if d.is_dir():
                try:
                    d.rmdir()
                except OSError:
                    pass
    logger.info("清空缓存: 删除 %d 个文件", count)
    return {"removed": count}


@router.get("/favorites")
def list_favorites() -> list[dict]:
    """获取所有收藏"""
    items = []
    for fav in favorite_manager.get_all():
        items.append({
            "repo_path": fav.repo_path,
            "ident": fav.ident,
            "added": fav.added,
            "tags": fav.tags or [],
        })
    return items


@router.delete("/favorites/{repo_path}/{ident}")
def remove_favorite(repo_path: str, ident: str) -> dict:
    """移除收藏"""
    if favorite_manager.remove(repo_path, ident):
        return {"removed": True}
    raise HTTPException(status_code=404, detail="收藏未找到")


@router.get("/analysis")
def analysis_stats() -> dict:
    """复习统计信息"""
    a = Attic("ana", {"totaltime": 0, "openpuzzles": 0, "puzzles_err": 0})
    total = a.data.get("openpuzzles", 0)
    errs = a.data.get("puzzles_err", 0)
    t = a.data.get("totaltime", 0)
    rate = round(100 * (1 - errs / total), 2) if total else None
    speed = round(total / t, 2) if t else None
    return {
        "total_puzzles": total,
        "errors": errs,
        "total_time": t,
        "accuracy_pct": rate,
        "speed_pps": speed,
    }


@router.post("/cache/precache")
def trigger_precache() -> dict:
    """触发全量 TTS 缓存生成（后台异步）"""
    import threading
    from heurams.kernel.repolib import Repo
    import heurams.kernel.particles as pt
    from heurams.services.tts_service import convertor
    from heurams.services.hasher import get_md5

    paths_cfg = config_var.get()["global"]["paths"]
    cache_dir = Path(paths_cfg.get("cache", str(Path(paths_cfg["data"]) / "cache"))) / "voice"
    cache_dir.mkdir(parents=True, exist_ok=True)
    repo_dir = Path(paths_cfg["data"]) / "repo"

    def _run():
        repos = Repo.probe_valid_repos_in_dir(repo_dir)
        count = 0
        for rp in repos:
            try:
                repo = Repo.from_repodir(rp)
                for ident in repo.ident_index:
                    n = pt.Nucleon.from_data(repo.nucleonic_data_lict.get_itemic_unit(ident))
                    text = n.get("tts_text", "")
                    if not text:
                        continue
                    cache_file = cache_dir / f"{get_md5(text)}.wav"
                    if not cache_file.exists():
                        try:
                            convertor(text, cache_file)
                            count += 1
                        except Exception:
                            pass
            except Exception:
                continue
        logger.info("预缓存完成: 生成 %d 个文件", count)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"started": True, "message": "缓存生成已启动"}


@router.get("/tts")
def generate_tts(text: str):
    """生成 TTS 音频并返回 wav 文件"""
    from heurams.services.hasher import get_md5
    from heurams.services.tts_service import convertor

    paths_cfg = config_var.get()["global"]["paths"]
    cache_dir = Path(paths_cfg.get("cache", str(Path(paths_cfg["data"]) / "cache"))) / "voice"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{get_md5(text)}.wav"

    if not cache_file.exists():
        try:
            convertor(text, cache_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(str(cache_file), media_type="audio/wav", filename="tts.wav")


@router.get("/about")
def about_info() -> dict:
    """系统信息"""
    disk = shutil.disk_usage("/")
    is_venv = hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    return {
        "version": ver,
        "stage": stage,
        "codename": codename,
        "codename_cn": codename_cn,
        "python_version": platform.python_version(),
        "python_path": sys.executable,
        "os": f"{platform.system()} {platform.release()}",
        "platform": platform.platform(),
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "disk_free_pct": round(disk.free / disk.total * 100, 1),
        "in_virtualenv": is_venv,
    }
