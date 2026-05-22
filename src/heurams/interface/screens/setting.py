"""Settings screen"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    Collapsible,
    Input,
    Switch,
    Select,
)

from textual import events, on

from heurams.context import *
from heurams.i18n import _
from heurams.kernel.particles import *
from heurams.kernel.repolib import *
from heurams.services.logger import get_logger
from heurams.services.textproc import domize, undomize
from heurams.services.epath import epath

logger = get_logger(__name__)


class SettingScreen(Screen):
    """Settings screen"""

    SUB_TITLE = _("Settings")
    BINDINGS = [
        ("q", "go_back", _("Back")),
        ("s", "go_back", _("Settings")),
    ]
    CSS_PATH = rootdir / "interface" / "css" / "screens" / "setting.tcss"

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def compose(self) -> ComposeResult:
        """Compose UI components"""
        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer():
            yield Label("[b]" + _("Settings") + "[/b]")
            for i in config_var.get():
                if i.startswith("_"):
                    continue
                a = self._get_subcfg(f"{i}")
                if a:
                    yield Collapsible(
                        *a,
                        title=i + f'\n[d]{config_var.get().get(f"_{i}_desc", "")}[/d]',
                    )
        yield Label(
            _("Changes are saved immediately when you leave this page, but restart is recommended to ensure the new configuration is applied."),
            classes="foot",
        )
        yield Footer()

    def _get_subcfg(self, parent_epath: str):
        parent = epath(config_var.get(), parent_epath)
        if isinstance(parent, ConfigDict):
            if parent.is_dir:
                lst = list()
                for i in parent:
                    if i.startswith("_"):
                        continue
                    a = self._get_subcfg(f"{parent_epath}.{i}")
                    if a:
                        lst.append(
                            Collapsible(
                                *a, title=i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'
                            )
                        )
                return lst
        if isinstance(parent, dict) or (
            isinstance(parent, ConfigDict) and not parent.is_dir
        ):
            lst = list()
            for i in parent:
                if i.startswith("_"):
                    continue
                if isinstance(parent[i], dict):
                    a = self._get_subcfg(f"{parent_epath}.{i}")
                    if a:
                        lst.append(
                            Collapsible(
                                *a, title=i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'
                            )
                        )
                elif f"_{i}_candidate" in parent:  # 选择框模式
                    if isinstance(parent[f"_{i}_candidate"], dict):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Select(
                                    (
                                        (f"{j}\n[d]{k}[/d]", j)
                                        for j, k in parent[f"_{i}_candidate"].items()
                                    ),
                                    prompt=f'{parent.get(f"{i}", "")}',
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                                classes="setting-item",
                            )
                        )
                    elif isinstance(parent[f"_{i}_candidate"], list):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Select(
                                    ((j, j) for j in parent[f"_{i}_candidate"]),
                                    prompt=f'{parent.get(f"{i}", "")}',
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                                classes="setting-item",
                            )
                        )
                else:
                    if isinstance(parent[i], float):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Input(
                                    value=str(parent[i]),
                                    placeholder=_("Requires a float"),
                                    type="number",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                                classes="setting-item",
                            )
                        )
                    elif isinstance(parent[i], str):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Input(
                                    value=parent[i],
                                    placeholder=_("Requires a string"),
                                    type="text",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                                classes="setting-item",
                            )
                        )
                    elif isinstance(parent[i], bool):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Switch(
                                    value=parent[i],
                                    id=domize(f"{parent_epath}.{i}"),
                                    classes="setting-switch",
                                ),
                                classes="setting-item",
                            )
                        )
                    elif isinstance(parent[i], int):
                        lst.append(
                            Horizontal(
                                Label(i + f'\n[d]{parent.get(f"_{i}_desc", "")}[/d]'),
                                Input(
                                    value=str(parent[i]),
                                    placeholder=_("Requires an integer"),
                                    type="integer",
                                    id=domize(f"{parent_epath}.{i}"),
                                ),
                                classes="setting-item",
                            )
                        )
                    elif isinstance(parent[i], list):
                        pass
                    else:
                        lst.append(Label(_("Unknown type")))
            return lst
        return [Label(_("No sub-items"))]

    def on_mount(self) -> None:
        """挂载组件时初始化"""

    def action_go_back(self) -> None:
        """返回上一屏幕"""
        config_var.get().persist()
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        """退出应用程序"""
        self.app.exit()

    def action_open_navigator(self) -> None:
        """打开导航器"""
        self.app.push_screen(NavigatorScreen())

    def on_input_changed(self, event: Input.Changed) -> None:
        widget_id = event.input.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )

    def on_switch_changed(self, event: Switch.Changed) -> None:
        widget_id = event.switch.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        widget_id = event.select.id
        if not widget_id:
            return
        eepath = undomize(widget_id)
        value = event.value
        epath(
            config_var.get(),
            eepath,
            enable_modify=True,
            new_value=type(epath(config_var.get(), eepath))(value),
        )
