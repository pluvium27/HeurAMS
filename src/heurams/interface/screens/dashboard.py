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

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.repostat = {}
        self.title2dirname = {}
        self.title2repo = {}
        self.dirname2repo = {}
        self._load_data()

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Horizontal(
                Vertical(
                    Label(f'欢迎使用 "潜进" 版本 {version.ver}'),
                    Label(
                        f"当前 UNIX 日时间戳: {timer.get_daystamp()}"
                    ),
                    Label(f"应用时区修正: UTC+{config_var.get()['timezone_offset'] / 3600}"),
                    Label(f"全局算法设置: {config_var.get()['algorithm']['default']}"),
                    classes="column infview",
                ),
                Vertical(
                    Label(f"已加载 {len(self.repostat)} 个单元集", classes='dataview'),
                    Label(f"共计 {reduce(lambda x, y: x + y, map(lambda x: x.get('unit_sum'), self.repostat.values()))} 个单元", classes='dataview'),
                    Label(f"已激活 {reduce(lambda x, y: x + y, map(lambda x: x.get('activated_sum'), self.repostat.values()))} 个单元", classes='dataview'),
                    Label(f"终端尺寸: {os.get_terminal_size()[0]}x{os.get_terminal_size()[1]}"),
                    classes="column dataview",
                ),
                id="dashboardtop"
            )

            yield ListView(id="repo-list", classes="repo-list-view")
            yield Label(f'"潜进" 启发式辅助记忆调度器 版本 {version.ver} {version.stage.capitalize()}')
        yield Footer()

    def _load_data(self):
        self.repo_dirs = Repo.probe_valid_repos_in_dir(
            Path(config_var.get()["paths"]["data"]) / "repo"
        )
        for repo_dir in self.repo_dirs:
            repo = Repo.create_from_repodir(repo_dir)
            self._analyse_repo(repo)

    def _analyse_repo(self, repo: Repo):
        dirname = repo.source.name  # type: ignore
        title = repo.manifest["title"]
        is_due = 0
        unit_sum = len(repo)
        activated_sum = 0
        nextdate = float('inf')
        for i in repo.ident_index:
            nucleon = pt.Nucleon.create_on_nucleonic_data(
                nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i)
            )
            electron = pt.Electron.create_on_electonic_data(
                electronic_data=repo.electronic_data_lict.get_itemic_unit(i)
            )
            if electron.is_activated():
                activated_sum += 1
                if electron.is_due():
                    is_due = 1
                nextdate = min(nextdate, electron.nextdate())
        is_unfinished = unit_sum > activated_sum
        if is_unfinished:
            nextdate = min(nextdate, timer.get_daystamp())
        need_to_study = is_due or is_unfinished
        prompt = f"{title}\0\n  进度: {activated_sum}/{unit_sum} ({round(activated_sum/unit_sum*100)}%)\n  {'需要学习' if need_to_study else '无需操作'}"
        stat = {
            "is_due": is_due,
            "unit_sum": unit_sum,
            "title": title,
            "activated_sum": activated_sum,
            "nextdate": nextdate,
            "is_unfinished": is_unfinished,
            "need_to_study": need_to_study,
            "prompt": prompt,
            "dirname": dirname,
        }
        self.repostat[dirname] = stat
        self.title2dirname[title] = dirname
        self.title2repo[title] = repo
        self.dirname2repo[dirname] = repo

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        repo_list_widget = self.query_one("#repo-list", ListView)

        # 按下次复习时间排序
        repodirs = sorted(
            self.repo_dirs,
            key=lambda f: self.repostat[f.name]["nextdate"],
            reverse=True,
        )
        repotitles = map(lambda f: self.repostat[f.name]["title"], repodirs)
        # 填充列表
        if not repodirs:
            repo_list_widget.append(
                ListItem(
                    Static(
                        "在 ./data/repo/ 中未找到任何仓库.\n"
                        "请导入仓库后重启应用, 或者新建空的仓库."
                    )
                )
            )
            repo_list_widget.disabled = True
            return

        for repotitle in repotitles:
            prompt = self.repostat[self.title2dirname[repotitle]]["prompt"]
            list_item = ListItem(Label(prompt), Button(f"开始学习", flat=True, variant="primary", classes="repo_listitem_btn", id=f"launch_{self.repostat[self.title2dirname[repotitle]]['dirname']}"), classes="repo_listitem")
            repo_list_widget.append(list_item)

            # if not self.stay_enabled[repodir]:
            #    list_item.disabled = True

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return

        selected_label = event.item.query_one(Label)
        label_text = str(selected_label.render())

        if "未找到任何仓库" in label_text:
            return

        # 提取文件名
        selected_repotitle = label_text.partition("\0")[0].replace("*", "")
        selected_repo = self.title2repo[label_text.partition("\0")[0].replace("*", "")]

        # 跳转到准备屏幕
        self.app.push_screen(
            PreparationScreen(
                selected_repo, self.repostat[self.title2dirname[selected_repotitle]]
            )
        )

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()

    def action_open_navigator(self) -> None:
        """打开导航器"""
        self.app.push_screen(NavigatorScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        logger.debug(f"event.button.id: {event.button.id}")
        """处理按钮点击事件"""
        if str(event.button.id).startswith("launch_"): # type: ignore
            from .preparation import launch
            launch(repo=self.dirname2repo[event.button.id[7:]], app=self.app, scheduled_num=-1) # type: ignore
            # TODO: 这样启动的记忆实例的状态机无法绑定到 PreparationScreen 中