from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QLabel,
    QPushButton,
    QFrame,
)

from src.models.hero import Hero
from src.managers.hero_manager import HeroManager
from src.database.current_campaign import CurrentCampaign
from src.widgets.portrait_picker import pick_and_copy_portrait


PORTRAIT_SIZE = 120


class HeroPanel(QWidget):

    heroSaved = Signal()

    def __init__(self):
        super().__init__()

        self.hero = None

        root = QVBoxLayout(self)

        #
        # Portrait
        #

        portrait_row = QHBoxLayout()

        self.portrait_label = QLabel()
        self.portrait_label.setFixedSize(PORTRAIT_SIZE, PORTRAIT_SIZE)
        self.portrait_label.setStyleSheet("""
            background:#2b2b2b;
            border:2px solid #555;
            border-radius:8px;
        """)
        self.portrait_label.setAlignment(Qt.AlignCenter)

        portrait_row.addWidget(self.portrait_label)

        portrait_buttons = QVBoxLayout()

        self.portrait_button = QPushButton("Change Portrait")
        self.portrait_button.clicked.connect(self.change_portrait)
        portrait_buttons.addWidget(self.portrait_button)
        portrait_buttons.addStretch()

        portrait_row.addLayout(portrait_buttons)
        portrait_row.addStretch()

        root.addLayout(portrait_row)

        #
        # Form fields
        #

        form = QFormLayout()

        self.name = QLineEdit()
        form.addRow("Name", self.name)

        self.race = QLineEdit()
        form.addRow("Race", self.race)

        self.hero_class = QLineEdit()
        form.addRow("Class", self.hero_class)

        self.speed = QSpinBox()
        self.speed.setRange(0, 200)
        form.addRow("Speed", self.speed)

        self.level = QSpinBox()
        self.level.setRange(1, Hero.MAX_LEVEL)
        form.addRow("Level", self.level)

        self.xp = QSpinBox()
        self.xp.setRange(0, 99999999)
        form.addRow("XP", self.xp)

        self.hp = QSpinBox()
        self.hp.setRange(0, Hero.MAX_HP_CAP)
        form.addRow("HP", self.hp)

        self.max_hp = QSpinBox()
        self.max_hp.setRange(1, Hero.MAX_HP_CAP)
        form.addRow("Max HP", self.max_hp)

        self.mp = QSpinBox()
        self.mp.setRange(0, 9999)
        form.addRow("MP", self.mp)

        self.max_mp = QSpinBox()
        self.max_mp.setRange(0, 9999)
        form.addRow("Max MP", self.max_mp)

        self.base_armour = QSpinBox()
        self.base_armour.setRange(0, Hero.MAX_ARMOUR_CAP)
        self.base_armour.valueChanged.connect(self.update_total_armour)
        form.addRow("Base Armour", self.base_armour)

        self.armour_bonus = QSpinBox()
        self.armour_bonus.setRange(0, 99)
        self.armour_bonus.valueChanged.connect(self.update_total_armour)
        form.addRow("Armour Bonus", self.armour_bonus)

        self.total_armour_label = QLabel("0")
        form.addRow("Total Armour", self.total_armour_label)

        self.weapon_bonus = QSpinBox()
        self.weapon_bonus.setRange(0, 99)
        form.addRow("Weapon Bonus", self.weapon_bonus)

        self.trinket = QLineEdit()
        form.addRow("Trinket", self.trinket)

        root.addLayout(form)

        #
        # Conditions
        #

        conditions_label = QLabel("Conditions")
        conditions_label.setStyleSheet("font-weight:bold;")
        root.addWidget(conditions_label)

        conditions_grid = QGridLayout()

        self.condition_buttons = {}

        for index, condition in enumerate(Hero.CONDITIONS):

            button = QPushButton(condition)
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    background:#2b2b2b;
                    color:white;
                    border:2px solid #555;
                    border-radius:8px;
                    padding:6px;
                }

                QPushButton:checked {
                    background:#8b1a1a;
                    border:2px solid #d4af37;
                }
            """)

            self.condition_buttons[condition] = button

            row = index // 4
            col = index % 4

            conditions_grid.addWidget(button, row, col)

        root.addLayout(conditions_grid)

        #
        # Notes
        #

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes...")
        root.addWidget(self.notes)

        #
        # Save
        #

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        root.addWidget(self.save_button)

        self.load_hero(None)

    def update_total_armour(self):

        total = self.base_armour.value() + self.armour_bonus.value()
        self.total_armour_label.setText(str(total))

    def change_portrait(self):

        if self.hero is None or not CurrentCampaign.loaded():
            return

        dest_folder = CurrentCampaign.path() / "Images"

        path = pick_and_copy_portrait(self, dest_folder)

        if path:
            self.hero.portrait = path
            self.update_portrait_preview()

    def update_portrait_preview(self):

        if self.hero and self.hero.portrait and Path(self.hero.portrait).exists():

            pixmap = QPixmap(self.hero.portrait).scaled(
                PORTRAIT_SIZE,
                PORTRAIT_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.portrait_label.setPixmap(pixmap)

        else:
            self.portrait_label.clear()

    def load_hero(self, hero):

        self.hero = hero

        enabled = hero is not None
        self.setEnabled(enabled)

        if not enabled:
            self.portrait_label.clear()
            return

        self.name.setText(hero.name)
        self.race.setText(hero.race)
        self.hero_class.setText(hero.hero_class)

        self.speed.setValue(hero.speed)
        self.level.setValue(hero.level)
        self.xp.setValue(hero.xp)

        self.hp.setValue(hero.hp)
        self.max_hp.setValue(hero.max_hp)

        self.mp.setValue(hero.mp)
        self.max_mp.setValue(hero.max_mp)

        self.base_armour.setValue(hero.base_armour)
        self.armour_bonus.setValue(hero.armour_bonus)
        self.update_total_armour()

        self.weapon_bonus.setValue(hero.weapon_bonus)
        self.trinket.setText(hero.trinket)

        for condition, button in self.condition_buttons.items():
            button.setChecked(condition in hero.conditions)

        self.notes.setPlainText(hero.notes)

        self.update_portrait_preview()

    def save(self):

        if self.hero is None:
            return

        self.hero.name = self.name.text()
        self.hero.race = self.race.text()
        self.hero.hero_class = self.hero_class.text()

        self.hero.speed = self.speed.value()
        self.hero.level = self.level.value()
        self.hero.xp = self.xp.value()

        self.hero.hp = self.hp.value()
        self.hero.max_hp = self.max_hp.value()

        self.hero.mp = self.mp.value()
        self.hero.max_mp = self.max_mp.value()

        self.hero.base_armour = self.base_armour.value()
        self.hero.armour_bonus = self.armour_bonus.value()

        self.hero.weapon_bonus = self.weapon_bonus.value()
        self.hero.trinket = self.trinket.text()

        self.hero.conditions = [
            condition
            for condition, button in self.condition_buttons.items()
            if button.isChecked()
        ]

        self.hero.notes = self.notes.toPlainText()

        HeroManager.save_hero(self.hero)

        self.heroSaved.emit()
