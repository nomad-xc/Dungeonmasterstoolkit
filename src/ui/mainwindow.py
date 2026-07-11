from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QStackedWidget,
    QLabel,
)

from src.pages.campaigns import CampaignPage
from src.pages.heroes import HeroesPage


class PlaceholderPage(QWidget):
    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(title)
        label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
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
        self.menu = QListWidget()
        self.menu.setFixedWidth(220)

        self.menu.addItems([
            "Campaigns",
            "Heroes",
            "Library",
            "Scenes",
            "Session",
            "Player Display",
            "Settings",
        ])

        # Disable campaign-specific pages
        for index in [1, 3, 4, 5]:
            item = self.menu.item(index)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)

        root.addWidget(self.menu)

        #
        # Pages
        #
        self.stack = QStackedWidget()

        self.stack.addWidget(CampaignPage())                     # 0
        self.stack.addWidget(HeroesPage())                       # 1
        self.stack.addWidget(PlaceholderPage("Library"))         # 2
        self.stack.addWidget(PlaceholderPage("Scenes"))          # 3
        self.stack.addWidget(PlaceholderPage("Session"))         # 4
        self.stack.addWidget(PlaceholderPage("Player Display"))  # 5
        self.stack.addWidget(PlaceholderPage("Settings"))        # 6

        root.addWidget(self.stack)

        self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)

        self.menu.setCurrentRow(0)

    def unlock_campaign(self):
        """Enable campaign-specific pages."""

        for index in [1, 3, 4, 5]:
            item = self.menu.item(index)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)