from textual.app import App
from textual.widgets import Button

from heurams.context import config_var
from heurams.interface import HeurAMSApp
from heurams.services.logger import get_logger

from .screens.about import AboutScreen
from .screens.dashboard import DashboardScreen
from .screens.precache import PrecachingScreen
from .screens.repocreator import RepoCreatorScreen

logger = get_logger(__name__)

def main():
    app = HeurAMSApp()
    app.run()

if __name__ == "__main__":
    main()