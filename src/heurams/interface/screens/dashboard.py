"""仪表盘界面"""

import pathlib

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import (Button, Footer, Header, Label, ListItem, ListView,
                             Static)

import heurams.services.timer as timer
import heurams.services.version as version
from heurams.context import *
from heurams.kernel.particles import *
from heurams.kernel.repolib import *
from heurams.services.logger import get_logger

from .about import AboutScreen
from .preparation import PreparationScreen

logger = get_logger(__name__)


class DashboardScreen(Screen):
    """主仪表盘屏幕"""

    SUB_TITLE = "仪表盘"

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
        self._load_data()

    def compose(self) -> ComposeResult:
        """组合界面组件"""
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Label('欢迎使用 "潜进" 启发式辅助记忆调度器', classes="title-label"),
            Label(f"当前 UNIX 日时间戳: {timer.get_daystamp()}"),
            Label(f'时区修正: UTC+{config_var.get()["timezone_offset"] / 3600}'),
            Label(f"使用算法: {config_var.get()['algorithm']['default']}"),
            Label("选择待学习或待修改的仓库:", classes="title-label"),
            ListView(id="repo-list", classes="repo-list-view"),
            Label(
                f'"潜进" 启发式辅助记忆调度器 | 版本 {version.ver} '
            ),
        )
        yield Footer()

    def _load_data(self):
        self.repo_dirs = Repo.probe_vaild_repos_in_dir(Path(config_var.get()['paths']['data']) / 'repo')
        for repo_dir in self.repo_dirs:
            repo = Repo.create_from_repodir(repo_dir)
            self._analyse_repo(repo)

    def _analyse_repo(self, repo: Repo):
        dirname = repo.source.name # type: ignore
        title = repo.manifest["title"]
        is_due = 0
        unit_sum = len(repo)
        activated_sum = 0
        nextdate = 0x3f3f3f3f
        is_unfinished = (unit_sum > activated_sum)
        for i in repo.ident_index:
            nucleon = pt.Nucleon.create_on_nucleonic_data(nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i))
            electron = pt.Electron.create_on_electonic_data(electronic_data=repo.electronic_data_lict.get_itemic_unit(i))
            if electron.is_activated():
                activated_sum += 1
                if electron.is_due():
                    is_due = 1
                nextdate = min(nextdate, electron.nextdate())
        if is_unfinished:
            nextdate = min(nextdate, timer.get_daystamp())
        need_to_study = is_due or is_unfinished
        prompt = f"{title}\0\n  进度: {activated_sum}/{unit_sum}\n  {"需要学习" if need_to_study else "无需操作"}"
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

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        repo_list_widget = self.query_one("#repo-list", ListView)

        # 按下次复习时间排序
        repodirs = sorted(
            self.repo_dirs,
            key=lambda f: self.repostat[f.name]['nextdate'],
            reverse=True,
        )
        repotitles = map(lambda f: self.repostat[f.name]['title'], repodirs)
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
            prompt = self.repostat[self.title2dirname[repotitle]]['prompt']
            list_item = ListItem(Label(prompt))
            repo_list_widget.append(list_item)

            #if not self.stay_enabled[repodir]:
            #    list_item.disabled = True

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return

        selected_label = event.item.query_one(Label)
        label_text = str(selected_label.renderable)

        if "未找到任何仓库" in label_text:
            return

        # 提取文件名
        selected_repotitle = label_text.partition("\0")[0].replace("*", "")
        selected_repo = self.title2repo[label_text.partition("\0")[0].replace("*", "")]
        

        # 跳转到准备屏幕
        self.app.push_screen(PreparationScreen(selected_repo, self.repostat[self.title2dirname[selected_repotitle]]))

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()
