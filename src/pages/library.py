from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QInputDialog,
    QMessageBox,
)

from src.managers.monster_manager import MonsterManager
from src.widgets.monster_editor import MonsterEditor


PORTRAIT_SIZE = 80


class MonsterCard(QFrame):

    def __init__(self, monster, refresh_callback):
        super().__init__()

        self.monster = monster
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

        portrait_label = QLabel()
        portrait_label.setFixedSize(PORTRAIT_SIZE, PORTRAIT_SIZE)
        portrait_label.setAlignment(Qt.AlignCenter)

        if monster.portrait and Path(monster.portrait).exists():
            pixmap = QPixmap(monster.portrait).scaled(
                PORTRAIT_SIZE,
                PORTRAIT_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            portrait_label.setPixmap(pixmap)

        layout.addWidget(portrait_label)

        title = QLabel(monster.name)
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(QLabel(f"HP {monster.hp}/{monster.max_hp}"))
        layout.addWidget(QLabel(f"AC {monster.ac}"))
        layout.addWidget(QLabel(f"Speed {monster.speed}"))
        layout.addWidget(QLabel(f"XP {monster.xp}"))

        layout.addStretch()

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_monster)
        layout.addWidget(delete_button)

    def mouseDoubleClickEvent(self, event):

        editor = MonsterEditor(self.monster)

        if editor.exec():

            MonsterManager.save_monster(self.monster)

            self.refresh_callback()

    def delete_monster(self):

        confirm = QMessageBox.question(
            self,
            "Delete Monster",
            f"Delete '{self.monster.name}' from the library?"
        )

        if confirm == QMessageBox.Yes:
            MonsterManager.delete_monster(self.monster)
            self.refresh_callback()


class LibraryPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Library")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.add_button = QPushButton("Add Monster")
        self.add_button.clicked.connect(self.add_monster)

        layout.addWidget(self.add_button)

        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        layout.addLayout(self.grid)

        layout.addStretch()

        self.refresh()

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()

    def refresh(self):

        while self.grid.count():

            item = self.grid.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        monsters = MonsterManager.load_monsters()

        for index, monster in enumerate(monsters):

            row = index // 3
            col = index % 3

            self.grid.addWidget(
                MonsterCard(monster, self.refresh),
                row,
                col
            )

    def add_monster(self):

        name, ok = QInputDialog.getText(
            self,
            "New Monster",
            "Monster Name:"
        )

        if not ok or not name:
            return

        MonsterManager.create_monster(name)

        self.refresh()
