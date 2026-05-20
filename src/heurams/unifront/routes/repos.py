"""仓库信息 REST 路由"""

from fastapi import APIRouter, HTTPException

from heurams.services.logger import get_logger

from ..dependencies import compute_repo_progress, get_repo, list_repos
from ..schemas import RepoInfo

logger = get_logger(__name__)
router = APIRouter(prefix="/api/repos", tags=["repos"])


@router.get("")
def list_all_repos() -> list[RepoInfo]:
    """获取所有可用仓库"""
    return list_repos()


@router.get("/{package}")
def get_repo_info(package: str) -> RepoInfo:
    """获取单个仓库详细信息"""
    repo = get_repo(package)
    if repo is None:
        raise HTTPException(status_code=404, detail=f"仓库 '{package}' 未找到")

    progress = compute_repo_progress(repo)
    return RepoInfo(
        package=repo.manifest.get("package", package),
        title=repo.manifest.get("title", package),
        author=repo.manifest.get("author", ""),
        desc=repo.manifest.get("desc", ""),
        source=str(repo.source),
        total=progress["total"],
        touched=progress["touched"],
    )
