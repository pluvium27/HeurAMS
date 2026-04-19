# 收藏服务
import json
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FavoriteItem:
    """收藏项"""

    repo_path: str  # 仓库相对路径 (相对于 data/repo)
    ident: str  # 原子标识符
    added: int  # 添加时间戳 (UNIX 秒)
    # 可选标签
    tags: List[str] | None = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> dict:
        return {
            "repo_path": self.repo_path,
            "ident": self.ident,
            "added": self.added,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FavoriteItem":
        return cls(
            repo_path=data["repo_path"],
            ident=data["ident"],
            added=data["added"],
            tags=data.get("tags", []),
        )


class FavoriteManager:
    """收藏管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_loaded"):
            self._loaded = True
            self._favorites: List[FavoriteItem] = []
            self._file_path = self._get_file_path()
            self.load()

    def _get_file_path(self) -> Path:
        """获取收藏文件路径"""
        config_path = Path(config_var.get()['global']["paths"]["data"])
        fav_path = config_path / "global" / "favorites.json"
        fav_path.parent.mkdir(parents=True, exist_ok=True)
        return fav_path

    def load(self) -> None:
        """从文件加载收藏列表"""
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._favorites = [FavoriteItem.from_dict(item) for item in data]
                logger.debug("收藏列表加载成功，共 %d 项", len(self._favorites))
            except Exception as e:
                logger.error("加载收藏列表失败: %s", e)
                self._favorites = []
        else:
            self._favorites = []

    def save(self) -> None:
        """保存收藏列表到文件"""
        try:
            data = [item.to_dict() for item in self._favorites]
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("收藏列表保存成功，共 %d 项", len(self._favorites))
        except Exception as e:
            logger.error("保存收藏列表失败: %s", e)

    def add(self, repo_path: str, ident: str, tags: List[str] | None = None) -> bool:
        """添加收藏

        Args:
            repo_path: 仓库相对路径
            ident: 原子标识符
            tags: 标签列表
        Returns:
            是否成功添加 (若已存在则返回 False)
        """
        # 检查是否已存在
        for item in self._favorites:
            if item.repo_path == repo_path and item.ident == ident:
                logger.debug("收藏已存在: %s/%s", repo_path, ident)
                return False
        item = FavoriteItem(
            repo_path=repo_path,
            ident=ident,
            added=int(time.time()),
            tags=tags if tags else [],
        )
        self._favorites.append(item)
        self.save()
        logger.info("添加收藏: %s/%s", repo_path, ident)
        return True

    def remove(self, repo_path: str, ident: str) -> bool:
        """移除收藏

        Returns:
            是否成功移除 (若不存在则返回 False)
        """
        for idx, item in enumerate(self._favorites):
            if item.repo_path == repo_path and item.ident == ident:
                del self._favorites[idx]
                self.save()
                logger.info("移除收藏: %s/%s", repo_path, ident)
                return True
        logger.debug("收藏不存在: %s/%s", repo_path, ident)
        return False

    def has(self, repo_path: str, ident: str) -> bool:
        """检查是否已收藏"""
        for item in self._favorites:
            if item.repo_path == repo_path and item.ident == ident:
                return True
        return False

    def get_all(self) -> List[FavoriteItem]:
        """获取所有收藏项（按添加时间倒序）"""
        return sorted(self._favorites, key=lambda x: x.added, reverse=True)

    def get_by_repo(self, repo_path: str) -> List[FavoriteItem]:
        """获取指定仓库的所有收藏项"""
        return [item for item in self._favorites if item.repo_path == repo_path]

    def clear(self) -> None:
        """清空收藏列表"""
        self._favorites = []
        self.save()
        logger.info("清空收藏列表")

    def count(self) -> int:
        """收藏总数"""
        return len(self._favorites)


# 全局单例实例
favorite_manager = FavoriteManager()
