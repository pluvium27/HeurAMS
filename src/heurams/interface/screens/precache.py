"""缓存工具界面"""

import pathlib

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ProgressBar, Static
from textual.worker import get_current_worker

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *

# 兼容性缓存路径：优先使用 paths.cache，否则使用 data/cache
paths = config_var.get()["paths"]
cache_dir = pathlib.Path(paths.get("cache", paths["data"] + "/cache")) / "voice"


def format_size(bytes_num: int) -> str:
    """将字节数格式化为人类可读的字符串"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0 # type: ignore
    return f"{bytes_num:.2f} PB"


class PrecachingScreen(Screen):
    """预缓存音频文件屏幕

    缓存记忆单元音频文件, 全部(默认) 或部分记忆单元(可选参数传入)

    Args:
        nucleons (list): 可选列表, 仅包含 Nucleon 对象
        desc (list): 可选字符串, 包含对此次调用的文字描述
    """

    SUB_TITLE = "缓存管理器"
    BINDINGS = [
        ("q", "go_back", "返回"),
    ]

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
        # 不再需要缓存配置，保留配置读取以兼容
        self.cache_stats = {"total_size": 0, "file_count": 0, "human_size": "0 B", "cached_units": 0, "total_units": 0, "cache_rate": 0}
        self._update_cache_stats()

    def _get_total_units(self) -> int:
        """获取所有仓库的总单元数"""
        from heurams.context import config_var
        from heurams.kernel.repolib import Repo
        repo_path = pathlib.Path(config_var.get()["paths"]["data"]) / "repo"
        repo_dirs = Repo.probe_valid_repos_in_dir(repo_path)
        repos = map(Repo.create_from_repodir, repo_dirs)
        total = 0
        for repo in repos:
            try:
                total += len(repo.ident_index)
            except:
                continue
        return total

    def _update_cache_stats(self) -> None:
        """更新缓存统计信息"""
        total_size = 0
        file_count = 0
        cached_units = 0
        if cache_dir.exists():
            for file in cache_dir.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
                    file_count += 1
                    if file.suffix.lower() == ".wav":
                        cached_units += 1
        total_units = self._get_total_units()
        cache_rate = (cached_units / total_units * 100) if total_units > 0 else 0
        
        self.cache_stats["total_size"] = total_size
        self.cache_stats["file_count"] = file_count
        self.cache_stats["human_size"] = format_size(total_size)
        self.cache_stats["cached_units"] = cached_units
        self.cache_stats["total_units"] = total_units
        self.cache_stats["cache_rate"] = cache_rate

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="precache_container"):
            yield Label("[b]音频预缓存[/b]", classes="title-label")
            with Container():
                yield Static(
                    f"缓存率: {self.cache_stats.get('cache_rate', 0):.1f}% (已缓存 {self.cache_stats.get('cached_units', 0)} / {self.cache_stats.get('total_units', 0)} 个单元)",
                    classes="cache-usage-text"
                )
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
            with Container(classes="cache-info"):
                yield Static(f"缓存路径: {cache_dir}", classes="cache-path")
                yield Static(f"文件数: {self.cache_stats['file_count']}", classes="cache-count")
                yield Static(f"总大小: {self.cache_stats['human_size']}", classes="cache-size")
                yield Button("刷新", id="refresh_cache_stats", variant="default", flat=True)
                yield Static("若您离开此界面, 未完成的缓存进程会自动停止.")
                yield Static('缓存程序支持 "断点续传".')

        yield Footer()

    def on_mount(self):
        """挂载时初始化状态"""
        self.update_status("就绪", "等待开始...")
        self._update_cache_display()

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

    def _update_cache_display(self) -> None:
        """更新缓存信息显示"""
        # 更新统计信息
        self._update_cache_stats()
        # 更新缓存率进度条
        # 更新缓存大小和文件数显示
        cache_count_widget = self.query_one(".cache-count", Static)
        cache_size_widget = self.query_one(".cache-size", Static)
        cache_usage_text = self.query_one(".cache-usage-text", Static)
        if cache_count_widget:
            cache_count_widget.update(f"文件数: {self.cache_stats['file_count']}")
        if cache_size_widget:
            cache_size_widget.update(f"总大小: {self.cache_stats['human_size']}")
        if cache_usage_text:
            cache_usage_text.update(
                f"缓存率: {self.cache_stats.get('cache_rate', 0):.1f}% "
                f"(已缓存 {self.cache_stats.get('cached_units', 0)} / {self.cache_stats.get('total_units', 0)} 个单元)"
            )

    def precache_by_text(self, text: str):
        """预缓存单段文本的音频"""
        from heurams.context import config_var, rootdir, workdir

        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{hasher.get_md5(text)}.wav"
        if not cache_file.exists():
            try:
                from heurams.services.tts_service import convertor

                convertor(text, cache_file)
                return 1
            except Exception as e:
                print(f"预缓存失败 '{text}': {e}")
                return 0
        return 1

    def precache_by_nucleon(self, nucleon: pt.Nucleon):
        """依据 Nucleon 缓存"""
        ret = self.precache_by_text(nucleon["tts_text"])
        return ret

    def precache_by_list(self, nucleons: list):
        """依据 Nucleons 列表缓存"""
        for idx, nucleon in enumerate(nucleons):
            # print(f"PROC: {nucleon}")
            worker = get_current_worker()
            if worker and worker.is_cancelled:  # 函数在worker中执行且已被取消
                return False
            text = nucleon["tts_text"]
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

    def precache_all_files(self):
        """预缓存所有文件"""
        from heurams.context import config_var, rootdir, workdir
        from heurams.kernel.repolib import Repo

        repo_path = pathlib.Path(config_var.get()["paths"]["data"]) / "repo"
        repo_dirs = Repo.probe_valid_repos_in_dir(repo_path)
        repos = map(Repo.create_from_repodir, repo_dirs)

        # 计算总项目数
        self.total = 0
        nucleon_list = list()
        for repo in repos:
            try:
                for i in repo.ident_index:
                    nucleon_list.append(
                        pt.Nucleon.create_on_nucleonic_data(
                            repo.nucleonic_data_lict.get_itemic_unit(i)
                        )
                    )
            except:
                continue
        self.total = len(nucleon_list)
        return self.precache_by_list(nucleon_list)

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

                from heurams.context import config_var, rootdir, workdir

                shutil.rmtree(cache_dir, ignore_errors=True)
                self.update_status("已清空", "音频缓存已清空", 0)
                self._update_cache_display()  # 更新缓存统计显示
            except Exception as e:
                self.update_status("错误", f"清空缓存失败: {e}")
            self.cancel_flag = 1
            self.processed = 0
            self.progress = 0

        elif event.button.id == "refresh_cache_stats":
            # 刷新缓存统计信息
            self._update_cache_display()
            self.app.notify("缓存信息已刷新", severity="information")
        elif event.button.id == "go_back":
            self.action_go_back()

    def action_go_back(self):
        if self.is_precaching and self.precache_worker:
            self.precache_worker.cancel()
        self.app.pop_screen()
