"""Memorization preparation screen"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Markdown,
    Static,
    Sparkline,
)
from textual.lazy import Reveal

from textual import events, on

import heurams.kernel.particles as pt
from heurams.context import *
from heurams.context import config_var
from heurams.i18n import _
from heurams.kernel.repolib import *
from heurams.kernel.algorithms import algorithms
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class PreparationScreen(Screen):

    SUB_TITLE = _("Prepare Repository")

    BINDINGS = [
        ("q", "go_back", _("Back")),
        ("p", "precache", _("Cache")),
        ("d", "toggle_dark", ""),
        ("0,1,2,3", "app.push_screen('about')", ""),
    ]

    CSS_PATH = rootdir / "interface" / "css" / "screens" / "preparation.tcss"

    def __init__(self, repo: Repo) -> None:
        super().__init__(name=None, id=None, classes=None)
        self.repo = repo
        self.load_data()

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def compose(self) -> ComposeResult:
        from heurams.services.attic import Attic

        a = Attic("ana", {"openpre": 0})
        a.data["openpre"] += 1
        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(id="main_container"):
            yield Markdown(
                _("**Ready**: `{title}`\n").format(title=self.repo.manifest['title']), id="title"
            )
            yield Label(_("Repo path: {path}").format(path=self.repo.source))
            yield Label(
                _("Progress: {touched}/{total} [{pct}%]").format(
                    touched=self.repo.progress['touched'],
                    total=len(self.repo),
                    pct=round(self.repo.progress['touched'] / self.repo.progress['total'] * 100, 1)
                )
            )
            yield Label(
                _("Scheduling algorithm: {algo} {desc}").format(
                    algo=self.repo.config["algorithm"],
                    desc=algorithms[self.repo.config["algorithm"]].desc
                )
            )
            yield Label(
                _("Study count: {total} = {review} [d][Review][/d] + {new} [d][New][/d]\n").format(
                    total=self.repo.preview['review'] + self.scheduled_num,
                    review=self.repo.preview['review'],
                    new=self.scheduled_num,
                ),
                id="schnum_label",
            )

            yield Horizontal(
                Button(
                    _("Start Memorizing"),
                    id="start_memorizing_button",
                    variant="primary",
                    classes="btn",
                ),
                Button(
                    _("Manage Cache"),
                    id="precache_button",
                    variant="success",
                    classes="btn",
                ),
                id="operations",
            )

            yield Static()
            yield Sparkline(self.spark_line_arr, summary_function=max)
            # yield Static(str(self.spark_line_arr))
            with Reveal(ScrollableContainer(id="previewer_container")):
                for i in self.content.splitlines():
                    yield Static(i, classes="unit-statline")
        yield Footer()

    def load_data(self):
        self.scheduled_num = self.repo.config["scheduled_num"]
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

    router = rt.Router(atoms_to_provide)
    memscreen = MemScreen(router=router, repo=repo)
    app.push_screen(memscreen)
