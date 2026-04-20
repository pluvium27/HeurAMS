"""仪表盘界面"""

from functools import reduce
import pathlib
from pathlib import Path
import os

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static
from textual.layouts import horizontal

import heurams.kernel.particles as pt
import heurams.services.timer as timer
import heurams.services.version as version
from heurams.context import *
from heurams.kernel.particles import *
from heurams.kernel.repolib import *
from heurams.kernel.algorithms import algorithms
from heurams.services.logger import get_logger

from .about import AboutScreen
from .navigator import NavigatorScreen
from .preparation import PreparationScreen

logger = get_logger(__name__)


class DashboardScreen(Screen):
    """主仪表盘屏幕"""

    SUB_TITLE = "仪表盘"
    BINDINGS = [
        ("q", "go_back", "返回"),
    ]

    CSS_PATH = Path(__file__).parent.parent / 'css' / "screens" / "dashboard.tcss"
    
    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.repolink = {}

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        self._load_data()
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Horizontal(  # 顶部的状态
                Vertical(
                    Label(f'欢迎使用 "潜进" 版本 {version.ver}'),
                    Label(f"当前 UNIX 日时间戳: {timer.get_daystamp()}"),
                    Label(
                        f"应用时区修正: UTC+{config_var.get()['services']['timer']['timezone_offset'] / 3600}"
                    ),
                    Label(
                        f"默认算法设置: {config_var.get()['interface']['global']['algorithm']}"
                    ),
                    classes="left",
                ),
                Vertical(
                    Label(f"已加载 {len(self.repos)} 个单元集"),
                    Label(
                        f"共计 {reduce(lambda x, y: x + y, map(lambda x: x.progress['total'], self.repos))} 个单元"
                    ),
                    Label(
                        f"已激活 {reduce(lambda x, y: x + y, map(lambda x: x.progress['touched'], self.repos))} 个单元"
                    ),
                    Label(f""),
                    classes="right",
                ),
                id="header",
            )

            yield ListView(id="repo_list", classes="repo-list")  # 单元集选择

            yield Label(
                f'"潜进" 启发式辅助记忆调度器 版本 {version.ver} {version.stage.capitalize()}'
            )  # 版本信息
        yield Footer()

    def _load_data(self):
        repo_dirs = Repo.probe_valid_repos_in_dir(
            Path(config_var.get()["global"]["paths"]["repo"])
        )
        self.repos = list(map(Repo.from_repodir, repo_dirs))
        for repo in self.repos:
            self._analyse_repo(repo)

    def _analyse_repo(self, repo: Repo):
        # need_review: 需要/不需要学习
        # nearest_review_time: 最近下次学习时间
        # progress: 进度
        # algotype: 算法类型
        ## initial_time: 起始时间
        # package: 包名
        # prompt: 最终呈现信息
        repo.package = repo.manifest["package"]
        repo.nearest_review_time = float("inf")
        repo.progress = {
            "total": repo.data_length,
            "touched": 0,
        }
        initial_time = float("inf")
        for i in range(repo.data_length):
            e = pt.Electron.from_data(electronic_data=repo.electronic_data_lict[i], algo_name=repo.config['algorithm'])
            n = pt.Nucleon.from_data(repo.nucleonic_data_lict[i])
            if e.is_activated():
                repo.progress["touched"] += 1
                repo.nearest_review_time = min(repo.nearest_review_time, e.nextdate())
                # initial_time = min(initial_time, e.)
        repo.need_review = timer.get_daystamp() >= repo.nearest_review_time
        repo.prompt = f"""{repo.manifest['title']} ({repo.config['algorithm']})
  进度: {repo.progress['touched']}/{repo.progress['total']} ({round(repo.progress['touched']/repo.progress['total']*100, 1)}%)
  {'需要学习' if repo.need_review else "无需操作"}
        """

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        repo_list_widget = self.query_one("#repo_list", ListView)

        # 按下次复习时间排序
        repodirs = sorted(
            self.repos,
            key=lambda r: r.nearest_review_time,
            reverse=True,
        )
        repotitles = map(lambda f: self.repostat[f.name]["title"], repodirs)
        # 填充列表
        if not repodirs:
            repo_list_widget.append(
                ListItem(
                    Static(
                        f"在 {config_var.get()['global']['paths']['repo']} 中未找到任何仓库.\n"
                        "请导入仓库后重启应用, 或者新建空的仓库."
                    ),
                    id="not-found",
                )
            )
            repo_list_widget.disabled = True
            return

        for r in self.repos:
            self.repolink[str(id(r))] = r  # 用于规避 ctype id 对象还原
            list_item = ListItem(
                Label(r.prompt),
                Button(
                    f"开始学习",
                    flat=True,
                    variant="primary",
                    id=f"slaunch_repo_{id(r)}",
                    classes="repo-list-item-shortcut",
                ),
                classes="repo-list-item",
                id=f"launch_repo_{id(r)}",
            )
            repo_list_widget.append(list_item)

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return

        if "not-found" == event.item.id:
            return

        # 还原对象
        selected_repo = self.repolink[event.item.id.lstrip("launch_repo_")]

        # 跳转到准备屏幕
        self.app.push_screen(PreparationScreen(selected_repo))

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()

    def action_open_navigator(self) -> None:
        """打开导航器"""
        self.app.push_screen(NavigatorScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        logger.debug(f"event.button.id: {event.button.id}")
        if event.button.id.startswith("slaunch_repo_"):  # type: ignore
            from .preparation import launch

            launch(repo=self.repolink[event.button.id.lstrip("slaunch_repo_")], app=self.app, scheduled_num=-1)  # type: ignore
            # TODO: 这样启动的记忆实例的状态机无法绑定到 PreparationScreen 中
