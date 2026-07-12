from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QInputDialog,
)

from src.managers.hero_manager import HeroManager
from src.widgets.hero_panel import HeroPanel


class HeroesPage(QWidget):

    def __init__(self):
        super().__init__()

        self.heroes = []

        root = QHBoxLayout(self)

        #
        # Left: hero list
        #

        left = QVBoxLayout()

        title = QLabel("Heroes")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)
        left.addWidget(title)

        self.add_button = QPushButton("Add Hero")
        self.add_button.clicked.connect(self.add_hero)
        left.addWidget(self.add_button)

        self.hero_list = QListWidget()
        self.hero_list.currentRowChanged.connect(self.select_hero)
        left.addWidget(self.hero_list)

        root.addLayout(left, 1)

        #
        # Right: editable panel
        #

        self.panel = HeroPanel()
        self.panel.heroSaved.connect(self.refresh)

        root.addWidget(self.panel, 2)

        self.refresh()

    def refresh(self, select_name=None):

        if select_name is None:
            current_item = self.hero_list.currentItem()
            select_name = current_item.text() if current_item else None

        self.hero_list.blockSignals(True)
        self.hero_list.clear()

        self.heroes = HeroManager.load_heroes()

        for hero in self.heroes:
            self.hero_list.addItem(hero.name)

        self.hero_list.blockSignals(False)

        if self.heroes:

            restored_row = 0

            if select_name is not None:
                for index, hero in enumerate(self.heroes):
                    if hero.name == select_name:
                        restored_row = index
                        break

            self.hero_list.setCurrentRow(restored_row)
            self.select_hero(restored_row)

        else:
            self.panel.load_hero(None)

    def select_hero(self, row):

        if 0 <= row < len(self.heroes):
            self.panel.load_hero(self.heroes[row])
        else:
            self.panel.load_hero(None)

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

        self.refresh(select_name=name)
