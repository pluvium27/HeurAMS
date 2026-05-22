"""About screen"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Markdown
from textual import events, on

import heurams.services.version as version
from heurams.context import *
from heurams.i18n import _
import platform
import shutil
import os
import sys


class AboutScreen(Screen):
    BINDINGS = [
        ("q", "go_back", _("Back")),
        ("z", "go_back", _("About")),
    ]
    SUB_TITLE = _("About")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def compose(self) -> ComposeResult:

        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(id="about_container"):
            yield Label(_("[b]About & Version Info[/b]"))
            # Get system info
            textual_version = self._get_textual_version()
            terminal_info = self._get_terminal_info()
            python_version = self._get_python_version()
            os_version = self._get_os_version()
            disk_usage = self._get_disk_usage()

            about_text = _(
                """# About HeurAMS

Main library version: `{ver}-python`  
UI frontend: `Textual TUI (Basic UI)`  
UI version: `{ver}`  
API codename: `{codename}`  

> A heuristic auxiliary memorizing scheduler based on heuristic algorithms and cognitive science theories, designed to help users memorize and plan learning more efficiently.  
> An open, elegant, and extensible spaced repetition scheduler experimental platform, designed to help researchers conduct investigations, experiments, and research on cutting-edge memory algorithms more efficiently.  

You can visit the project homepage at https://ams.pluv27.top for user guides, development documentation and software updates, and participate in software development and improvement.  

Open source under the GNU Affero General Public License (version 3), with an additional exemption clause for local API calls, used for other frontend to library interface calls.  

You are using the built-in terminal user interface, which is the first full-featured frontend implementation and library test suite, located in the interface subdirectory of the library.  

Developers:  
- Wang Zhiyu ([@pluvium27](https://github.com/pluvium27)): Project initiator and lead developer  

Special thanks to the following individuals and groups; their algorithms and theories form the cornerstone of the current software algorithms:  

- [Piotr A. Woźniak](https://supermemo.guru/wiki/Piotr_Wozniak): SM-2 algorithm and SM-15 algorithm theory  
- [Jarrett Ye](https://github.com/L-M-Sherlock): FSRS algorithm and spaced repetition theory references  
- [Kazuaki Tanida](https://github.com/slaypni): CoffeeScript reverse implementation of SM-15 algorithm  
- [Open Spaced Repetition](https://github.com/open-spaced-repetition): FSRS algorithm underlying implementation  

# Runtime Environment

Python interpreter version: {python_version}  
Python interpreter path: {executable}  
Textual framework version: {textual_version}  
Terminal emulator: {terminal_info}  
Operating system version: {os_version}  
Disk free space: {disk_usage}  

When reporting issues, please copy this information into the issue description and attach `heurams.log` as an attachment to help developers locate the error."""
            ).format(
                ver=version.ver,
                codename=version.codename.capitalize(),
                python_version=python_version,
                executable=sys.executable,
                textual_version=textual_version,
                terminal_info=terminal_info,
                os_version=os_version,
                disk_usage=disk_usage,
            )
            yield Markdown(about_text, classes="about-markdown")
            yield Button(
                _("Back to Main"),
                id="back_button",
                variant="primary",
                flat=True,
                classes="back-button",
            )
        yield Footer()

    def action_go_back(self):
        self.app.pop_screen()

    def on_button_pressed(self, event) -> None:
        event.stop()
        if event.button.id == "back_button":
            self.action_go_back()

    def _get_textual_version(self) -> str:
        try:
            import textual

            return textual.__version__
        except (ImportError, AttributeError):
            return _("Unknown")

    def _get_terminal_info(self) -> str:
        terminal = shutil.which("terminal")
        if terminal:
            return terminal
        # Try from environment variables
        terminal_env = os.environ.get("TERM_PROGRAM") or os.environ.get("TERM")
        return terminal_env or _("Unknown")

    def _get_python_version(self) -> str:
        """获取 Python 解释器版本"""
        return platform.python_version()

    def _get_os_version(self) -> str:
        """获取操作系统版本"""
        try:
            if platform.system() == "Darwin":
                # macOS
                import subprocess

                result = subprocess.run(
                    ["sw_vers", "-productVersion"], capture_output=True, text=True
                )
                return f"macOS {result.stdout.strip()}"
            elif platform.system() == "Windows":
                # Windows
                return f"Windows {platform.release()}"
            elif platform.system() == "Linux":
                # Linux - 尝试获取发行版信息
                try:
                    import distro

                    return f"{distro.name()} {distro.version()}"
                except (ImportError, AttributeError):
                    return platform.platform()
            else:
                return platform.platform()
        except Exception:
            return platform.platform()

    def _get_disk_usage(self) -> str:
        """获取磁盘使用情况"""
        usage = shutil.disk_usage("/")
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        percent_free = (free_gb / total_gb) * 100
        #print(f"{free_gb:.1f} GB ({percent_free:.1f}%)")
        return f"{free_gb:.1f} GB ({percent_free:.1f}%)"
