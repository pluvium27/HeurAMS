"""Sync tool screen"""

import pathlib
import time

from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, Static
from textual.worker import get_current_worker

from textual import events, on

from heurams.context import *
from heurams.i18n import _


class SyncScreen(Screen):

    BINDINGS = [("q", "go_back", _("Back"))]

    def __init__(self, nucleons: list = [], desc: str = ""):
        super().__init__(name=None, id=None, classes=None)
        self.sync_service = None
        self.is_syncing = False
        self.is_paused = False
        self.log_messages = []
        self.max_log_lines = 50

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def compose(self) -> ComposeResult:

        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(id="sync_container"):
            # Title and connection status
            yield Static(_("Sync Tool"), classes="title")
            yield Static("", id="status_label", classes="status")

            # Config info
            yield Static(_("Sync protocol: {proto}").format(proto=config_var.get()['services']['sync']))
            yield Static(_("Server Configuration:"), classes="section_title")
            with Horizontal(classes="config_info"):
                yield Static(_("Remote server:"), classes="config_label")
                yield Static("", id="server_url", classes="config_value")
            with Horizontal(classes="config_info"):
                yield Static(_("Remote path:"), classes="config_label")
                yield Static("", id="remote_path", classes="config_value")

            with Horizontal(classes="control_buttons"):
                yield Button(_("Test Connection"), id="test_connection", variant="primary")
                yield Button(_("Start Sync"), id="start_sync", variant="success")
                yield Button(_("Pause"), id="pause_sync", variant="warning", disabled=True)
                yield Button(_("Cancel"), id="cancel_sync", variant="error", disabled=True)

            yield Static(_("Sync Progress"), classes="section_title")
            yield ProgressBar(id="progress_bar", show_percentage=True, total=100)
            yield Static("", id="progress_label", classes="progress_text")

            yield Static(_("Sync Log"), classes="section_title")
            yield Static("", id="log_output", classes="log_output")

        yield Footer()

    def on_mount(self):
        """Initialise state on mount"""
        self.update_ui_from_config()
        self.log_message(_("Sync tool started"))

    def update_ui_from_config(self):
        """Update UI with config info"""
        try:
            sync_cfg: dict = config_var.get()["providers"]["sync"]["webdav"]
            # Update server URL
            url = sync_cfg.get("url", _("Not configured"))
            url_widget = self.query_one("#server_url")
            url_widget.update(url)  # type: ignore
            # Update remote path
            remote_path = sync_cfg.get("remote_path", "/")
            path_widget = self.query_one("#remote_path")
            path_widget.update(remote_path)  # type: ignore

            # Update status label
            status_widget = self.query_one("#status_label")
            if self.sync_service and self.sync_service.client:
                status_widget.update(_("✅ Sync service ready"))  # type: ignore
                status_widget.add_class("ready")
            else:
                status_widget.update(_("❌ Sync service not configured or not enabled"))  # type: ignore
                status_widget.add_class("error")

        except Exception as e:
            self.log_message(_("Failed to update UI: {error}").format(error=e), is_error=True)

    def update_status(self, status, current_item="", progress=None):
        """Update status display"""
        try:
            status_widget = self.query_one("#status_label")
            status_widget.update(status)  # type: ignore

            if progress is not None:
                progress_bar = self.query_one("#progress_bar")
                progress_bar.progress = progress  # type: ignore

                progress_label = self.query_one("#progress_label")
                progress_label.update(f"{progress}% - {current_item}" if current_item else f"{progress}%")  # type: ignore

        except Exception as e:
            self.log_message(_("Failed to update status: {error}").format(error=e), is_error=True)

    def log_message(self, message: str, is_error: bool = False):
        """Add log message and update display"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = "[ERROR]" if is_error else "[INFO]"
        log_line = f"{timestamp} {prefix} {message}"

        self.log_messages.append(log_line)
        # Keep log lines under max
        if len(self.log_messages) > self.max_log_lines:
            self.log_messages = self.log_messages[-self.max_log_lines :]

        # Update log display
        try:
            log_widget = self.query_one("#log_output")
            log_widget.update("\n".join(self.log_messages))  # type: ignore
        except Exception:
            pass  # Ignore if widget not ready

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        button_id = event.button.id

        if button_id == "test_connection":
            self.test_connection()
        elif button_id == "start_sync":
            self.start_sync()
        elif button_id == "pause_sync":
            self.pause_sync()
        elif button_id == "cancel_sync":
            self.cancel_sync()

        event.stop()

    def test_connection(self):
        """Test WebDAV server connection"""
        if not self.sync_service:
            self.log_message(_("Sync service not initialised, please check configuration"), is_error=True)
            self.update_status(_("❌ Sync service not initialised"))
            return

        self.log_message(_("Testing WebDAV connection..."))
        self.update_status(_("Testing connection..."))

        try:
            success = self.sync_service.test_connection()
            if success:
                self.log_message(_("Connection test successful"))
                self.update_status(_("✅ Connection OK"))
            else:
                self.log_message(_("Connection test failed"), is_error=True)
                self.update_status(_("❌ Connection failed"))
        except Exception as e:
            self.log_message(_("Connection test error: {error}").format(error=e), is_error=True)
            self.update_status(_("❌ Connection error"))

    def start_sync(self):
        """Start syncing"""
        if not self.sync_service:
            self.log_message(_("Sync service not initialised, cannot start sync"), is_error=True)
            return

        if self.is_syncing:
            self.log_message(_("Sync already in progress"), is_error=True)
            return

        self.is_syncing = True
        self.is_paused = False
        self.update_button_states()

        self.log_message(_("Starting data sync..."))
        self.update_status(_("Syncing..."), progress=0)

        # Start background sync task
        self.run_worker(self.perform_sync, thread=True)

    def perform_sync(self):
        """Execute sync task (runs in background thread)"""
        worker = get_current_worker()

        try:
            # Get local directories to sync
            from heurams.context import config_var

            config = config_var.get()
            paths = config.get("paths", {})

            # Sync nucleon directory
            nucleon_dir = pathlib.Path(paths.get("nucleon_dir", "./data/nucleon"))
            if nucleon_dir.exists():
                self.log_message(_("Syncing nucleon directory: {dir}").format(dir=nucleon_dir))
                self.update_status(_("Syncing nucleon directory..."), progress=10)

                result = self.sync_service.sync_directory(nucleon_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        _("nucleon sync complete: uploaded {up}, downloaded {down}").format(
                            up=result.get('uploaded', 0),
                            down=result.get('downloaded', 0),
                        )
                    )
                else:
                    self.log_message(
                        _("nucleon sync failed: {err}").format(err=result.get('error', _('Unknown error'))),
                        is_error=True,
                    )

            # Sync electron directory
            electron_dir = pathlib.Path(paths.get("electron_dir", "./data/electron"))
            if electron_dir.exists():
                self.log_message(_("Syncing electron directory: {dir}").format(dir=electron_dir))
                self.update_status(_("Syncing electron directory..."), progress=60)

                result = self.sync_service.sync_directory(electron_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        _("electron sync complete: uploaded {up}, downloaded {down}").format(
                            up=result.get('uploaded', 0),
                            down=result.get('downloaded', 0),
                        )
                    )
                else:
                    self.log_message(
                        _("electron sync failed: {err}").format(err=result.get('error', _('Unknown error'))),
                        is_error=True,
                    )

            # Sync orbital directory (if exists)
            orbital_dir = pathlib.Path(paths.get("orbital_dir", "./data/orbital"))
            if orbital_dir.exists():
                self.log_message(_("Syncing orbital directory: {dir}").format(dir=orbital_dir))
                self.update_status(_("Syncing orbital directory..."), progress=80)

                result = self.sync_service.sync_directory(orbital_dir)  # type: ignore
                if result.get("success"):
                    self.log_message(
                        _("orbital sync complete: uploaded {up}, downloaded {down}").format(
                            up=result.get('uploaded', 0),
                            down=result.get('downloaded', 0),
                        )
                    )
                else:
                    self.log_message(
                        _("orbital sync failed: {err}").format(err=result.get('error', _('Unknown error'))),
                        is_error=True,
                    )

            # Sync complete
            self.update_status(_("Sync complete"), progress=100)
            self.log_message(_("All directories synced"))

        except Exception as e:
            self.log_message(_("Error during sync: {error}").format(error=e), is_error=True)
            self.update_status(_("Sync failed"))
        finally:
            # Reset sync state
            self.is_syncing = False
            self.is_paused = False
            self.update_button_states()  # type: ignore

    def pause_sync(self):
        """Pause sync"""
        if not self.is_syncing:
            return

        self.is_paused = not self.is_paused
        self.update_button_states()

        if self.is_paused:
            self.log_message(_("Sync paused"))
            self.update_status(_("Sync paused"))
        else:
            self.log_message(_("Sync resumed"))
            self.update_status(_("Syncing..."))

    def cancel_sync(self):
        """Cancel sync"""
        if not self.is_syncing:
            return

        self.is_syncing = False
        self.is_paused = False
        self.update_button_states()

        self.log_message(_("Sync cancelled"))
        self.update_status(_("Sync cancelled"))

    def update_button_states(self):
        """Update button states"""
        try:
            start_button = self.query_one("#start_sync")
            pause_button = self.query_one("#pause_sync")
            cancel_button = self.query_one("#cancel_sync")

            if self.is_syncing:
                start_button.disabled = True
                pause_button.disabled = False
                cancel_button.disabled = False
                pause_button.label = _("Resume") if self.is_paused else _("Pause")  # type: ignore
            else:
                start_button.disabled = False
                pause_button.disabled = True
                cancel_button.disabled = True

        except Exception as e:
            self.log_message(_("Failed to update button state: {error}").format(error=e), is_error=True)

    def action_go_back(self):
        self.app.pop_screen()

    def action_quit_app(self):
        self.app.exit()
