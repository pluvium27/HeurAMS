#!/usr/bin/env python3
from textual.app import ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Label,
    Button,
    Static,
    ProgressBar,
)
from textual.containers import ScrollableContainer, Horizontal
from textual.containers import ScrollableContainer
from textual.screen import Screen
import pathlib

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *
from textual.worker import get_current_worker


class PrecachingScreen(Screen):
    """预缓存音频文件屏幕

    缓存记忆单元音频文件, 全部(默认) 或部分记忆单元(可选参数传入)

    Args:
        nucleons (list): 可选列表, 仅包含 Nucleon 对象
        desc (list): 可选字符串, 包含对此次调用的文字描述
    """

    SUB_TITLE = "缓存管理器"
    BINDINGS = [("q", "go_back", "返回")]

    def __init__(self, nucleons: list = [], desc: str = ""):
        super().__init__(name=None, id=None, classes=None)
        self.nucleons = nucleons
        self.is_precaching = False
        self.current_file = ""
        self.current_item = ""
        self.progress = 0
        self.total = len(nucleons)
        self.processed = 0
        self.precache_worker = None
        self.cancel_flag = 0
        self.desc = desc
        for i in nucleons:
            i: pt.Nucleon
            i.do_eval()
        # print("完成 EVAL")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="precache_container"):
            yield Label("[b]音频预缓存[/b]", classes="title-label")

            if self.nucleons:
                yield Static(f"目标单元归属: [b]{self.desc}[/b]", classes="target-info")
                yield Static(f"单元数量: {len(self.nucleons)}", classes="target-info")
            else:
                yield Static("目标: 所有单元", classes="target-info")

            yield Static(id="status", classes="status-info")
            yield Static(id="current_item", classes="current-item")
            yield ProgressBar(total=100, show_eta=False, id="progress_bar")

            with Horizontal(classes="button-group"):
                if not self.is_precaching:
                    yield Button("开始预缓存", id="start_precache", variant="primary")
                else:
                    yield Button("取消预缓存", id="cancel_precache", variant="error")
                yield Button("清空缓存", id="clear_cache", variant="warning")
                yield Button("返回", id="go_back", variant="default")

            yield Static("若您离开此界面, 未完成的缓存进程会自动停止.")
            yield Static('缓存程序支持 "断点续传".')

        yield Footer()

    def on_mount(self):
        """挂载时初始化状态"""
        self.update_status("就绪", "等待开始...")

    def update_status(self, status, current_item="", progress=None):
        """更新状态显示"""
        status_widget = self.query_one("#status", Static)
        item_widget = self.query_one("#current_item", Static)
        progress_bar = self.query_one("#progress_bar", ProgressBar)

        status_widget.update(f"状态: {status}")
        item_widget.update(f"当前项目: {current_item}" if current_item else "")

        if progress is not None:
            progress_bar.progress = progress
            progress_bar.advance(0)  # 刷新显示

    def precache_by_text(self, text: str):
        """预缓存单段文本的音频"""
        from heurams.context import rootdir, workdir, config_var

        cache_dir = pathlib.Path(config_var.get()["paths"]["cache_dir"])
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{hasher.get_md5(text)}.wav"
        if not cache_file.exists():
            try:  # TODO: 调用模块消除tts耦合
                import edge_tts as tts

                communicate = tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
                communicate.save_sync(str(cache_file))
                return 1
            except Exception as e:
                print(f"预缓存失败 '{text}': {e}")
                return 0
        return 1

    def precache_by_nucleon(self, nucleon: pt.Nucleon):
        """依据 Nucleon 缓存"""
        # print(nucleon.metadata['formation']['tts_text'])
        ret = self.precache_by_text(nucleon.metadata["formation"]["tts_text"])
        return ret
        # print(f"TTS 缓存: {nucleon.metadata['formation']['tts_text']}")

    def precache_by_list(self, nucleons: list):
        """依据 Nucleons 列表缓存"""
        for idx, nucleon in enumerate(nucleons):
            # print(f"PROC: {nucleon}")
            worker = get_current_worker()
            if worker and worker.is_cancelled:  # 函数在worker中执行且已被取消
                return False
            text = nucleon.metadata["formation"]["tts_text"]
            # self.current_item = text[:30] + "..." if len(text) > 50 else text
            # print(text)
            self.processed += 1
            # print(self.processed)
            # print(self.total)
            progress = int((self.processed / self.total) * 100) if self.total > 0 else 0
            # print(progress)
            self.update_status(f"正处理 ({idx + 1}/{len(nucleons)})", text, progress)
            ret = self.precache_by_nucleon(nucleon)
            if not ret:
                self.update_status(
                    "出错",
                    f"处理失败, 跳过: {self.current_item}",
                )
                import time

                time.sleep(1)
            if self.cancel_flag:
                worker.cancel()
                self.cancel_flag = 0
                return False
        return True

    def precache_by_nucleons(self):
        # print("开始缓存")
        ret = self.precache_by_list(self.nucleons)
        # print(f"返回 {ret}")
        return ret

    def precache_by_filepath(self, path: pathlib.Path):
        """预缓存单个文件的所有内容"""
        lst = list()
        for i in pt.load_nucleon(path):
            lst.append(i[0])
        return self.precache_by_list(lst)

    def precache_all_files(self):
        """预缓存所有文件"""
        from heurams.context import rootdir, workdir, config_var

        nucleon_path = pathlib.Path(config_var.get()["paths"]["nucleon_dir"])
        nucleon_files = [
            f for f in nucleon_path.iterdir() if f.suffix == ".toml"
        ]  # TODO: 解耦合

        # 计算总项目数
        self.total = 0
        nu = list()
        for file in nucleon_files:
            try:
                for i in pt.load_nucleon(file):
                    nu.append(i[0])
            except:
                continue
        self.total = len(nu)
        for i in nu:
            i: pt.Nucleon
            i.do_eval()
        return self.precache_by_list(nu)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "start_precache" and not self.is_precaching:
            # 开始预缓存
            if self.nucleons:
                self.precache_worker = self.run_worker(
                    self.precache_by_nucleons,
                    thread=True,
                    exclusive=True,
                    exit_on_error=True,
                )
            else:
                self.precache_worker = self.run_worker(
                    self.precache_all_files,
                    thread=True,
                    exclusive=True,
                    exit_on_error=True,
                )

        elif event.button.id == "cancel_precache" and self.is_precaching:
            # 取消预缓存
            if self.precache_worker:
                self.precache_worker.cancel()
            self.is_precaching = False
            self.processed = 0
            self.progress = 0
            self.update_status("已取消", "预缓存操作被用户取消", 0)

        elif event.button.id == "clear_cache":
            # 清空缓存
            try:
                import shutil
                from heurams.context import rootdir, workdir, config_var

                shutil.rmtree(
                    f"{config_var.get()["paths"]["cache_dir"]}", ignore_errors=True
                )
                self.update_status("已清空", "音频缓存已清空", 0)
            except Exception as e:
                self.update_status("错误", f"清空缓存失败: {e}")
            self.cancel_flag = 1
            self.processed = 0
            self.progress = 0

        elif event.button.id == "go_back":
            self.action_go_back()

    def action_go_back(self):
        if self.is_precaching and self.precache_worker:
            self.precache_worker.cancel()
        self.app.pop_screen()

    def action_quit_app(self):
        if self.is_precaching and self.precache_worker:
            self.precache_worker.cancel()
        self.app.exit()
