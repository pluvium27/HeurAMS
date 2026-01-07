"""记忆准备界面"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Label, Markdown, Static

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

    scheduled_num = reactive(config_var.get()["scheduled_num"])

    def __init__(self, repo: Repo, repostat: dict) -> None:
        super().__init__(name=None, id=None, classes=None)
        self.repo = repo
        self.repostat = repostat

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="vice_container"):
            yield Label(f"准备就绪: [b]{self.repostat['title']}[/b]\n")
            yield Label(
                f"仓库路径: {config_var.get()['paths']['data']}/repo/[b]{self.repostat['dirname']}[/b]"
            )
            yield Label(f"\n单元数量: {len(self.repo)}\n")
            yield Label(f"单次记忆数量: {self.scheduled_num}", id="schnum_label")

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

            yield Static(f"\n单元预览:\n")
            for i in self._get_full_content().replace("/", "").splitlines():
                yield Static(i, classes="full")
        yield Footer()

    # def watch_scheduled_num(self, old_scheduled_num, new_scheduled_num):
    #    logger.debug("响应", old_scheduled_num, "->", new_scheduled_num)
    #    try:
    #        one = self.query_one("#schnum_label")
    #        one.update(f"单次记忆数量: {new_scheduled_num}") # type: ignore
    #    except:
    #        pass

    def _get_full_content(self):
        content = ""
        for i in self.repo.ident_index:
            n = pt.Nucleon.create_on_nucleonic_data(
                nucleonic_data=self.repo.nucleonic_data_lict.get_itemic_unit(i)
            )
            content += f"  • {n['content']}  \n"
        return content

    def action_go_back(self):
        self.app.pop_screen()

    def action_precache(self):
        from ..screens.precache import PrecachingScreen

        lst = list()
        for i in self.repo.ident_index:
            lst.append(
                pt.Nucleon.create_on_nucleonic_data(
                    self.repo.nucleonic_data_lict.get_itemic_unit(i)
                )
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
            atoms = list()
            for i in self.repo.ident_index:
                n = pt.Nucleon.create_on_nucleonic_data(
                    nucleonic_data=self.repo.nucleonic_data_lict.get_itemic_unit(i)
                )
                e = pt.Electron.create_on_electonic_data(
                    electronic_data=self.repo.electronic_data_lict.get_itemic_unit(i)
                )
                a = pt.Atom(n, e, self.repo.orbitic_data)
                atoms.append(a)

            atoms_to_provide = list()
            left_new = self.scheduled_num
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
            save_func = self.repo.persist_to_repodir
            memscreen = MemScreen(pheser, save_func, repo=self.repo)
            self.app.push_screen(memscreen)

        elif event.button.id == "precache_button":
            self.action_precache()
