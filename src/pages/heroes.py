from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QInputDialog,
)

from src.managers.hero_manager import HeroManager


class HeroCard(QFrame):

    def __init__(self, hero, refresh_callback):
        super().__init__()

        self.hero = hero
        self.refresh_callback = refresh_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(220)

        self.setStyleSheet("""
        QFrame{
            background:#2b2b2b;
            border:2px solid #555;
            border-radius:12px;
        }

        QLabel{
            color:white;
        }

        QFrame:hover{
            border:2px solid #d4af37;
        }
        """)

        layout = QVBoxLayout(self)

        title = QLabel(hero.name)
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(QLabel(hero.hero_class))
        layout.addWidget(QLabel(f"Level {hero.level}"))
        layout.addWidget(QLabel(f"HP {hero.hp}/{hero.max_hp}"))
        layout.addWidget(QLabel(f"MP {hero.mp}/{hero.max_mp}"))
        layout.addWidget(QLabel(f"AC {hero.ac}"))
        layout.addWidget(QLabel(f"Gold {hero.gold}"))

        layout.addStretch()

    def mouseDoubleClickEvent(self, event):

        from src.widgets.hero_editor import HeroEditor

        editor = HeroEditor(self.hero)

        if editor.exec():

            HeroManager.save_hero(self.hero)

            self.refresh_callback()


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

        self.add_button = QPushButton("Add Hero")
        self.add_button.clicked.connect(self.add_hero)

        layout.addWidget(self.add_button)

        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        layout.addLayout(self.grid)

        layout.addStretch()

        self.refresh()

    def refresh(self):

        while self.grid.count():

            item = self.grid.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        heroes = HeroManager.load_heroes()

        for index, hero in enumerate(heroes):

            row = index // 3
            col = index % 3

            self.grid.addWidget(
                 HeroCard(hero, self.refresh),
                 row,
                 col
            )

    def add_hero(self):

        name, ok = QInputDialog.getText(
            self,
            "New Hero",
            "Hero Name:"
        )

        if not ok or not name:
            return

        hero_class, ok = QInputDialog.getText(
            self,
            "Hero Class",
            "Class:"
        )

        if not ok or not hero_class:
            return

        HeroManager.create_hero(
            name,
            hero_class
        )

        self.refresh()