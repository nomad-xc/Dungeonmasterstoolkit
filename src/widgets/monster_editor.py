from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QLabel,
    QPushButton,
)

from src.widgets.portrait_picker import pick_and_copy_portrait


PORTRAIT_SIZE = 120
PORTRAIT_FOLDER = Path("library/portraits")


class MonsterEditor(QDialog):

    def __init__(self, monster):
        super().__init__()

        self.monster = monster

        self.setWindowTitle(monster.name)
        self.resize(500, 650)

        layout = QVBoxLayout(self)

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

        self.portrait_button = QPushButton("Change Portrait")
        self.portrait_button.clicked.connect(self.change_portrait)
        portrait_row.addWidget(self.portrait_button)
        portrait_row.addStretch()

        layout.addLayout(portrait_row)

        self.update_portrait_preview()

        #
        # Form
        #

        form = QFormLayout()

        self.name = QLineEdit(monster.name)
        form.addRow("Name", self.name)

        self.hp = QSpinBox()
        self.hp.setRange(0, 9999)
        self.hp.setValue(monster.hp)
        form.addRow("HP", self.hp)

        self.max_hp = QSpinBox()
        self.max_hp.setRange(1, 9999)
        self.max_hp.setValue(monster.max_hp)
        form.addRow("Max HP", self.max_hp)

        self.ac = QSpinBox()
        self.ac.setRange(0, 99)
        self.ac.setValue(monster.ac)
        form.addRow("AC", self.ac)

        self.speed = QSpinBox()
        self.speed.setRange(0, 200)
        self.speed.setValue(monster.speed)
        form.addRow("Speed", self.speed)

        self.xp = QSpinBox()
        self.xp.setRange(0, 99999999)
        self.xp.setValue(monster.xp)
        form.addRow("XP", self.xp)

        layout.addLayout(form)

        self.description = QTextEdit(monster.description)
        self.description.setPlaceholderText("Description...")
        layout.addWidget(self.description)

        self.abilities = QTextEdit(monster.abilities)
        self.abilities.setPlaceholderText("Abilities...")
        layout.addWidget(self.abilities)

        self.behavior = QTextEdit(monster.behavior)
        self.behavior.setPlaceholderText("Behavior...")
        layout.addWidget(self.behavior)

        self.notes = QTextEdit(monster.notes)
        self.notes.setPlaceholderText("Notes...")
        layout.addWidget(self.notes)

        buttons = QHBoxLayout()

        save = QPushButton("Save")
        cancel = QPushButton("Cancel")

        save.clicked.connect(self.save)
        cancel.clicked.connect(self.reject)

        buttons.addWidget(save)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

    def update_portrait_preview(self):

        if self.monster.portrait and Path(self.monster.portrait).exists():

            pixmap = QPixmap(self.monster.portrait).scaled(
                PORTRAIT_SIZE,
                PORTRAIT_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.portrait_label.setPixmap(pixmap)

        else:
            self.portrait_label.clear()

    def change_portrait(self):

        path = pick_and_copy_portrait(self, PORTRAIT_FOLDER)

        if path:
            self.monster.portrait = path
            self.update_portrait_preview()

    def save(self):

        self.monster.name = self.name.text()

        self.monster.hp = self.hp.value()
        self.monster.max_hp = self.max_hp.value()

        self.monster.ac = self.ac.value()
        self.monster.speed = self.speed.value()

        self.monster.xp = self.xp.value()

        self.monster.description = self.description.toPlainText()
        self.monster.abilities = self.abilities.toPlainText()
        self.monster.behavior = self.behavior.toPlainText()
        self.monster.notes = self.notes.toPlainText()

        self.accept()
