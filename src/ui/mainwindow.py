from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
)

from src.pages.campaigns import CampaignPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dungeon Master's Toolkit")
        self.resize(1600, 900)

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        #
        # Top Navigation
        #
        nav = QWidget()
        nav_layout = QHBoxLayout(nav)

        pages = [
            "Dashboard",
            "Heroes",
            "Combat",
            "Initiative",
            "Maps",
            "Monster DB",
            "Sounds",
            "Settings",
        ]

        for page in pages:
            button = QPushButton(page)
            nav_layout.addWidget(button)

        root.addWidget(nav)

        #
        # Main Content
        #
        self.stack = QStackedWidget()

        self.stack.addWidget(CampaignPage())

        root.addWidget(self.stack)