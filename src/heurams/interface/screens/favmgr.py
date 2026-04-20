"""收藏夹管理器界面"""

import base64
from pathlib import Path
from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
)

from heurams.context import config_var
from heurams.kernel.repolib import Repo
from heurams.services.favorite_service import FavoriteItem, favorite_manager
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class FavoriteManagerScreen(Screen):
    """收藏夹管理器屏幕"""

    SUB_TITLE = "收藏夹"

    BINDINGS = [
        ("q", "go_back", "返回"),
        ("d", "toggle_dark", ""),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.favorites: List[FavoriteItem] = []
        self._load_favorites()

    def _load_favorites(self) -> None:
        """加载收藏列表"""
        self.favorites = favorite_manager.get_all()
        logger.debug("加载 %d 个收藏项", len(self.favorites))

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        with ScrollableContainer(id="favorites-container"):
            if not self.favorites:
                yield Label("暂无收藏", classes="empty-label")
                yield Static("使用 * 键在记忆界面中添加收藏.")
            else:
                yield Label(f"共 {len(self.favorites)} 个收藏项", classes="count-label")
                yield ListView(id="favorites-list")
        yield Footer()

    def on_mount(self) -> None:
        """挂载后填充列表"""
        if self.favorites:
            list_view = self.query_one("#favorites-list")
            for fav in self.favorites:
                list_view.append(self._create_favorite_item(fav))  # type: ignore

    def _encode_favorite_key(self, repo_path: str, ident: str) -> str:
        """编码仓库路径和标识符为安全的按钮 ID 部分"""
        # 使用 \x00 分隔两部分，然后进行 base64 编码
        combined = f"{repo_path}\x00{ident}"
        encoded = base64.urlsafe_b64encode(combined.encode()).decode()
        # 去掉填充的等号
        return encoded.rstrip("=")

    def _decode_favorite_key(self, key: str) -> tuple[str, str]:
        """解码按钮 ID 部分为仓库路径和标识符"""
        # 补全等号以使长度是4的倍数
        padded = key + "=" * ((4 - len(key) % 4) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        repo_path, ident = decoded.split("\x00", 1)
        return repo_path, ident

    def _create_favorite_item(self, fav: FavoriteItem) -> ListItem:
        """创建收藏项列表项"""
        # 尝试获取仓库信息
        repo_info = self._get_repo_info(fav.repo_path, fav)
        title = repo_info.get("title", fav.repo_path) if repo_info else fav.repo_path
        content_preview = repo_info.get("content_preview", "") if repo_info else ""
        added_time = self._format_time(fav.added)

        # 构建显示文本
        display_text = f"[b]{title}[/b] ({fav.ident})\n"
        if content_preview:
            display_text += f"{content_preview}\n"
        display_text += f"添加于: {added_time}"
        if fav.tags:
            display_text += f"  标签: {', '.join(fav.tags)}"

        # 创建安全的按钮 ID
        button_key = self._encode_favorite_key(fav.repo_path, fav.ident)
        # 创建列表项，包含移除按钮
        container = ScrollableContainer(
            Markdown(display_text, classes="favorite-content"),
            Button("移除", id=f"remove-{button_key}", variant="error"),
            classes="favorite-item",
        )
        return ListItem(container)

    def _get_repo_info(self, repo_path: str, fav: FavoriteItem) -> Optional[dict]:
        """获取仓库信息（标题、原子内容预览）"""
        try:
            data_repo = Path(config_var.get()["global"]["paths"]["data"]) / "repo"
            repo_dir = data_repo / repo_path
            if not repo_dir.exists():
                logger.warning("仓库目录不存在: %s", repo_dir)
                return None
            repo = Repo.from_repodir(repo_dir)
            # 获取原子内容预览
            content_preview = ""
            payload = repo.payload
            # 查找对应 ident 的 payload 条目
            for ident_key, content in payload:
                if ident_key == fav.ident:
                    # 截断过长的内容
                    if isinstance(content, dict) and "content" in content:
                        text = content["content"]
                    else:
                        text = str(content)
                    if len(text) > 100:
                        content_preview = text[:100] + "..."
                    else:
                        content_preview = text
                    break
            return {
                "title": repo.manifest["title"],
                "content_preview": content_preview,
            }
        except Exception as e:
            logger.error("获取仓库信息失败: %s", e)
            return None

    def _format_time(self, timestamp: int) -> str:
        """格式化时间戳"""
        from datetime import datetime

        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        button_id = event.button.id
        if button_id and button_id.startswith("remove-"):
            # 提取编码后的键
            key = button_id[7:]  # 去掉 "remove-" 前缀
            try:
                repo_path, ident = self._decode_favorite_key(key)
                self._remove_favorite(repo_path, ident)
            except Exception as e:
                logger.error("解析按钮 ID 失败: %s", e)
                self.app.notify("操作失败: 无效的按钮标识", severity="error")

    def _remove_favorite(self, repo_path: str, ident: str) -> None:
        """移除收藏项"""
        if favorite_manager.remove(repo_path, ident):
            self.app.notify(f"已移除收藏: {ident}", severity="information")
            # 重新加载列表
            self._load_favorites()
            # 刷新界面
            self._refresh_list()
        else:
            self.app.notify(f"移除失败: {ident}", severity="error")

    def _refresh_list(self) -> None:
        """刷新列表显示"""
        container = self.query_one("#favorites-container")
        # 清空容器
        for child in container.children:
            child.remove()
        # 重新组合
        if not self.favorites:
            container.mount(Label("暂无收藏", classes="empty-label"))
            container.mount(Static("使用 * 键在记忆界面中添加收藏。"))
        else:
            container.mount(
                Label(f"共 {len(self.favorites)} 个收藏项", classes="count-label")
            )
            list_view = ListView(id="favorites-list")
            container.mount(list_view)
            for fav in self.favorites:
                list_view.append(self._create_favorite_item(fav))

    def action_go_back(self) -> None:
        """返回上一屏幕"""
        self.app.pop_screen()

    def action_toggle_dark(self) -> None:
        """切换暗黑模式"""
        self.app.dark = not self.app.dark  # type: ignore
