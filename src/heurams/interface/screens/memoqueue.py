"""队列式记忆工作界面"""

from enum import Enum, auto
from pathlib import Path
from typing import Callable

from textual.app import ComposeResult
from textual.containers import Center, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

import heurams.kernel.particles as pt
import heurams.kernel.puzzles as pz
from heurams.context import config_var
from heurams.kernel.reactor import *
from heurams.services.favorite_service import favorite_manager
from heurams.services.logger import get_logger

from .. import shim


class AtomState(Enum):
    FAILED = auto()
    NORMAL = auto()


logger = get_logger(__name__)


class MemScreen(Screen):
    BINDINGS = [
        ("q", "go_back", "返回"),
        ("p", "prev", "查看上一个"),
        ("d", "toggle_dark", ""),
        ("v", "play_voice", "朗读"),
        ("*", "toggle_favorite", "收藏"),
        ("0,1,2,3", "app.push_screen('about')", ""),
    ]

    if config_var.get()["quick_pass"]:
        BINDINGS.append(("k", "quick_pass", "正确应答"))
        BINDINGS.append(("f", "quick_fail", "错误应答"))
    rating = reactive(-1)

    def __init__(
        self,
        phaser: Phaser,
        save_func: Callable,
        repo=None,
        name=None,
        id=None,
        classes=None,
    ) -> None:
        super().__init__(name, id, classes)
        self.phaser = phaser
        self.save_func = save_func
        self.repo = repo
        self.update_state()
        self.fission: Fission

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer():
            yield Label(self._get_progress_text(), id="progress")
            yield ScrollableContainer(id="puzzle-container")
        yield Footer()

    def update_state(self):
        """更新状态机"""
        self.procession: Procession = self.phaser.current_procession()  # type: ignore
        self.atom: pt.Atom = self.procession.current_atom  # type: ignore
        

    def on_mount(self):
        self.fission = self.procession.get_fission()
        self.mount_puzzle()
        self.update_display()

    def puzzle_widget(self):
        try:
            puzzle = self.fission.get_current_puzzle_inf()
            return shim.puzzle2widget[puzzle["puzzle"]](  # type: ignore
                atom=self.atom, alia=puzzle["alia"]  # type: ignore
            )
        except Exception as e:
            logger.debug(f"调度展开出错: {e}")
            return Static(f"无法生成谜题 {e}")

    def _get_progress_text(self):
        s = f"阶段: {self.procession.phase.name}\n"
        # 收藏状态
        if self.repo is not None:
            fav_status = "已收藏" if self._is_current_atom_favorited() else "未收藏"
            s += f"收藏: {fav_status}\n"
        if config_var.get().get("debug_topline", 0):
            try:
                alia = self.fission.get_current_puzzle_inf()["alia"]  # type: ignore
                s += f"谜题: {alia}\n"
            except:
                pass
            try:
                stat = self.phaser.__repr__("simple", "")
                s += f"{stat}\n"
            except:
                pass
            try:
                stat = self.procession.__repr__("simple", "")
                s += f"{stat}\n"
            except:
                pass
            try:
                stat = self.fission.__repr__("simple", "")
                s += f"{stat}\n"
            except Exception as e:
                s = str(e)
        s += f"进度: {self.procession.process() + 1}/{self.procession.total_length()}"
        return s

    def update_display(self):
        """更新进度显示"""
        progress_widget = self.query_one("#progress")
        progress_widget.update(self._get_progress_text())  # type: ignore

    def mount_puzzle(self):
        """挂载当前谜题组件"""
        if self.procession.phase == PhaserState.FINISHED:
            self.mount_finished_widget()
            return
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        container.mount(self.puzzle_widget())

    def mount_finished_widget(self):
        """挂载已完成组件"""
        container = self.query_one("#puzzle-container")
        for i in container.children:
            i.remove()
        from heurams.interface.widgets.finished import Finished

        if config_var.get().get("persist_to_file", 0):
            self.save_func()
        container.mount(Finished(is_saved=config_var.get().get("persist_to_file", 0)))

    def on_button_pressed(self, event):
        event.stop()

    def action_play_voice(self):
        self.run_worker(self.play_voice, exclusive=True, thread=True)

    def play_voice(self):
        """朗读当前内容"""
        from pathlib import Path

        from heurams.services.audio_service import play_by_path
        from heurams.services.hasher import get_md5

        path = Path(config_var.get()["paths"]["data"]) / "cache" / "voice"
        path = path / f"{get_md5(self.atom.registry['nucleon']["tts_text"])}.wav"
        if path.exists():
            play_by_path(path)
        else:
            from heurams.services.tts_service import convertor

            convertor(self.atom.registry["nucleon"]["tts_text"], path)
            play_by_path(path)

    def watch_rating(self, old_rating, new_rating) -> None:
        if new_rating == -1:  # 安全值
            return
        self.update_state()
        if self.procession.phase == PhaserState.FINISHED:
            rating = -1
            return
        self.fission.report(new_rating)
        self.forward(new_rating)
        self.rating = -1


    def forward(self, rating):
        self.update_state()
        allow_forward = 1 if rating >= 4 else 0
        if allow_forward:
            self.fission.forward()
        if self.fission.state == "retronly":
            self.forward_atom(self.fission.get_quality())
        self.update_state()
        self.mount_puzzle()
        self.update_display()

    def atom_reporter(self, quality):
        if not self.atom.registry["runtime"]["locked"]:
            if not self.atom.registry["electron"].is_activated():
                self.atom.registry["electron"].activate()
                logger.debug(f"激活原子 {self.atom}")
                self.atom.lock(1)
                self.atom.minimize(5)
            else:
                self.atom.minimize(quality)
        else:
            pass

    def forward_atom(self, quality):
        logger.debug(f"Quality: {quality}")
        self.atom_reporter(quality)
        if quality <= 3:
            self.procession.append()
            self.update_state()  # 刷新状态
        self.procession.forward(1)
        self.update_state()  # 刷新状态
        self.fission = self.procession.get_fission()

    def action_go_back(self):
        self.app.pop_screen()

    def action_quick_pass(self):
        self.rating = 5

    def action_quick_fail(self):
        self.rating = 3

    def _get_repo_rel_path(self) -> str:
        """获取仓库相对路径（相对于 data/repo）"""
        if self.repo is None:
            return ""
        # self.repo.source 是 Path 对象，指向仓库目录
        repo_full_path = self.repo.source
        data_repo_path = Path(config_var.get()["paths"]["data"]) / "repo"
        try:
            rel_path = repo_full_path.relative_to(data_repo_path)
            return str(rel_path)
        except ValueError:
            # 如果不在 data/repo 下，则返回完整路径（字符串形式）
            return str(repo_full_path)

    def _is_current_atom_favorited(self) -> bool:
        """检查当前原子是否已收藏"""
        if self.repo is None:
            return False
        repo_path = self._get_repo_rel_path()
        return favorite_manager.has(repo_path, self.atom.ident)

    def action_toggle_favorite(self):
        """切换收藏状态"""
        if self.repo is None:
            self.app.notify("无法收藏：未关联仓库", severity="error")
            return
        repo_path = self._get_repo_rel_path()
        ident = self.atom.ident
        if favorite_manager.has(repo_path, ident):
            favorite_manager.remove(repo_path, ident)
            self.app.notify(f"已取消收藏：{ident}", severity="information")
        else:
            favorite_manager.add(repo_path, ident)
            self.app.notify(f"已收藏：{ident}", severity="information")
        # 更新显示（如果需要）
        self.update_display()
