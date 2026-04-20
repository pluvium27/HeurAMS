"""记忆准备界面"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Markdown,
    Static,
    Rule,
    Sparkline,
)

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *
from heurams.context import config_var
from heurams.kernel.repolib import *
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class PreparationScreen(Screen):

    SUB_TITLE = "准备记忆集"

    BINDINGS = [
        ("q", "go_back", "返回"),
        ("p", "precache", "预缓存音频"),
        ("d", "toggle_dark", ""),
        ("0,1,2,3", "app.push_screen('about')", ""),
    ]

    scheduled_num = reactive(config_var.get()["interface"]["global"]["scheduled_num"])

    def __init__(self, repo: Repo) -> None:
        super().__init__(name=None, id=None, classes=None)
        self.repo = repo
        self.load_data()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="vice_container"):
            yield Label(f"准备就绪: [b]{self.repo.manifest['title']}[/b]\n")
            yield Label(f"[b]仓库路径: {self.repo.source}[/b]")
            yield Label(f"\n单元数量: {len(self.repo)}\n")
            yield Label(f"最小记忆分组: {self.scheduled_num}\n", id="schnum_label")

            yield Button(
                "开始记忆",
                id="start_memorizing_button",
                variant="primary",
                classes="start-button",
            )
            yield Button(
                "预缓存音频",
                id="precache_button",
                variant="success",
                classes="precache-button",
            )

            yield Static()
            yield Sparkline(self.spark_line_arr, summary_function=max)
            yield Rule()
            # yield Static(str(self.spark_line_arr))
            yield Static(f"单元状态预览:\n")
            for i in self.content.splitlines():
                yield Static(i, classes="full")
        yield Footer()

    # def watch_scheduled_num(self, old_scheduled_num, new_scheduled_num):
    #    logger.debug("响应", old_scheduled_num, "->", new_scheduled_num)
    #    try:
    #        one = self.query_one("#schnum_label")
    #        one.update(f"单次记忆数量: {new_scheduled_num}") # type: ignore
    #    except:
    #        pass

    def load_data(self):
        content = ""
        spark_line_arr = []
        for i in self.repo.ident_index:
            n = pt.Nucleon.from_data(
                nucleonic_data=self.repo.nucleonic_data_lict.get_itemic_unit(i)
            )
            e = pt.Electron.from_data(
                electronic_data=self.repo.electronic_data_lict.get_itemic_unit(i),
                algo_name=self.repo.config["algorithm"],
            )
            statstr = ""

            if e.is_activated():
                statstr = "[#00ff00]A[/]"
                if e.is_due():
                    statstr = "[#ffff00]R[/]"
                # statstr += ('[dim]' + str(e.rept(real_rept=True)).zfill(2)+'[/]')
            else:
                statstr = "[#ff0000]U[/]"
            spark_line_arr.append(e.rept(real_rept=True))
            content += f" {statstr} {n['content'].replace('/', '')}  \n"
        self.content = content
        self.spark_line_arr = spark_line_arr

    def action_go_back(self):
        self.app.pop_screen()

    def action_precache(self):
        from ..screens.precache import PrecachingScreen

        lst = list()
        for i in self.repo.ident_index:
            lst.append(
                pt.Nucleon.from_data(self.repo.nucleonic_data_lict.get_itemic_unit(i))
            )
        precache_screen = PrecachingScreen(
            nucleons=lst, desc=self.repo.manifest["title"]
        )
        self.app.push_screen(precache_screen)

    def action_quit_app(self):
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        logger.debug("按下按钮")
        if event.button.id == "start_memorizing_button":
            launch(repo=self.repo, app=self.app, scheduled_num=self.scheduled_num)

        elif event.button.id == "precache_button":
            self.action_precache()


def launch(repo, app, scheduled_num):
    if scheduled_num == -1:
        scheduled_num = config_var.get()["interface"]["global"]["scheduled_num"]
    atoms = list()
    for i in repo.ident_index:
        n = pt.Nucleon.from_data(
            nucleonic_data=repo.nucleonic_data_lict.get_itemic_unit(i)
        )
        e = pt.Electron.from_data(
            electronic_data=repo.electronic_data_lict.get_itemic_unit(i),
            algo_name=repo.config["algorithm"],
        )
        a = pt.Atom(n, e, repo.orbitic_data)
        atoms.append(a)

    atoms_to_provide = list()
    left_new = scheduled_num
    for i in atoms:
        i: pt.Atom
        if i.registry["electron"].is_activated():
            if i.registry["electron"].is_due():
                atoms_to_provide.append(i)
        else:
            left_new -= 1
            if left_new >= 0:
                atoms_to_provide.append(i)
    import heurams.kernel.reactor as rt

    from .memoqueue import MemScreen

    pheser = rt.Phaser(atoms_to_provide)
    save_func = repo.persist_to_repodir
    memscreen = MemScreen(pheser, save_func, repo=repo)
    app.push_screen(memscreen)
