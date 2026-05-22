"""Favorites manager screen"""

import base64
from pathlib import Path
from typing import List, Optional

from textual import events, on

from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from textual import events, on
from heurams.context import config_var
from heurams.i18n import _
from heurams.kernel.repolib import Repo
from heurams.services.favorite_service import FavoriteItem, favorite_manager
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class FavoriteManagerScreen(Screen):
    """Favorites manager screen"""

    SUB_TITLE = _("Favorites")

    BINDINGS = [
        ("q", "go_back", _("Back")),
        ("d", "toggle_dark", ""),
    ]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.favorites: List[FavoriteItem] = []
        self._load_favorites()

    def _load_favorites(self) -> None:
        """Load favorites list"""
        self.favorites = favorite_manager.get_all()
        logger.info("Loaded %d favorites", len(self.favorites))

    def compose(self) -> ComposeResult:
        """Compose UI components"""

        if config_var.get()["interface"]["global"]["show_header"]:
            yield Header(
                show_clock=config_var.get()["interface"]["global"]["clock_on_header"]
            )
        with ScrollableContainer(id="favorites-container"):
            if not self.favorites:
                yield Label(_("No favorites"), classes="empty-label")
                yield Static(_("Press * in the memorization screen to add favorites."))
            else:
                yield Label(_("Total {n} favorite(s)").format(n=len(self.favorites)), classes="count-label")
                yield ListView(id="favorites-list")
        yield Footer()

    @on(events.ScreenResume)
    def post_active(self, event):
        from heurams.interface import shim

        shim.set_term_title(f"{self.app.TITLE} - {self.SUB_TITLE}")

    def on_mount(self) -> None:
        """挂载后填充列表"""
        if self.favorites:
            list_view = self.query_one("#favorites-list")
            for fav in self.favorites:
                list_view.append(self._create_favorite_item(fav))  # type: ignore

    def _encode_favorite_key(self, repo_path: str, ident: str) -> str:
        """Encode repo path and identifier into a safe button ID part"""
        # Use \x00 as separator between the two parts, then base64 encode
        combined = f"{repo_path}\x00{ident}"
        encoded = base64.urlsafe_b64encode(combined.encode()).decode()
        # Strip padding
        return encoded.rstrip("=")

    def _decode_favorite_key(self, key: str) -> tuple[str, str]:
        """Decode button ID part back to repo path and identifier"""
        # Pad to make length multiple of 4
        padded = key + "=" * ((4 - len(key) % 4) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        repo_path, ident = decoded.split("\x00", 1)
        return repo_path, ident

    def _create_favorite_item(self, fav: FavoriteItem) -> ListItem:
        """Create a favorite list item"""
        # Try to get repo info
        repo_info = self._get_repo_info(fav.repo_path, fav)
        title = repo_info.get("title", fav.repo_path) if repo_info else fav.repo_path
        added_time = self._format_time(fav.added)

        # Build display text
        display_text = f"{fav.ident}\n"
        display_text += _("  [d]Added: {time}\n  From {title}[/d]").format(time=added_time, title=title)
        if fav.tags:
            display_text += f"{', '.join(fav.tags)}"

        # Create safe button ID
        button_key = self._encode_favorite_key(fav.repo_path, fav.ident)
        # Create list item with remove button
        container = Horizontal(
            Label(display_text, classes="favorite-content"),
            Button(
                _("Remove"),
                id=f"remove-{button_key}",
                variant="error",
                flat=True,
                classes="favorite-item-btn",
            ),
            classes="favorite-item",
        )
        return ListItem(container)

    def _get_repo_info(self, repo_path: str, fav: FavoriteItem) -> Optional[dict]:
        """Get repo info (title, atom content preview)"""
        try:
            data_repo = Path(config_var.get()["global"]["paths"]["data"]) / "repo"
            repo_dir = data_repo / repo_path
            if not repo_dir.exists():
                logger.warning("Repo directory does not exist: %s", repo_dir)
                return None
            repo = Repo.from_repodir(repo_dir)
            # Get atom content preview
            content_preview = ""
            payload = repo.payload
            # Find the payload entry matching ident
            for ident_key, content in payload:
                if ident_key == fav.ident:
                    # Truncate long content
                    if isinstance(content, dict) and "content" in content:
                        text = content["content"]
                    else:
                        text = str(content)
                    if len(text) > 100:
                        content_preview = text[:100] + "..."
                    else:
                        content_preview = text
                    break
            return {
                "title": repo.manifest["title"],
                "content_preview": content_preview,
            }
        except Exception as e:
            logger.error("Failed to get repo info: %s", e)
            return None

    def _format_time(self, timestamp: int) -> str:
        """Format timestamp as datetime string"""
        from datetime import datetime

        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press event"""
        button_id = event.button.id
        if button_id and button_id.startswith("remove-"):
            # Extract encoded key
            key = button_id[7:]  # Remove "remove-" prefix
            try:
                repo_path, ident = self._decode_favorite_key(key)
                self._remove_favorite(repo_path, ident)
            except Exception as e:
                logger.error("Failed to parse button ID: %s", e)
                self.app.notify(_("Operation failed: invalid button identifier"), severity="error")

    def _remove_favorite(self, repo_path: str, ident: str) -> None:
        """Remove a favorite item"""
        if favorite_manager.remove(repo_path, ident):
            self.app.notify(_("Removed favorite: {ident}").format(ident=ident), severity="information")
            # Reload list
            self._load_favorites()
            # Refresh UI
            self._refresh_list()
        else:
            self.app.notify(_("Failed to remove: {ident}").format(ident=ident), severity="error")

    def _refresh_list(self) -> None:
        """Refresh the list display"""
        container = self.query_one("#favorites-container")
        # Clear container
        for child in container.children:
            child.remove()
        # Re-compose
        if not self.favorites:
            container.mount(Label(_("No favorites"), classes="empty-label"))
            container.mount(Static(_("Press * in the memorization screen to add favorites.")))
        else:
            container.mount(
                Label(_("Total {n} favorite(s)").format(n=len(self.favorites)), classes="count-label")
            )
            list_view = ListView(id="favorites-list")
            container.mount(list_view)
            for fav in self.favorites:
                list_view.append(self._create_favorite_item(fav))

    def action_go_back(self) -> None:
        """返回上一屏幕"""
        self.app.pop_screen()

    def action_toggle_dark(self) -> None:
        """切换暗黑模式"""
        self.app.dark = not self.app.dark  # type: ignore
