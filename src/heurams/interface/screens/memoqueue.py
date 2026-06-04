"""队列式记忆工作界面"""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

from textual import events, on

import heurams.kernel.particles as pt
from heurams.context import config_var, rootdir
from heurams.kernel.reactor import *
from heurams.services.favorite_service import favorite_manager
from heurams.services.logger import get_logger
from heurams.services.attic import Attic

from .. import shim

logger = get_logger(__name__)


class MemScreen(Screen):
    BINDINGS = [
        ("q", "go_back_notif", "返回"),
        ("p", "prev", "查看上一个"),
        ("d", "toggle_dark", ""),
        ("v", "play_voice", "朗读"),
        ("*", "toggle_favorite", "收藏"),
        ("r", "resume_mark"),
        ("Q", "go_back"),
        ("n", "block_prompt"),
        ("s", "block_prompt"),
        ("z", "block_prompt"),
    ]

    SUB_TITLE = "学习中"
    CSS_PATH = rootdir / "interface" / "css" / "screens" / "memoqueue.tcss"

    if config_var.get()["interface"]["global"]["quick_pass"]:
        BINDINGS.append(("k", "quick_pass", "正确应答"))
        BINDINGS.append(("f", "quick_fail", "错误应答"))

    rating = reactive(-1)

    def __init__(
        self,
        router: Router,
        repo=None,
        name=None,
        id=None,
        classes=None,
    ) -> None:
        super().__init__(name, id, classes)
        self.router = router
        self.repo = repo
        self.update_state()
        self.expander: Expander

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def compose(self) -> ComposeResult:
        from heurams.services.attic import Attic

        a = Attic("ana", {"openqueue": 0})
        a.data["openqueue"] += 1
        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(classes="memoqueue-container"):
            yield Label(self._get_progress_text(), id="head_stat")
            yield ScrollableContainer(id="puzzle_container")
        yield Footer()

    def update_state(self):
        """更新状态机"""
        self.procession: Procession = self.router.current_procession()  # type: ignore
        self.atom: pt.Atom = self.procession.current_atom  # type: ignore

    def on_mount(self):
        self.expander = self.procession.get_expander()
        from heurams.services.attic import Attic
        import time

        a = Attic("ana", {"last": time.time()})
        a.data["last"] = time.time()
        self.mount_puzzle()
        self.update_display()

    def puzzle_widget(self):
        try:
            puzzle = self.expander.get_current_puzzle_inf()
            return shim.puzzle2widget[puzzle["puzzle"]](  # type: ignore
                atom=self.atom, alia=puzzle["alia"]  # type: ignore
            )
        except Exception as e:
            logger.debug(f"调度展开出错: {e}")
            return Static(f"无法生成谜题 {e}")

    def _get_progress_text(self):
        s = ""
        if self.repo is not None:
            fav_status = "已收藏" if self._is_current_atom_favorited() else "未收藏"
            s += f"[{fav_status}] "
        s += f"[{self.procession.process() + 1}/{self.procession.total_length()}] \[{self.procession.route.name}]\n"
        if self.procession.cursor - 1 >= 0:
            s += f"上一个: [d]{self.procession.atoms[self.procession.cursor - 1]['ident']}[/d]"
        return s

    def update_display(self):
        """更新进度显示"""
        progress_widget = self.query_one("#head_stat")
        progress_widget.update(self._get_progress_text())  # type: ignore

    def mount_puzzle(self):
        """挂载当前谜题组件"""
        if self.procession.route == RouterState.FINISHED:
            self.mount_finished_widget()
            return
        container = self.query_one("#puzzle_container")
        for i in container.children:
            i.remove()
        container.mount(self.puzzle_widget())

    def mount_finished_widget(self):
        """挂载已完成组件"""
        a = Attic("ana", {"finished": 0})
        a.data["finished"] += 1
        container = self.query_one("#puzzle_container")
        for i in container.children:
            i.remove()
        from heurams.interface.widgets.finished import Finished

        if config_var.get()["interface"]["global"]["persist_to_file"]:
            self.repo.persist_to_repodir()
        container.mount(
            Finished(
                is_saved=config_var.get()["interface"]["global"]["persist_to_file"]
            )
        )

    def on_button_pressed(self, event):
        event.stop()

    def action_play_voice(self):
        self.run_worker(self.play_voice, exclusive=True, thread=True)

    def play_voice(self):
        """朗读当前内容"""
        from pathlib import Path

        from heurams.services.audio_service import play_by_path
        from heurams.services.hasher import get_md5

        path = Path(config_var.get()["global"]["paths"]["data"]) / "cache" / "voice"
        path = path / f"{get_md5(self.atom.registry['nucleon']["tts_text"])}.wav"
        logger.debug(str(path))
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
        if self.procession.route == RouterState.FINISHED:
            rating = -1
            return
        self.expander.report(new_rating)
        self.forward(new_rating)
        self.rating = -1

    def forward(self, rating):
        self.update_state()
        allow_forward = 1 if rating >= 4 else 0
        if allow_forward:
            self.expander.forward()
        if self.expander.state == "retronly":
            self.forward_atom(self.expander.get_quality())
        self.update_state()
        from heurams.services.attic import Attic

        a = Attic("ana", {"openpuzzles": 0})
        a = Attic("ana", {"totaltime": 0})
        a.data["openpuzzles"] += 1
        import time

        a.data["totaltime"] += time.time() - a.data["last"]
        a.data["last"] = time.time()
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
            from heurams.services.attic import Attic

            a = Attic("ana", {"puzzles_err": 0})
            a.data["puzzles_err"] += 1
            self.procession.append()
            self.update_state()  # 刷新状态
        self.procession.forward(1)
        self.update_state()  # 刷新状态
        self.expander = self.procession.get_expander()

    def action_go_back_notif(self):
        self.notify("确定吗? 按下大写 Q 以返回")

    def action_go_back(self):
        self.app.pop_screen()

    def action_quick_pass(self):
        self.rating = 5

    def action_quick_fail(self):
        self.rating = 3

    def _get_repo_rel_path(self) -> str:
        """获取仓库相对路径 (相对于 data/repo) """
        if self.repo is None:
            return ""
        # self.repo.source 是 Path 对象, 指向仓库目录
        repo_full_path = self.repo.source
        data_repo_path = Path(config_var.get()["global"]["paths"]["data"]) / "repo"
        try:
            rel_path = repo_full_path.relative_to(data_repo_path)
            return str(rel_path)
        except ValueError:
            # 如果不在 data/repo 下, 则返回完整路径 (字符串形式) 
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
        # 更新显示 (如果需要) 
        self.update_display()

    def action_block_prompt(self):
        self.app.notify("功能在记忆界面中不可用, 完成或返回后再试", severity="error")

    def action_resume_mark(self):
        from heurams.services.attic import Attic
        import time

        a = Attic("ana")
        l = a.data["last"]
        a.data["last"] = time.time()
        self.app.notify(f"时间恢复已修正: {l} -> {a.data['last']}")
