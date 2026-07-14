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
    QScrollArea,
    QTabWidget,
)

from src.managers.monster_manager import MonsterManager
from src.widgets.monster_editor import MonsterEditor


PORTRAIT_SIZE = 80


def clear_layout(layout):

    while layout.count():

        item = layout.takeAt(0)

        widget = item.widget()
        if widget:
            widget.deleteLater()

        sub_layout = item.layout()
        if sub_layout:
            clear_layout(sub_layout)


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

        outer = QVBoxLayout(self)

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs)

        self.monster_container = QVBoxLayout()
        monster_tab = self._build_kind_tab(
            self.monster_container, "monster", "Add Monster"
        )
        self.tabs.addTab(monster_tab, "Monsters")

        self.villain_container = QVBoxLayout()
        villain_tab = self._build_kind_tab(
            self.villain_container, "villain", "Add Villain"
        )
        self.tabs.addTab(villain_tab, "Villains")

        self.refresh()

    def _build_kind_tab(self, container, kind, add_label):

        tab = QWidget()
        layout = QVBoxLayout(tab)

        add_button = QPushButton(add_label)
        add_button.clicked.connect(lambda checked=False, k=kind: self.add_monster(k))
        layout.addWidget(add_button)

        sections_widget = QWidget()
        sections_widget.setLayout(container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sections_widget)
        layout.addWidget(scroll)

        return tab

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()

    def refresh(self):

        self._refresh_section(self.monster_container, "monster")
        self._refresh_section(self.villain_container, "villain")

    def _refresh_section(self, container, kind):

        clear_layout(container)

        monsters = MonsterManager.load_monsters(kind=kind)

        groups = {}

        for monster in monsters:
            key = monster.creature_type or "Unsorted"
            groups.setdefault(key, []).append(monster)

        for type_name in sorted(groups.keys()):

            type_label = QLabel(type_name)
            type_label.setStyleSheet("""
                font-size:18px;
                font-weight:bold;
                color:#d4af37;
            """)
            container.addWidget(type_label)

            grid = QGridLayout()
            grid.setSpacing(20)

            for index, monster in enumerate(groups[type_name]):

                row = index // 3
                col = index % 3

                grid.addWidget(
                    MonsterCard(monster, self.refresh),
                    row,
                    col
                )

            container.addLayout(grid)

        container.addStretch()

    def add_monster(self, kind):

        label = "Villain" if kind == "villain" else "Monster"

        name, ok = QInputDialog.getText(
            self,
            f"New {label}",
            f"{label} Name:"
        )

        if not ok or not name:
            return

        MonsterManager.create_monster(name, kind=kind)

        self.refresh()
