from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
)

from src.widgets.sidebar import Sidebar

from src.pages.campaigns import CampaignPage
from src.pages.heroes import HeroesPage
from src.pages.library import LibraryPage
from src.pages.session import SessionPage
from src.pages.gameplay import GameplayPage
from src.pages.player_display import PlayerDisplayPage
from src.database.session_state import SessionState


class PlaceholderPage(QWidget):

    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(title)
        label.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
        """)

        layout.addWidget(label)
        layout.addStretch()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dungeon Master's Toolkit")
        self.resize(1600, 900)

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        #
        # Sidebar
        #

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        #
        # Pages
        #

        self.stack = QStackedWidget()

        self.campaign_page = CampaignPage()
        self.campaign_page.campaignOpened.connect(self.campaign_loaded)

        # KEEP REFERENCES TO PAGES
        self.heroes_page = HeroesPage()

        self.library_page = LibraryPage()

        self.session_page = SessionPage()
        self.gameplay_page = GameplayPage()
        self.player_display_page = PlayerDisplayPage(
            open_library_tokens=self.show_library_tokens_tab
        )

        self.stack.addWidget(self.campaign_page)                    # 0
        self.stack.addWidget(self.heroes_page)                      # 1
        self.stack.addWidget(self.library_page)                     # 2
        self.stack.addWidget(self.session_page)                     # 3
        self.stack.addWidget(self.gameplay_page)                    # 4
        self.stack.addWidget(self.player_display_page)              # 5
        self.stack.addWidget(PlaceholderPage("Settings"))           # 6

        root.addWidget(self.stack)

        self.sidebar.currentRowChanged.connect(self.change_page)

        self.sidebar.setCurrentRow(0)

    def change_page(self, row):

        if self.sidebar.count() == 2:

            mapping = {
                0: 0,
                1: 2,
            }

        else:

            mapping = {
                0: 0,
                1: 2,
                3: 1,
                4: 3,
                5: 4,
                6: 5,
                7: 6,
            }

        if row in mapping:
            self.stack.setCurrentIndex(mapping[row])

    def show_library_tokens_tab(self):

        for i in range(self.library_page.tabs.count()):
            if self.library_page.tabs.tabText(i) == "Tokens":
                self.library_page.tabs.setCurrentIndex(i)
                break

        self.sidebar.setCurrentRow(1)

    def campaign_loaded(self, campaign_name):

        self.sidebar.show_campaign(campaign_name)

        self.setWindowTitle(
            f"Dungeon Master's Toolkit - {campaign_name}"
        )

        SessionState.reset()

        # THIS IS THE IMPORTANT PART
        self.heroes_page.refresh()
        self.session_page.refresh()
        self.gameplay_page.refresh()
        self.player_display_page.refresh()

        self.sidebar.setCurrentRow(3)