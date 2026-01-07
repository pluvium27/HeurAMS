"""仓库编辑器, 使用TextArea控件等实现仓库配置编辑"""

import json
from pathlib import Path
from typing import Optional

import toml
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
    TextArea,
)

from heurams.context import config_var
from heurams.kernel.repolib import Repo
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class RepoEditorScreen(Screen):
    """仓库编辑器屏幕"""

    SUB_TITLE = "仓库编辑器"

    BINDINGS = [
        ("q", "go_back", "返回"),
        ("s", "save_file", "保存"),
        ("r", "reload_file", "重载"),
        ("d", "toggle_dark", ""),
    ]

    # 当前选择的仓库路径
    selected_repo_path: reactive[Optional[Path]] = reactive(None)
    # 当前选择的文件名
    selected_filename: reactive[Optional[str]] = reactive(None)
    # 文件内容
    file_content: reactive[str] = reactive("")

    def __init__(
        self,
        repo: Optional[Repo] = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.repo = repo
        self.repo_dir: Optional[Path] = None
        self.file_list = []
        if repo is not None and repo.source is not None:
            self.repo_dir = repo.source
            self._load_file_list()
        # selected_repo_path 将在 on_mount 中设置，避免触发watch时组件未就绪

    def _load_file_list(self) -> None:
        """加载仓库目录下的文件列表"""
        if self.repo_dir is None:
            return
        self.file_list = []
        for fname in Repo.file_mapping.values():
            fpath = self.repo_dir / fname
            if fpath.exists():
                self.file_list.append(fname)
        # 也可能存在其他文件，但暂时只支持标准文件
        self.file_list.sort()

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        with Container(id="main_container"):
            with Horizontal(id="top_panel"):
                # 左侧: 仓库选择
                with Vertical(id="repo_selector", classes="panel"):
                    yield Label("仓库列表", classes="panel-title")
                    yield ListView(
                        *[
                            ListItem(Label(repo_dir.name))
                            for repo_dir in self._get_repo_dirs()
                        ],
                        id="repo_list",
                        classes="list-view",
                    )
                # 中间: 文件列表
                with Vertical(id="file_selector", classes="panel"):
                    yield Label("文件列表", classes="panel-title")
                    yield ListView(
                        *[ListItem(Label(fname)) for fname in self.file_list],
                        id="file_list",
                        classes="list-view",
                    )
                # 右侧: 编辑区域
                with Vertical(id="editor_panel", classes="panel"):
                    yield Label("编辑文件", classes="panel-title")
                    yield TextArea(
                        id="text_editor",
                        language="plaintext",
                        classes="text-editor",
                    )
                    with Horizontal(id="button_bar"):
                        yield Button("保存", id="save_button", variant="primary")
                        yield Button("重载", id="reload_button", variant="default")
                        yield Button("返回", id="back_button", variant="error")
        yield Footer()

    def _get_repo_dirs(self) -> list[Path]:
        """获取data/repo/下所有有效仓库目录"""
        repo_root = Path(config_var.get()["paths"]["data"]) / "repo"
        repo_dirs = []
        if repo_root.exists():
            for entry in repo_root.iterdir():
                if entry.is_dir():
                    # 检查是否存在 manifest.toml
                    if (entry / "manifest.toml").exists():
                        repo_dirs.append(entry)
        return repo_dirs

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        # 如果已有仓库，设置 selected_repo_path 以触发watch（此时组件已就绪）
        if self.repo_dir is not None:
            self.selected_repo_path = self.repo_dir
        # 焦点放在仓库列表
        self.query_one("#repo_list", ListView).focus()

    def watch_selected_repo_path(
        self, old_path: Optional[Path], new_path: Optional[Path]
    ) -> None:
        """当选择的仓库路径变化时，加载文件列表"""
        if new_path is None:
            self.file_list = []
            self.selected_filename = None
            self.file_content = ""
            return
        self.repo_dir = new_path
        self._load_file_list()
        # 如果组件已挂载，更新UI
        if self.is_mounted:
            file_list_view = self.query_one("#file_list", ListView)
            file_list_view.clear()
            for fname in self.file_list:
                file_list_view.append(ListItem(Label(fname)))
            # 清空编辑器
            self.query_one("#text_editor", TextArea).text = ""
        self.selected_filename = None

    def watch_selected_filename(
        self, old_name: Optional[str], new_name: Optional[str]
    ) -> None:
        """当选择的文件名变化时，加载文件内容"""
        if new_name is None or self.repo_dir is None:
            self.file_content = ""
            return
        file_path = self.repo_dir / new_name
        if not file_path.exists():
            self.notify(f"文件不存在: {new_name}", severity="error")
            return
        try:
            content = file_path.read_text(encoding="utf-8")
            self.file_content = content
            # 如果组件已挂载，更新编辑器
            if self.is_mounted:
                editor = self.query_one("#text_editor", TextArea)
                editor.text = content
                # 根据文件后缀设置语言
                if new_name.endswith(".toml"):
                    editor.language = "toml"
                elif new_name.endswith(".json"):
                    editor.language = "json"
                else:
                    editor.language = "plaintext"
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            self.notify(f"读取文件失败: {e}", severity="error")

    def watch_file_content(self, old_content: str, new_content: str) -> None:
        """当文件内容变化时更新编辑器（仅当外部改变时）"""
        # 目前不需要做任何事情，因为编辑器内容已绑定
        pass

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return
        list_id = event.list_view.id
        selected_label = event.item.query_one(Label)
        selected_text = str(selected_label.render())

        if list_id == "repo_list":
            # 用户选择了仓库
            repo_root = Path(config_var.get()["paths"]["data"]) / "repo"
            selected_dir = repo_root / selected_text
            if selected_dir.exists():
                self.selected_repo_path = selected_dir
        elif list_id == "file_list":
            # 用户选择了文件
            if self.repo_dir is None:
                self.notify("请先选择仓库", severity="warning")
                return
            self.selected_filename = selected_text

    def on_button_pressed(self, event) -> None:
        """处理按钮点击事件"""
        event.stop()
        if event.button.id == "save_button":
            self.action_save_file()
        elif event.button.id == "reload_button":
            self.action_reload_file()
        elif event.button.id == "back_button":
            self.action_go_back()

    def action_save_file(self) -> None:
        """保存当前编辑的文件"""
        if self.repo_dir is None or self.selected_filename is None:
            self.notify("未选择仓库或文件", severity="warning")
            return
        file_path = self.repo_dir / self.selected_filename
        editor = self.query_one("#text_editor", TextArea)
        new_content = editor.text
        # 验证格式
        try:
            if self.selected_filename.endswith(".toml"):
                toml.loads(new_content)  # 验证TOML
            elif self.selected_filename.endswith(".json"):
                json.loads(new_content)  # 验证JSON
        except Exception as e:
            self.notify(f"格式错误: {e}", severity="error")
            return
        # 写入文件
        try:
            file_path.write_text(new_content, encoding="utf-8")
            self.notify("保存成功", severity="information")
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            self.notify(f"保存文件失败: {e}", severity="error")

    def action_reload_file(self) -> None:
        """重新加载当前文件（放弃修改）"""
        if self.repo_dir is None or self.selected_filename is None:
            self.notify("未选择仓库或文件", severity="warning")
            return
        file_path = self.repo_dir / self.selected_filename
        try:
            content = file_path.read_text(encoding="utf-8")
            editor = self.query_one("#text_editor", TextArea)
            editor.text = content
            self.notify("已重载", severity="information")
        except Exception as e:
            logger.error(f"重载文件失败: {e}")
            self.notify(f"重载文件失败: {e}", severity="error")

    def action_go_back(self) -> None:
        """返回上一屏幕"""
        self.app.pop_screen()

    def action_toggle_dark(self) -> None:
        """切换暗色模式"""
        self.app.dark = not self.app.dark
