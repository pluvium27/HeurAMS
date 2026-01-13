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

版本 {version.ver} {version.stage.capitalize()}
  
开发代号: {version.codename.capitalize()} {version.codename_cn} 

一个基于启发式算法的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划.  

以 AGPL-3.0 开放源代码  

您可在项目主页 https://ams.imwangzhiyu.xyz 获取用户指南, 开发文档与软件更新  

如果您觉得这个软件有用, 请给它添加一个星标 :)  

我们的共同目标是为人人带来高品质的辅助记忆 & 学习软件.

不管您来自何方, 我们都欢迎您加入社区并做出贡献.

开发人员:  

- Wang Zhiyu([@pluvium27](https://github.com/pluvium27)): 项目作者  

特别感谢:

- [Piotr A. Woźniak](https://supermemo.guru/wiki/Piotr_Wozniak): SM-2 算法与 SM-15 算法理论
- [Kazuaki Tanida](https://github.com/slaypni): SM-15 算法的 CoffeeScript 实现
- [Thoughts Memo](https://www.zhihu.com/people/L.M.Sherlock): 文献参考


# 运行环境信息

Textual 框架版本: {textual_version}  
  
终端模拟器: {terminal_info}  
  
Python 解释器版本: {python_version}  
  
操作系统版本: {os_version}  
  
存储余量: {disk_usage}  
  
内存大小: {memory_info}  

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
        except (ImportError, AttributeError):
            return "未知"
    
    def _get_terminal_info(self) -> str:
        """获取终端模拟器信息"""
        terminal = shutil.which("terminal")
        if terminal:
            return terminal
        # 尝试从环境变量获取
        terminal_env = os.environ.get('TERM_PROGRAM') or os.environ.get('TERM')
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
                result = subprocess.run(['sw_vers', '-productVersion'], 
                                      capture_output=True, text=True)
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
        try:
            usage = psutil.disk_usage('/')
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)
            percent_free = (free_gb / total_gb) * 100
            return f"{free_gb:.1f} GB ({percent_free:.1f}%)"
        except Exception:
            return "未知"
    
    def _get_memory_info(self) -> str:
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024 ** 3)
            return f"{total_gb:.1f} GB"
        except Exception:
            return "未知"