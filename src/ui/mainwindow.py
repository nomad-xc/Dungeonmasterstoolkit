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

        self.stack.addWidget(self.campaign_page)               # 0
        self.stack.addWidget(HeroesPage())                     # 1
        self.stack.addWidget(PlaceholderPage("Library"))       # 2
        self.stack.addWidget(PlaceholderPage("Scenes"))        # 3
        self.stack.addWidget(PlaceholderPage("Session"))       # 4
        self.stack.addWidget(PlaceholderPage("Player Display"))# 5
        self.stack.addWidget(PlaceholderPage("Settings"))      # 6

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

    def campaign_loaded(self, campaign_name):

        self.sidebar.show_campaign(campaign_name)

        self.setWindowTitle(
            f"Dungeon Master's Toolkit - {campaign_name}"
        )

        self.sidebar.setCurrentRow(3)