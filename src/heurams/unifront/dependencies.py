"""unifront 依赖注入"""

from __future__ import annotations

from pathlib import Path

import heurams.kernel.particles as pt
from heurams.context import config_var, workdir
from heurams.kernel.repolib.repo import Repo
from heurams.services.logger import get_logger

from .schemas import RepoInfo

logger = get_logger(__name__)

_repo_cache: dict[str, Repo] = {}


def get_data_repo_dir() -> Path:
    """获取仓库目录"""
    return workdir / "data" / "repo"


def compute_repo_progress(repo: Repo) -> dict:
    """计算 repo 的学习进度"""
    progress = {
        "total": repo.data_length,
        "touched": 0,
    }
    for i in range(repo.data_length):
        try:
            e = pt.Electron.from_data(
                electronic_data=repo.electronic_data_lict[i],
                algo_name=repo.config["algorithm"],
            )
            if e.is_activated():
                progress["touched"] += 1
        except Exception:
            pass
    return progress


def get_repo(package: str) -> Repo | None:
    """按包名获取 Repo"""
    if package in _repo_cache:
        return _repo_cache[package]

    repo_dir = get_data_repo_dir() / package
    if not repo_dir.exists():
        return None

    try:
        repo = Repo.from_repodir(repo_dir)
        _repo_cache[package] = repo
        return repo
    except Exception as e:
        logger.error("加载仓库 %s 失败: %s", package, e)
        return None


def get_config():
    """获取配置对象"""
    return config_var.get()


def list_repos() -> list[RepoInfo]:
    """列举可用仓库"""
    from .schemas import RepoInfo

    repo_dir = get_data_repo_dir()
    valid_repos = Repo.probe_valid_repos_in_dir(repo_dir)

    result = []
    for rp in valid_repos:
        if rp.name in _repo_cache:
            repo = _repo_cache[rp.name]
        else:
            repo = Repo.from_repodir(rp)
            _repo_cache[rp.name] = repo
        progress = compute_repo_progress(repo)
        result.append(
            RepoInfo(
                package=repo.manifest.get("package", rp.name),
                title=repo.manifest.get("title", rp.name),
                author=repo.manifest.get("author", ""),
                desc=repo.manifest.get("desc", ""),
                source=str(rp),
                total=progress["total"],
                touched=progress["touched"],
            )
        )
    return result
