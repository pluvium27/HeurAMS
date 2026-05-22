"""Dashboard screen"""

from functools import reduce
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static
from textual import events, on
from textual.reactive import reactive

import heurams.kernel.particles as pt
import heurams.services.timer as timer
import heurams.services.version as version
from heurams.context import *
from heurams.i18n import _
from heurams.kernel.particles import *
from heurams.kernel.repolib import *
from heurams.services.logger import get_logger

from .navigator import NavigatorScreen
from .preparation import PreparationScreen

logger = get_logger(__name__)


class DashboardScreen(Screen):
    """Main dashboard screen"""

    SUB_TITLE = _("Dashboard")
    BINDINGS = [
        ("q", "go_back", _("Back")),
    ]

    CSS_PATH = rootdir / "interface" / "css" / "screens" / "dashboard.tcss"

    repolink = reactive({})

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._load_data()

    def compose(self) -> ComposeResult:
        """Compose UI components"""
        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer():
            yield Horizontal(
                Vertical(
                    Label(_("Current daystamp: {ds}").format(ds=timer.get_daystamp())),
                    Label(
                        _("Timezone offset: UTC+{offset}").format(offset=str(config_var.get()['services']['timer']['timezone_offset'] / 3600).removesuffix('.0'))
                    ),
                    Label(
                        _("Default algorithm: {algo}").format(algo=config_var.get()['interface']['global']['algorithm']),
                    ),
                    classes="left",
                ),
                Vertical(
                    Label(_("Loaded {n} repo(s)").format(n=len(self.repos))),
                    Label(
                        _("Total {n} unit(s)").format(n=reduce(lambda x, y: x + y, map(lambda x: x.progress['total'], self.repos)) if self.repos else 0)
                    ),
                    Label(
                        _("Activated {n} unit(s)").format(n=reduce(lambda x, y: x + y, map(lambda x: x.progress['touched'], self.repos)) if self.repos else 0)
                    ),
                    Label(f""),
                    classes="right",
                ),
                id="header",
            )
            yield ListView(id="repo_list", classes="repo-list")
            from heurams.services.attic import Attic

            a = Attic("ana", {"totaltime": 0, "openpuzzles": 0, "puzzles_err": 0})
            yield Label(_("Version {ver}-{stage}").format(ver=version.ver, stage=version.stage))
            yield Label(
                _("Processed {puzzles} puzzles in {time}s, accuracy {accuracy}, speed {speed} puzzle(s)/s").format(
                    puzzles=a.data['openpuzzles'],
                    time=round(a.data['totaltime'], 2),
                    accuracy=_("N/A") if not a.data['openpuzzles'] else str(round(100 * (1 - a.data['puzzles_err']/a.data['openpuzzles']), 2)) + '%',
                    speed=_("N/A") if not a.data['totaltime'] else str(round(a.data['openpuzzles']/a.data['totaltime'], 2)),
                ),
                id="analysis",
            )  # Version info
        yield Footer()

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")
        # https://github.com/Textualize/textual/discussions/4268
        # self.refresh(recompose=True) 此函数有问题且官方不管 而且性能低

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
        ## initial_time: 起始时间
        # package: 包名
        # prompt: 最终呈现信息
        repo.package = repo.manifest["package"]
        repo.nearest_review_time = float("inf")
        repo.progress = {
            "total": repo.data_length,
            "touched": 0,
            "have_activated_ever": False,
        }
        repo.preview = {
            "review": 0,
            "new": repo.config[
                "scheduled_num"
            ],  # TODO: 考虑之后在这里加点运算避免 SM-2 积压, 但现在需要的是直观!
        }
        initial_time = float("inf")
        for i in range(
            repo.data_length
        ):  # TODO: 增加异步性能优化, 但是学习数据属实规模小...
            e = pt.Electron.from_data(
                electronic_data=repo.electronic_data_lict[i],
                algo_name=repo.config["algorithm"],
            )
            # n = pt.Nucleon.from_data(repo.nucleonic_data_lict[i])
            if e.is_activated():
                repo.progress["have_activated_ever"] = True  # 被激活过~
                repo.progress["touched"] += 1
                repo.nearest_review_time = min(repo.nearest_review_time, e.nextdate())
                if timer.get_daystamp() >= e.nextdate():
                    repo.preview["review"] += 1
                # initial_time = min(initial_time, e.)
        repo.need_review = timer.get_daystamp() >= repo.nearest_review_time
        repo.prompt = _(
            """{title} [{algo}]
  [d]Progress: {touched}/{total} ({pct}%)[/d]
  [d]{status}[/d]"""
        ).format(
            title=repo.manifest["title"],
            algo=repo.config["algorithm"],
            touched=repo.progress["touched"],
            total=repo.progress["total"],
            pct=round(repo.progress["touched"] / repo.progress["total"] * 100, 1),
            status=(
                _("Due: {review}R + {new}U").format(
                    review=repo.preview["review"], new=repo.preview["new"]
                )
                if repo.need_review
                else (
                    _("Not started: 0R + {new}U").format(new=repo.preview["new"])
                    if not repo.progress["have_activated_ever"]
                    else _("Up to date")
                )
            ),
        )

    def on_mount(self) -> None:
        """挂载组件时初始化"""
        repo_list_widget = self.query_one("#repo_list", ListView)

        # 按下次复习时间排序
        repodirs = sorted(
            self.repos,
            key=lambda r: r.nearest_review_time,
            reverse=True,  # 紧张的先复习
        )

        # 填充列表
        if not repodirs:
            repo_list_widget.append(
                ListItem(
                    Static(
                        _("No repo directories found in {path}.\nPlease import a repo and restart, or create a new one.").format(path=config_var.get()['global']['paths']['repo'])
                    ),
                    id="not-found",
                )
            )
            repo_list_widget.disabled = True
            return

        for r in self.repos:
            self.repolink[str(r.manifest["package"])] = r  # 用于规避 ctype id 对象还原
            # NOTE: 上一行不要使用 id(), id 可能被重用!
            list_item = ListItem(
                *[Label(line) for line in r.prompt.splitlines()],
                Button(
                    _("Start Learning"),
                    flat=True,
                    variant="primary",
                    id=f"slaunch_repo_{r.manifest['package']}",
                    classes="repo-list-item-shortcut",
                ),
                classes="repo-list-item",
                id=f"launch_repo_{r.manifest['package']}",
            )
            repo_list_widget.append(list_item)

    def on_list_view_selected(self, event) -> None:
        """处理列表项选择事件"""
        if not isinstance(event.item, ListItem):
            return

        if "not-found" == event.item.id:
            return

        # 还原对象
        selected_repo = self.repolink[event.item.id.removeprefix("launch_repo_")]

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
        if event.button.id.startswith("slaunch_repo_"):  # type: ignore
            from .preparation import launch

            launch(repo=self.repolink[event.button.id.removeprefix("slaunch_repo_")], app=self.app, scheduled_num=-1)  # type: ignore
            # TODO: 这样启动的记忆实例的状态机无法绑定到 PreparationScreen 中
