from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
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
from src.managers.map_manager import MapManager
from src.managers.token_manager import TokenManager
from src.widgets.monster_editor import MonsterEditor
from src.widgets.map_editor import MapEditor
from src.widgets.portrait_picker import pick_and_copy_images


PORTRAIT_SIZE = 80
MAP_THUMB_WIDTH = 220
MAP_THUMB_HEIGHT = 140
TOKEN_THUMB_SIZE = 120


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


class MapCard(QFrame):

    def __init__(self, map_obj, refresh_callback):
        super().__init__()

        self.map_obj = map_obj
        self.refresh_callback = refresh_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(220)
        self.setMaximumWidth(240)

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

        thumb_label = QLabel()
        thumb_label.setFixedSize(MAP_THUMB_WIDTH, MAP_THUMB_HEIGHT)
        thumb_label.setAlignment(Qt.AlignCenter)

        if map_obj.path and Path(map_obj.path).exists():
            pixmap = QPixmap(map_obj.path).scaled(
                MAP_THUMB_WIDTH,
                MAP_THUMB_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            thumb_label.setPixmap(pixmap)

        layout.addWidget(thumb_label)

        title = QLabel(map_obj.name)
        title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        layout.addWidget(QLabel(map_obj.category or "Unsorted"))

        layout.addStretch()

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_map)
        layout.addWidget(delete_button)

    def mouseDoubleClickEvent(self, event):

        editor = MapEditor(self.map_obj)

        if editor.exec():

            MapManager.save_map(self.map_obj)

            self.refresh_callback()

    def delete_map(self):

        confirm = QMessageBox.question(
            self,
            "Delete Map",
            f"Delete '{self.map_obj.name}' from the library?"
        )

        if confirm == QMessageBox.Yes:
            MapManager.delete_map(self.map_obj)
            self.refresh_callback()


class TokenCard(QFrame):

    def __init__(self, token, refresh_callback):
        super().__init__()

        self.token = token
        self.refresh_callback = refresh_callback

        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(180)

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

        thumb_label = QLabel()
        thumb_label.setFixedSize(TOKEN_THUMB_SIZE, TOKEN_THUMB_SIZE)
        thumb_label.setAlignment(Qt.AlignCenter)

        if token.path and Path(token.path).exists():
            pixmap = QPixmap(token.path).scaled(
                TOKEN_THUMB_SIZE,
                TOKEN_THUMB_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            thumb_label.setPixmap(pixmap)

        layout.addWidget(thumb_label)

        title = QLabel(token.name)
        title.setStyleSheet("font-weight:bold;")
        layout.addWidget(title)

        layout.addStretch()

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_token)
        layout.addWidget(delete_button)

    def mouseDoubleClickEvent(self, event):

        name, ok = QInputDialog.getText(
            self,
            "Rename Token",
            "Token Name:",
            text=self.token.name
        )

        if not ok or not name or name == self.token.name:
            return

        self.token.name = name
        TokenManager.save_token(self.token)

        self.refresh_callback()

    def delete_token(self):

        confirm = QMessageBox.question(
            self,
            "Delete Token",
            f"Delete '{self.token.name}' from the library?"
        )

        if confirm == QMessageBox.Yes:
            TokenManager.delete_token(self.token)
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

        self.map_container = QVBoxLayout()
        map_tab = self._build_map_tab(self.map_container)
        self.tabs.addTab(map_tab, "Maps")

        self.token_container = QVBoxLayout()
        token_tab = self._build_token_tab(self.token_container)
        self.tabs.addTab(token_tab, "Tokens")

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

    def _build_map_tab(self, container):

        tab = QWidget()
        layout = QVBoxLayout(tab)

        buttons_row = QHBoxLayout()

        add_button = QPushButton("Add Map(s)")
        add_button.clicked.connect(self.add_maps)
        buttons_row.addWidget(add_button)

        new_folder_button = QPushButton("New Folder")
        new_folder_button.clicked.connect(self.add_map_folder)
        buttons_row.addWidget(new_folder_button)

        layout.addLayout(buttons_row)

        sections_widget = QWidget()
        sections_widget.setLayout(container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sections_widget)
        layout.addWidget(scroll)

        return tab

    def _build_token_tab(self, container):

        tab = QWidget()
        layout = QVBoxLayout(tab)

        add_button = QPushButton("Add Token(s)")
        add_button.clicked.connect(self.add_tokens)
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
        self._refresh_maps_section(self.map_container)
        self._refresh_tokens_section(self.token_container)

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

    def _refresh_maps_section(self, container):

        clear_layout(container)

        maps = MapManager.load_maps()

        groups = {folder: [] for folder in MapManager.load_folders()}

        for map_obj in maps:
            key = map_obj.category or "Unsorted"
            groups.setdefault(key, []).append(map_obj)

        for category in sorted(groups.keys()):

            category_label = QLabel(category)
            category_label.setStyleSheet("""
                font-size:18px;
                font-weight:bold;
                color:#d4af37;
            """)
            container.addWidget(category_label)

            grid = QGridLayout()
            grid.setSpacing(20)

            for index, map_obj in enumerate(groups[category]):

                row = index // 3
                col = index % 3

                grid.addWidget(
                    MapCard(map_obj, self.refresh),
                    row,
                    col,
                    Qt.AlignLeft | Qt.AlignTop
                )

            for col in range(3):
                grid.setColumnStretch(col, 0)

            grid.setColumnStretch(3, 1)

            container.addLayout(grid)

        container.addStretch()

    def add_maps(self):

        paths = pick_and_copy_images(
            self, MapManager.images_folder(), title="Choose Map Images"
        )

        for path in paths:
            MapManager.create_map(Path(path).stem, path)

        if paths:
            self.refresh()

    def add_map_folder(self):

        name, ok = QInputDialog.getText(
            self,
            "New Folder",
            "Folder Name:"
        )

        if not ok or not name:
            return

        MapManager.create_folder(name)

        self.refresh()

    def _refresh_tokens_section(self, container):

        clear_layout(container)

        tokens = TokenManager.load_tokens()

        grid = QGridLayout()
        grid.setSpacing(20)

        for index, token in enumerate(tokens):

            row = index // 4
            col = index % 4

            grid.addWidget(
                TokenCard(token, self.refresh),
                row,
                col
            )

        container.addLayout(grid)
        container.addStretch()

    def add_tokens(self):

        paths = pick_and_copy_images(
            self, TokenManager.images_folder(), title="Choose Token Images"
        )

        for path in paths:
            TokenManager.create_token(Path(path).stem, path)

        if paths:
            self.refresh()
