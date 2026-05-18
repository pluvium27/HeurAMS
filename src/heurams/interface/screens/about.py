"""关于界面"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Markdown
from textual import events, on

import heurams.services.version as version
from heurams.context import *
import platform
import shutil
import os
import sys


class AboutScreen(Screen):
    BINDINGS = [
        ("q", "go_back", "返回"),
        ("z", "go_back", "关于"),
    ]
    SUB_TITLE = "关于"

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
            yield Label("[b]关于与版本信息[/b]")
            # 获取系统信息
            textual_version = self._get_textual_version()
            terminal_info = self._get_terminal_info()
            python_version = self._get_python_version()
            os_version = self._get_os_version()
            disk_usage = self._get_disk_usage()

            about_text = f"""
# 关于 HeurAMS "潜进"  

主程序库版本: `{version.ver}-python`  
用户界面分支: `Textual TUI (基本用户界面)`  
用户界面版本: `{version.ver}`  
API 版本代号: `{version.codename.capitalize()}`

> 一个基于启发式算法与认知科学理论的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划.  
> 一个开放, 优雅, 易于扩展的间隔重复调度器实验平台, 旨在帮助研究者更高效地进行前沿记忆算法的研究.  

您可在项目主页 https://ams.pluv27.top 获取用户指南, 开发文档与软件更新, 并参与到软件的开发与改进工作.  

以 GNU Affero 通用公共许可证 (第3版) 开放源代码, 并有一条豁免本机 API 调用的附加条款, 用于其他前端到程序库的接口调用.  

您正使用程序库内置的终端用户界面, 它是第一个全功能前端实现与程序库测试套件, 位于程序库的 interface 子目录.  

开发人员列表:
- Wang Zhiyu ([@pluvium27](https://github.com/pluvium27)): 项目发起与主要开发者  

感谢以下人士与团体, 他们的算法与理论构成了此软件现有算法的基石:  

- [Piotr A. Woźniak](https://supermemo.guru/wiki/Piotr_Wozniak): SM-2 算法与 SM-15 算法理论
- [Jarrett Ye](https://github.com/L-M-Sherlock): FSRS 算法与间隔重复理论文献参考
- [Kazuaki Tanida](https://github.com/slaypni): SM-15 算法的 CoffeeScript 逆向实现
- [Open Spaced Repetition](https://github.com/open-spaced-repetition): FSRS 算法底层实现

# 运行环境信息

Python 解释器版本: {python_version}  
Python 解释器路径: {sys.executable}  
Textual 框架版本: {textual_version}  
终端模拟器: {terminal_info}  
操作系统版本: {os_version}  
存储余量: {disk_usage}  

报告问题时, 请复制这些信息到问题描述, 并上传软件日志 `heurams.log` 作为附件, 以协助开发者定位错误  
"""
            yield Markdown(about_text, classes="about-markdown")
            yield Button(
                "返回主界面",
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
        """获取 Textual 框架版本"""
        try:
            import textual

            return textual.__version__
        except (ImportError, AttributeError):
            return "未知"

    def _get_terminal_info(self) -> str:
        """获取终端模拟器信息"""
        terminal = shutil.which("terminal")
        if terminal:
            return terminal
        # 尝试从环境变量获取
        terminal_env = os.environ.get("TERM_PROGRAM") or os.environ.get("TERM")
        return terminal_env or "未知"

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
