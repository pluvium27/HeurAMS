"""Cache tool screen"""

import pathlib

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, ProgressBar, Static
from textual.worker import get_current_worker

from textual import events, on

import heurams.kernel.particles as pt
import heurams.services.hasher as hasher
from heurams.context import *
from heurams.i18n import _

# Compatibility cache path: prefer paths.cache, otherwise data/cache
paths = config_var.get()["global"]["paths"]
cache_dir = pathlib.Path(paths.get("cache", paths["data"] + "/cache")) / "voice"


def human_size(bytes_num: int) -> str:
    """Format byte count as human-readable string"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0  # type: ignore
    return f"{bytes_num:.2f} PB"


class PrecachingScreen(Screen):
    """Audio file pre-caching screen

    Cache memory unit audio files, all (default) or some memory units (optional params)

    Args:
        nucleons (list): Optional list containing Nucleon objects only
        desc (list): Optional string containing description of this call
    """

    SUB_TITLE = _("Cache Manager")
    BINDINGS = [
        ("q", "go_back", _("Back")),
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
        # 不再需要缓存配置, 保留配置读取以兼容
        self.cache_stats = {
            "total_size": 0,
            "file_count": 0,
            "human_size": "0 B",
            "cached_units": 0,
            "total_units": 0,
            "cache_rate": 0,
        }
        self._update_cache_stats()

    def _get_total_units(self) -> int:
        """Get total units across all repos"""
        from heurams.context import config_var
        from heurams.kernel.repolib import Repo

        repo_path = pathlib.Path(config_var.get()["global"]["paths"]["data"]) / "repo"
        repo_dirs = Repo.probe_valid_repos_in_dir(repo_path)
        repos = map(Repo.from_repodir, repo_dirs)
        total = 0
        for repo in repos:
            try:
                total += len(repo.ident_index)
            except:
                continue
        return total

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def _update_cache_stats(self) -> None:
        """Update cache statistics"""
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
        self.cache_stats["human_size"] = human_size(total_size)
        self.cache_stats["cached_units"] = cached_units
        self.cache_stats["total_units"] = total_units
        self.cache_stats["cache_rate"] = cache_rate

    def compose(self) -> ComposeResult:

        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(id="precache_container"):
            yield Label(_("[b]Audio Pre-cache[/b]"), classes="title-label")
            with Container():
                yield Static(
                    _("Cache rate: {rate:.1f}% ({cached} / {total} units)").format(
                        rate=self.cache_stats.get('cache_rate', 0),
                        cached=self.cache_stats.get('cached_units', 0),
                        total=self.cache_stats.get('total_units', 0),
                    ),
                    classes="cache-usage-text",
                )
                if self.nucleons:
                    yield Static(
                        _("Target units from: [b]{desc}[/b]").format(desc=self.desc), classes="target-info"
                    )
                    yield Static(
                        _("Unit count: {n}").format(n=len(self.nucleons)), classes="target-info"
                    )
                else:
                    yield Static(_("Target: all units"), classes="target-info")

                yield Static(id="status", classes="status-info")
                yield Static(id="current_item", classes="current-item")
                yield ProgressBar(total=100, show_eta=False, id="progress_bar")
                with Horizontal(classes="button-group"):
                    if not self.is_precaching:
                        yield Button(
                            _("Start Pre-cache"), id="start_precache", variant="primary"
                        )
                    else:
                        yield Button(
                            _("Cancel Pre-cache"), id="cancel_precache", variant="error"
                        )
                    yield Button(_("Clear Cache"), id="clear_cache", variant="warning")
                    yield Button(_("Back"), id="go_back", variant="default")
            with Container(classes="cache-info"):
                yield Static(_("Cache path: {path}").format(path=cache_dir), classes="cache-path")
                yield Static(
                    _("Files: {n}").format(n=self.cache_stats['file_count']), classes="cache-count"
                )
                yield Static(
                    _("Total size: {size}").format(size=self.cache_stats['human_size']), classes="cache-size"
                )
                yield Button(
                    _("Refresh"), id="refresh_cache_stats", variant="default", flat=True
                )
                yield Static(_("If you leave this screen, ongoing cache processes will stop automatically."))
                yield Static(_('Cache supports "resume from break".'))

        yield Footer()

    def on_mount(self):
        """Initialise state on mount"""
        self.update_status(_("Ready"), _("Waiting to start..."))
        self._update_cache_display()

    def update_status(self, status, current_item="", progress=None):
        """Update status display"""
        status_widget = self.query_one("#status", Static)
        item_widget = self.query_one("#current_item", Static)
        progress_bar = self.query_one("#progress_bar", ProgressBar)

        status_widget.update(_("Status: {s}").format(s=status))
        item_widget.update(_("Current item: {item}").format(item=current_item) if current_item else "")

        if progress is not None:
            progress_bar.progress = progress
            progress_bar.advance(0)  # Refresh display

    def _update_cache_display(self) -> None:
        """Update cache info display"""
        # Update stats
        self._update_cache_stats()
        # Update cache rate progress bar
        # Update cache size and file count display
        cache_count_widget = self.query_one(".cache-count", Static)
        cache_size_widget = self.query_one(".cache-size", Static)
        cache_usage_text = self.query_one(".cache-usage-text", Static)
        if cache_count_widget:
            cache_count_widget.update(_("Files: {n}").format(n=self.cache_stats['file_count']))
        if cache_size_widget:
            cache_size_widget.update(_("Total size: {size}").format(size=self.cache_stats['human_size']))
        if cache_usage_text:
            cache_usage_text.update(
                _("Cache rate: {rate:.1f}% ({cached} / {total} units)").format(
                    rate=self.cache_stats.get('cache_rate', 0),
                    cached=self.cache_stats.get('cached_units', 0),
                    total=self.cache_stats.get('total_units', 0),
                )
            )

    def precache_by_text(self, text: str):
        """Pre-cache audio for a single text string"""

        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{hasher.get_md5(text)}.wav"
        if not cache_file.exists():
            try:
                from heurams.services.tts_service import convertor

                convertor(text, cache_file)
                return 1
            except Exception as e:
                print(f"Pre-cache failed '{text}': {e}")
                return 0
        return 1

    def precache_by_nucleon(self, nucleon: pt.Nucleon):
        """Cache based on Nucleon"""
        ret = self.precache_by_text(nucleon["tts_text"])
        return ret

    def precache_by_list(self, nucleons: list):
        """Cache based on Nucleons list"""
        for idx, nucleon in enumerate(nucleons):
            # print(f"PROC: {nucleon}")
            worker = get_current_worker()
            if worker and worker.is_cancelled:  # Function running in worker and has been cancelled
                return False
            text = nucleon["tts_text"]
            # self.current_item = text[:30] + "..." if len(text) > 50 else text
            # print(text)
            self.processed += 1
            # print(self.processed)
            # print(self.total)
            progress = int((self.processed / self.total) * 100) if self.total > 0 else 0
            # print(progress)
            self.update_status(_("Processing ({i}/{total})").format(i=idx + 1, total=len(nucleons)), text, progress)
            ret = self.precache_by_nucleon(nucleon)
            if not ret:
                self.update_status(
                    _("Error"),
                    _("Failed, skipping: {item}").format(item=self.current_item),
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
        from heurams.context import config_var
        from heurams.kernel.repolib import Repo

        repo_path = pathlib.Path(config_var.get()["global"]["paths"]["data"]) / "repo"
        repo_dirs = Repo.probe_valid_repos_in_dir(repo_path)
        repos = map(Repo.from_repodir, repo_dirs)

        # 计算总项目数
        self.total = 0
        nucleon_list = list()
        for repo in repos:
            try:
                for i in repo.ident_index:
                    nucleon_list.append(
                        pt.Nucleon.from_data(
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
            # Start pre-cache
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
            # Cancel pre-cache
            if self.precache_worker:
                self.precache_worker.cancel()
            self.is_precaching = False
            self.processed = 0
            self.progress = 0
            self.update_status(_("Cancelled"), _("Pre-cache cancelled by user"), 0)

        elif event.button.id == "clear_cache":
            # Clear cache
            try:
                import shutil

                shutil.rmtree(cache_dir, ignore_errors=True)
                self.update_status(_("Cleared"), _("Audio cache cleared"), 0)
                self._update_cache_display()  # Update cache stats display
            except Exception as e:
                self.update_status(_("Error"), _("Failed to clear cache: {error}").format(error=e))
            self.cancel_flag = 1
            self.processed = 0
            self.progress = 0

        elif event.button.id == "refresh_cache_stats":
            # Refresh cache stats
            self._update_cache_display()
            self.app.notify(_("Cache info refreshed"), severity="information")
        elif event.button.id == "go_back":
            self.action_go_back()

    def action_go_back(self):
        if self.is_precaching and self.precache_worker:
            self.precache_worker.cancel()
        self.app.pop_screen()
