"""关于界面"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Markdown, Static

import heurams.services.version as version
from heurams.context import *
import platform
import shutil
import psutil
import os
import sys


class AboutScreen(Screen):
    BINDINGS = [
        ("q", "go_back", "返回"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="about_container"):
            yield Label("[b]关于与版本信息[/b]")

            # 获取系统信息
            textual_version = self._get_textual_version()
            terminal_info = self._get_terminal_info()
            python_version = self._get_python_version()
            os_version = self._get_os_version()
            disk_usage = self._get_disk_usage()
            memory_info = self._get_memory_info()

            about_text = f"""
# 关于 "潜进"  

主程序库版本: `{version.ver}-python`  
用户界面分支: `Textual TUI (基本用户界面)`  
用户界面版本: `{version.ver}`  
API 版本代号: `{version.codename.capitalize()}`

一个基于启发式算法与认知科学理论的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划.  

以 AGPL-3.0 开放源代码, 这直接意味着任何个体直接基于此代码对外或内部提供的应用和服务, 无论本地或网络, 必须向所有用户公开完整修改后的源代码, 且继续沿用 AGPL-3.0 协议.  

您正使用的 TUI 用户界面是 python 版本程序库自带的基本用户界面, 作为基本的全功能前端实现与程序库测试, 如果您想去除它, 请移除程序库根目录中的 interface 文件夹.  

您可在项目主页 https://ams.pluv27.top 获取用户指南, 开发文档与软件更新.  

如果您觉得这个软件有用, 可以在它的源代码仓库给它添加一个星标 :)  

> 潜进(HeurAMS), 以及它作为一个"程序库"是自由且免费的, 但是开发工作必须投入大量精力.  
> 您可以加入各种语言的翻译团队来翻译软件的界面, 您还可以制作图像、主题、音效, 或者改进软件配套的文档……  
> 不管您来自何方, 我们都欢迎您加入社区并做出贡献.  
> 我们的共同目标是为人人带来高品质的辅助记忆 & 学习软件.  
> 您的慷慨支持, 我们必当涌泉相报.  

开发人员列表:  

- Wang Zhiyu([@pluvium27](https://github.com/pluvium27)): 发起项目与主要维护者  

特别感谢以下人士, 他们的算法与理论构成了此软件算法的基石:  

- [Piotr A. Woźniak](https://supermemo.guru/wiki/Piotr_Wozniak): SM-2 算法与 SM-15 算法理论
- [Kazuaki Tanida](https://github.com/slaypni): SM-15 算法的 CoffeeScript 实现
- [Thoughts Memo](https://www.zhihu.com/people/L.M.Sherlock): 文献参考


# 运行环境信息

Python 解释器版本: {python_version}  
Python 解释器路径: {sys.executable}  
Textual 框架版本: {textual_version}  
终端模拟器: {terminal_info}  
操作系统版本: {os_version}  
存储余量: {disk_usage}  
内存大小: {memory_info}  
  
报告问题时, 请复制这些信息到问题描述, 并上传软件日志 `heurams.log` 作为附件, 以协助开发者定位错误  
"""
            yield Markdown(about_text, classes="about-markdown")

            yield Button(
                "返回主界面",
                id="back_button",
                variant="primary",
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
        except ImportError, AttributeError:
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
                except ImportError, AttributeError:
                    return platform.platform()
            else:
                return platform.platform()
        except Exception:
            return platform.platform()

    def _get_disk_usage(self) -> str:
        """获取磁盘使用情况"""
        try:
            usage = psutil.disk_usage("/")
            free_gb = usage.free / (1024**3)
            total_gb = usage.total / (1024**3)
            percent_free = (free_gb / total_gb) * 100
            return f"{free_gb:.1f} GB ({percent_free:.1f}%)"
        except Exception:
            return "未知"

    def _get_memory_info(self) -> str:
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            return f"{total_gb:.1f} GB"
        except Exception:
            return "未知"
