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

    def __init__(self, nucleon_file: pathlib.Path, electron_file: pathlib.Path) -> None:
        super().__init__(name=None, id=None, classes=None)
        self.nucleon_file = nucleon_file
        self.electron_file = electron_file
        self.nucleons_with_orbital = pt.load_nucleon(self.nucleon_file)
        self.electrons = pt.load_electron(self.electron_file)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="vice_container"):
            yield Label(f"准备就绪: [b]{self.nucleon_file.stem}[/b]\n")
            yield Label(
                f"内容源文件: {config_var.get()['paths']['nucleon_dir']}/[b]{self.nucleon_file.name}[/b]"
            )
            yield Label(
                f"元数据文件: {config_var.get()['paths']['electron_dir']}/[b]{self.electron_file.name}[/b]"
            )
            yield Label(f"\n单元数量: {len(self.nucleons_with_orbital)}\n")
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
            yield Markdown(self._get_full_content().replace("/", ""), classes="full")
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
        for nucleon, orbital in self.nucleons_with_orbital:
            nucleon: pt.Nucleon
            # print(nucleon.payload)
            content += " - " + nucleon["content"] + "  \n"
        return content

    def action_go_back(self):
        self.app.pop_screen()

    def action_precache(self):
        from ..screens.precache import PrecachingScreen

        lst = list()
        for i in self.nucleons_with_orbital:
            lst.append(i[0])
        precache_screen = PrecachingScreen(lst)
        self.app.push_screen(precache_screen)

    def action_quit_app(self):
        self.app.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        logger.debug("按下按钮")
        if event.button.id == "start_memorizing_button":
            atoms = list()
            for nucleon, orbital in self.nucleons_with_orbital:
                atom = pt.Atom(nucleon.ident)
                atom.link("nucleon", nucleon)
                try:
                    atom.link("electron", self.electrons[nucleon.ident])
                except KeyError:
                    atom.link("electron", pt.Electron(nucleon.ident))
                atom.link("orbital", orbital)
                atom.link("nucleon_fmt", "toml")
                atom.link("electron_fmt", "json")
                atom.link("orbital_fmt", "toml")
                atom.link("nucleon_path", self.nucleon_file)
                atom.link("electron_path", self.electron_file)
                atom.link("orbital_path", None)
                atoms.append(atom)
            atoms_to_provide = list()
            left_new = self.scheduled_num
            for i in atoms:
                i: pt.Atom
                if i.registry["electron"].is_due():
                    atoms_to_provide.append(i)
                else:
                    if i.registry["electron"].is_activated():
                        pass
                    else:
                        left_new -= 1
                        if left_new >= 0:
                            atoms_to_provide.append(i)
            logger.debug(f"ATP: {atoms_to_provide}")
            from .memoqueue import MemScreen

            memscreen = MemScreen(atoms_to_provide)
            self.app.push_screen(memscreen)
        elif event.button.id == "precache_button":
            self.action_precache()
