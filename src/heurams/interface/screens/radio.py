"""用于筛选当日记忆的条目 以音频形式重放"""

""" "前进电台" 界面"""
import os
from pathlib import Path
from typing import List, Optional

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

import heurams.kernel.particles as pt
from heurams.kernel.repolib import Repo
from heurams.context import config_var
from heurams.services.audio_service import play_by_path
from heurams.services.hasher import get_md5
from heurams.services.logger import get_logger
from heurams.services.tts_service import convertor

logger = get_logger(__name__)


class RadioScreen(Screen):
    SUB_TITLE = "电台"

    BINDINGS = [
        ("q", "go_back", "返回"),
        ("space", "toggle_play", "播放/暂停"),
    ]

    # 当前播放的原子索引
    current_index = reactive(0)
    # 播放状态: 'stopped', 'playing', 'paused'
    play_state = reactive("stopped")

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._organizer()

    def _organizer(self):
        repodirs = Repo.probe_valid_repos_in_dir(Path(config_var.get()['paths']['data']) / 'repo')
        repos = list(map(lambda repodir: Repo.create_from_repodir(repodir), repodirs))
        for repo in repos:
            last_modify = 0.0
            for i in repo.ident_index:
                e = pt.Electron.create_on_electonic_data(
                    electronic_data=repo.electronic_data_lict.get_itemic_unit(i)
                )
                last_modify = max(last_modify, e.las())
            

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main"):
            yield Label("[b]前进电台[/b]", classes="title")
            yield Static(f"共 {len(self.atoms)} 条当日记忆", id="status")
            with Container(id="controls"):
                yield Button("播放", id="play", variant="success")
                yield Button("暂停", id="pause", variant="primary")
                yield Button("上一首", id="prev", variant="default")
                yield Button("下一首", id="next", variant="default")
                yield Button("停止", id="stop", variant="error")
            yield ScrollableContainer(id="playlist")
        yield Footer()

    def on_mount(self) -> None:
        """挂载后更新播放列表显示"""
        self._update_playlist()

    def _filter_due_atoms(self) -> List[pt.Atom]:
        """筛选当日需要复习的原子（已激活且到期）"""
        atoms = []
        for ident in self.repo.ident_index:
            n = pt.Nucleon.create_on_nucleonic_data(
                nucleonic_data=self.repo.nucleonic_data_lict.get_itemic_unit(ident)
            )
            e = pt.Electron.create_on_electonic_data(
                electronic_data=self.repo.electronic_data_lict.get_itemic_unit(ident)
            )
            a = pt.Atom(n, e, self.repo.orbitic_data)
            # 仅选择已激活且到期的原子
            if (
                a.registry["electron"].is_activated()
                and a.registry["electron"].is_due()
            ):
                atoms.append(a)
        return atoms

    def _update_playlist(self) -> None:
        """更新播放列表显示"""
        container = self.query_one("#playlist")
        container.remove_children()
        for idx, atom in enumerate(self.atoms):
            content = atom.registry["nucleon"].get("content", "无内容")
            prefix = "▶ " if idx == self.current_index else "  "
            widget = Static(f"{prefix}{idx+1}. {content[:50]}...")
            widget.set_class(idx == self.current_index, "current")
            container.mount(widget)

    def _get_audio_path(self, atom: pt.Atom) -> Path:
        """返回音频文件路径，若不存在则生成"""
        tts_text = atom.registry["nucleon"].get("tts_text", "")
        if not tts_text:
            tts_text = atom.registry["nucleon"].get("content", "")
        voice_dir = Path(config_var.get()["paths"]["data"]) / "cache" / "voice"
        voice_dir.mkdir(parents=True, exist_ok=True)
        path = voice_dir / f"{get_md5(tts_text)}.wav"
        if not path.exists():
            convertor(tts_text, path)
        return path

    async def _play_atom(self, idx: int) -> None:
        """播放指定索引的原子（异步）"""
        if idx < 0 or idx >= len(self.atoms):
            return
        atom = self.atoms[idx]
        try:
            path = self._get_audio_path(atom)
            self._current_path = path
            # 在后台线程中播放，避免阻塞UI
            await self.run_worker(
                lambda: play_by_path(path), exclusive=True, thread=True
            )
        except Exception as e:
            logger.error("播放失败: %s", e)

    def _stop_playback(self) -> None:
        """停止当前播放"""
        if self._play_task and not self._play_task.done():
            self._play_task.cancel()
        self._play_task = None
        self._current_path = None
        self.play_state = "stopped"

    async def _play_current(self) -> None:
        """播放当前索引的原子"""
        self._stop_playback()
        self.play_state = "playing"
        self._play_task = asyncio.create_task(self._play_atom(self.current_index))
        try:
            await self._play_task
        except asyncio.CancelledError:
            pass
        finally:
            if self.play_state == "playing":
                self.play_state = "stopped"

    # 按钮事件处理
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "play":
            self.action_toggle_play()
        elif button_id == "pause":
            self.action_pause()
        elif button_id == "prev":
            self.action_prev()
        elif button_id == "next":
            self.action_next()
        elif button_id == "stop":
            self.action_stop()

    # 键盘动作
    def action_toggle_play(self) -> None:
        if self.play_state == "playing":
            self.action_pause()
        else:
            self.action_play()

    def action_play(self) -> None:
        if self.play_state != "playing":
            if self.play_state == "paused":
                # 恢复播放（目前暂停功能简单实现为停止）
                self.play_state = "playing"
            else:
                asyncio.create_task(self._play_current())

    def action_pause(self) -> None:
        if self.play_state == "playing":
            self._stop_playback()
            self.play_state = "paused"

    def action_stop(self) -> None:
        self._stop_playback()
        self.play_state = "stopped"

    def action_next(self) -> None:
        if self.current_index < len(self.atoms) - 1:
            self.current_index += 1
            self._update_playlist()
            if self.play_state == "playing":
                asyncio.create_task(self._play_current())

    def action_prev(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1
            self._update_playlist()
            if self.play_state == "playing":
                asyncio.create_task(self._play_current())

    def action_go_back(self) -> None:
        self._stop_playback()
        self.app.pop_screen()

    # 响应式更新
    def watch_current_index(self, old: int, new: int) -> None:
        self._update_playlist()

    def watch_play_state(self, old: str, new: str) -> None:
        # 更新按钮状态（可在此添加样式变化）
        pass
