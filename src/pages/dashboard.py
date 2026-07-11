from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Dungeon Master's Toolkit")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()