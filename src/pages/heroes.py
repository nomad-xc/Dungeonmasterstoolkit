from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QSizePolicy,
)


class HeroCard(QFrame):

    def __init__(self):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(260)

        self.setStyleSheet("""
        QFrame{
            background:#2b2b2b;
            border:2px solid #555;
            border-radius:12px;
        }
        QLabel{
            color:white;
        }
        """)

        layout = QVBoxLayout(self)

        title = QLabel("New Hero")
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(QLabel("Class"))
        layout.addWidget(QLabel("HP : 0 / 0"))
        layout.addWidget(QLabel("MP : 0 / 0"))
        layout.addWidget(QLabel("AC : 0"))
        layout.addWidget(QLabel("Speed : 0"))

        layout.addStretch()


class HeroesPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Heroes")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.addHero = QPushButton("Add Hero")
        self.addHero.clicked.connect(self.add_hero)
        self.addHero.setMinimumHeight(40)

        layout.addWidget(self.addHero)

        self.grid = QGridLayout()

        self.grid.setSpacing(20)

        layout.addLayout(self.grid)

        #
        # Temporary demo card
        #

        self.grid.addWidget(HeroCard(), 0, 0)

        layout.addStretch()

    def add_hero(self):

        cards = self.grid.count()

        row = cards // 3
        col = cards % 3

        self.grid.addWidget(HeroCard(), row, col)