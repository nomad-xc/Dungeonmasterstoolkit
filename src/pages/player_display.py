from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QFrame,
    QScrollArea,
    QTabWidget,
    QGraphicsView,
    QGraphicsPixmapItem,
)

from src.managers.map_manager import MapManager
from src.managers.token_manager import TokenManager
from src.managers.hero_manager import HeroManager
from src.managers.player_display_manager import PlayerDisplayManager
from src.database.current_campaign import CurrentCampaign
from src.widgets.portrait_picker import pick_and_copy_portrait
from src.widgets.primary_button import PrimaryButton
from src.widgets.canvas_items import (
    DisplayScene,
    TokenItem,
    HeroRingItem,
    MapBackgroundItem,
    InitiativeTrackerItem,
    SCENE_WIDTH,
    SCENE_HEIGHT,
)
from src.widgets.tv_display_window import TVDisplayWindow


MAP_THUMB_WIDTH = 180
MAP_THUMB_HEIGHT = 115

TOKEN_THUMB_SIZE = 90
HERO_THUMB_SIZE = 90


class DisplayMapCard(QFrame):

    def __init__(self, map_obj, select_callback):
        super().__init__()

        self.map_obj = map_obj
        self.select_callback = select_callback

        self.setFrameShape(QFrame.StyledPanel)
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
        title.setStyleSheet("font-weight:bold;")
        layout.addWidget(title)

    def mousePressEvent(self, event):
        self.select_callback(self.map_obj)


class InitiativePickerCard(QFrame):

    def __init__(self, add_callback):
        super().__init__()

        self.add_callback = add_callback

        self.setFrameShape(QFrame.StyledPanel)
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

        title = QLabel("Initiative")
        title.setStyleSheet("font-weight:bold; font-size:16px;")
        layout.addWidget(title)

        subtitle = QLabel("Live turn order tracker")
        subtitle.setStyleSheet("color:#999;")
        layout.addWidget(subtitle)

    def mousePressEvent(self, event):
        self.add_callback()


class HeroPickerCard(QFrame):

    def __init__(self, hero, select_callback):
        super().__init__()

        self.hero = hero
        self.select_callback = select_callback

        self.setFrameShape(QFrame.StyledPanel)
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

        layout = QHBoxLayout(self)

        thumb_label = QLabel()
        thumb_label.setFixedSize(HERO_THUMB_SIZE, HERO_THUMB_SIZE)
        thumb_label.setAlignment(Qt.AlignCenter)

        if hero.portrait and Path(hero.portrait).exists():
            pixmap = QPixmap(hero.portrait).scaled(
                HERO_THUMB_SIZE,
                HERO_THUMB_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            thumb_label.setPixmap(pixmap)

        layout.addWidget(thumb_label)

        title = QLabel(hero.name)
        title.setStyleSheet("font-weight:bold;")
        layout.addWidget(title)

        layout.addStretch()

    def mousePressEvent(self, event):
        self.select_callback(self.hero)


class TokenPickerCard(QFrame):

    def __init__(self, token, select_callback):
        super().__init__()

        self.token = token
        self.select_callback = select_callback

        self.setFrameShape(QFrame.StyledPanel)
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

        layout = QHBoxLayout(self)

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

    def mousePressEvent(self, event):
        self.select_callback(self.token)


class FitGraphicsView(QGraphicsView):

    def __init__(self, scene):
        super().__init__(scene)

        self.delete_callback = None
        self.setFocusPolicy(Qt.StrongFocus)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.IgnoreAspectRatio)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete and self.delete_callback:
            self.delete_callback()
            event.accept()
            return

        super().keyPressEvent(event)


class PlayerDisplayPage(QWidget):

    def __init__(self, open_library_tokens=None):
        super().__init__()

        self.open_library_tokens = open_library_tokens

        self.display = PlayerDisplayManager.load_display()
        self.scene = DisplayScene()
        self.backdrop_item = None
        self.background_item = None
        self.selected_item = None
        self.tv_window = None

        root = QVBoxLayout(self)

        #
        # Top bar
        #

        top_bar = QHBoxLayout()

        title = QLabel("Player Display")
        title.setStyleSheet("font-size:28px; font-weight:bold;")
        top_bar.addWidget(title)

        top_bar.addStretch()

        self.backdrop_button = QPushButton("Choose Background")
        self.backdrop_button.clicked.connect(self.choose_backdrop)
        top_bar.addWidget(self.backdrop_button)

        self.tv_button = PrimaryButton("TV Display")
        self.tv_button.clicked.connect(self.open_tv_display)
        top_bar.addWidget(self.tv_button)

        root.addLayout(top_bar)

        #
        # Body: left tabs + canvas
        #

        body = QHBoxLayout()

        left = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(270)

        maps_tab = QWidget()
        maps_tab_layout = QVBoxLayout(maps_tab)

        self.maps_container = QVBoxLayout()

        maps_inner = QWidget()
        maps_inner.setLayout(self.maps_container)

        maps_scroll = QScrollArea()
        maps_scroll.setWidgetResizable(True)
        maps_scroll.setWidget(maps_inner)

        maps_tab_layout.addWidget(maps_scroll)

        self.tabs.addTab(maps_tab, "Maps")

        widgets_tab = QWidget()
        widgets_tab_layout = QVBoxLayout(widgets_tab)

        self.widgets_container = QVBoxLayout()

        widgets_inner = QWidget()
        widgets_inner.setLayout(self.widgets_container)

        widgets_scroll = QScrollArea()
        widgets_scroll.setWidgetResizable(True)
        widgets_scroll.setWidget(widgets_inner)

        widgets_tab_layout.addWidget(widgets_scroll)

        self.tabs.addTab(widgets_tab, "Widgets")

        left.addWidget(self.tabs)

        body.addLayout(left)

        #
        # Canvas
        #

        canvas_col = QVBoxLayout()
        canvas_col.setContentsMargins(16, 16, 16, 16)

        self.view = FitGraphicsView(self.scene)
        self.view.setMinimumSize(SCENE_WIDTH * 2 // 5, SCENE_HEIGHT * 2 // 5)
        self.view.delete_callback = self.remove_selected
        self.view.setStyleSheet("""
            QGraphicsView {
                border: 3px solid white;
                background: #000000;
            }
        """)
        canvas_col.addWidget(self.view)

        #
        # Selection toolbar
        #

        self.selection_toolbar = QHBoxLayout()

        self.visible_checkbox = QCheckBox("Visible to Players")
        self.visible_checkbox.toggled.connect(self.toggle_visibility)
        self.selection_toolbar.addWidget(self.visible_checkbox)

        self.lock_checkbox = QCheckBox("Lock")
        self.lock_checkbox.toggled.connect(self.toggle_lock)
        self.selection_toolbar.addWidget(self.lock_checkbox)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        self.selection_toolbar.addWidget(self.remove_button)

        self.selection_toolbar.addStretch()

        self.selection_toolbar_widget = QWidget()
        self.selection_toolbar_widget.setLayout(self.selection_toolbar)
        self.visible_checkbox.setEnabled(False)
        self.lock_checkbox.setEnabled(False)
        self.remove_button.setEnabled(False)
        canvas_col.addWidget(self.selection_toolbar_widget)

        body.addLayout(canvas_col)

        root.addLayout(body)

        self.scene.selectionChanged.connect(self.update_selection_toolbar)

        # Heroes and the initiative order can change from the Gameplay page while
        # this page is just sitting open (or mirrored on the TV) - there's no
        # cross-page event system in this app, so poll for live updates instead.
        self.live_timer = QTimer(self)
        self.live_timer.setInterval(1000)
        self.live_timer.timeout.connect(self.scene.update)
        self.live_timer.start()

        self.refresh()

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()
        self.view.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

    #
    # Refresh
    #

    def refresh(self):

        self.display = PlayerDisplayManager.load_display()

        self.scene.clear()
        self.backdrop_item = None
        self.background_item = None
        self.selected_item = None
        self.visible_checkbox.setEnabled(False)
        self.lock_checkbox.setEnabled(False)
        self.remove_button.setEnabled(False)

        self.redraw_backdrop()
        self.redraw_background()

        for widget_dict in self.display.widgets:

            if widget_dict.get("type") == "token":
                self.add_token_item(widget_dict)
            elif widget_dict.get("type") == "hero":
                self.add_hero_item(widget_dict)
            elif widget_dict.get("type") == "initiative":
                self.add_initiative_tracker_item(widget_dict)

        self.refresh_maps_list()
        self.refresh_widgets_list()

    def refresh_maps_list(self):

        while self.maps_container.count():

            item = self.maps_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        for map_obj in MapManager.load_maps():
            self.maps_container.addWidget(DisplayMapCard(map_obj, self.select_map))

        self.maps_container.addStretch()

    def refresh_widgets_list(self):

        while self.widgets_container.count():

            item = self.widgets_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.widgets_container.addWidget(
            InitiativePickerCard(self.add_initiative_tracker)
        )

        for hero in HeroManager.load_heroes():
            if not hero.is_dm:
                self.widgets_container.addWidget(HeroPickerCard(hero, self.add_hero))

        for token in TokenManager.load_tokens():
            self.widgets_container.addWidget(
                TokenPickerCard(token, self.add_token_from_library)
            )

        bottom_row = QHBoxLayout()

        add_token_button = QPushButton("Add Token")
        add_token_button.clicked.connect(self.go_to_library_tokens)
        bottom_row.addWidget(add_token_button)

        quick_add_button = QPushButton("+")
        quick_add_button.clicked.connect(self.quick_add_token)
        bottom_row.addWidget(quick_add_button)

        bottom_row_widget = QWidget()
        bottom_row_widget.setLayout(bottom_row)
        self.widgets_container.addWidget(bottom_row_widget)

        self.widgets_container.addStretch()

    #
    # Backdrop (locked, uneditable - sits behind everything, including the map)
    #

    def choose_backdrop(self):

        dest_folder = (
            CurrentCampaign.path() / "Images"
            if CurrentCampaign.loaded()
            else Path("library/portraits")
        )

        path = pick_and_copy_portrait(self, dest_folder)

        if not path:
            return

        self.display.backdrop_image = path
        PlayerDisplayManager.save_display(self.display)

        self.redraw_backdrop()

    def redraw_backdrop(self):

        if self.backdrop_item is not None:
            self.scene.removeItem(self.backdrop_item)
            self.backdrop_item = None

        if self.display.backdrop_image and Path(self.display.backdrop_image).exists():

            pixmap = QPixmap(self.display.backdrop_image).scaled(
                SCENE_WIDTH,
                SCENE_HEIGHT,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )

            item = QGraphicsPixmapItem(pixmap)
            item.setZValue(-2000)

            self.scene.addItem(item)
            self.backdrop_item = item

    #
    # Background
    #

    def select_map(self, map_obj):

        # Deliberately keep whatever position/size/rotation/lock is already set -
        # a new map steps into the same slot as the last one, so switching maps
        # mid-session doesn't require re-adjusting it every time.
        self.display.background_map = map_obj.path
        PlayerDisplayManager.save_display(self.display)

        self.redraw_background()

    def redraw_background(self):

        if self.background_item is not None:
            self.scene.removeItem(self.background_item)
            self.background_item = None

        if self.display.background_map and Path(self.display.background_map).exists():

            width = self.display.background_width or SCENE_WIDTH
            height = self.display.background_height or SCENE_HEIGHT

            item = MapBackgroundItem(
                self.display.background_map,
                self.display.background_x,
                self.display.background_y,
                width,
                height,
                self.display.background_rotation,
            )
            item.set_locked(self.display.background_locked)
            item.geometryChanged.connect(lambda: self.save_background_geometry(item))

            self.scene.addItem(item)
            self.background_item = item

    def save_background_geometry(self, item):

        geometry = item.geometry_dict()

        self.display.background_x = geometry["x"]
        self.display.background_y = geometry["y"]
        self.display.background_width = geometry["width"]
        self.display.background_height = geometry["height"]
        self.display.background_rotation = geometry["rotation"]

        PlayerDisplayManager.save_display(self.display)

    #
    # Tokens
    #

    def next_widget_id(self):

        existing = [w.get("widget_id", 0) for w in self.display.widgets]

        return (max(existing) + 1) if existing else 1

    def add_token_from_library(self, token):

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "token",
            "x": 100,
            "y": 100,
            "width": 150,
            "height": 150,
            "rotation": 0,
            "visible": True,
            "locked": False,
            "image_path": token.path,
        }

        self.display.widgets.append(widget_dict)
        PlayerDisplayManager.save_display(self.display)

        self.add_token_item(widget_dict)

    def quick_add_token(self):

        path = pick_and_copy_portrait(self, TokenManager.images_folder())

        if not path:
            return

        token = TokenManager.create_token(Path(path).stem, path)

        self.refresh_widgets_list()
        self.add_token_from_library(token)

    def go_to_library_tokens(self):

        if self.open_library_tokens:
            self.open_library_tokens()

    def add_token_item(self, widget_dict):

        item = TokenItem(
            widget_dict["widget_id"],
            widget_dict["image_path"],
            widget_dict["x"],
            widget_dict["y"],
            widget_dict["width"],
            widget_dict["height"],
            widget_dict["rotation"],
            widget_dict["visible"],
        )
        item.set_locked(widget_dict.get("locked", False))

        item.geometryChanged.connect(lambda: self.save_item_geometry(item))

        self.scene.addItem(item)

    #
    # Heroes
    #

    def add_hero(self, hero):

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "hero",
            "x": 100,
            "y": 100,
            "width": 160,
            "height": 200,
            "rotation": 0,
            "visible": True,
            "locked": False,
            "hero_name": hero.name,
        }

        self.display.widgets.append(widget_dict)
        PlayerDisplayManager.save_display(self.display)

        self.add_hero_item(widget_dict)

    def add_hero_item(self, widget_dict):

        item = HeroRingItem(
            widget_dict["widget_id"],
            widget_dict["hero_name"],
            widget_dict["x"],
            widget_dict["y"],
            widget_dict["width"],
            widget_dict["height"],
            widget_dict["rotation"],
            widget_dict.get("visible", True),
        )
        item.set_locked(widget_dict.get("locked", False))

        item.geometryChanged.connect(lambda: self.save_item_geometry(item))

        self.scene.addItem(item)

    #
    # Initiative tracker
    #

    def add_initiative_tracker(self):

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "initiative",
            "x": 100,
            "y": 100,
            "width": 100,
            "height": 60,
            "rotation": 0,
            "visible": True,
            "locked": False,
        }

        self.display.widgets.append(widget_dict)
        PlayerDisplayManager.save_display(self.display)

        self.add_initiative_tracker_item(widget_dict)

    def add_initiative_tracker_item(self, widget_dict):

        item = InitiativeTrackerItem(
            widget_dict["widget_id"],
            widget_dict["x"],
            widget_dict["y"],
            widget_dict["rotation"],
            widget_dict.get("visible", True),
        )
        item.set_locked(widget_dict.get("locked", False))

        item.geometryChanged.connect(lambda: self.save_item_geometry(item))

        self.scene.addItem(item)

    def save_item_geometry(self, item):

        for w in self.display.widgets:
            if w["widget_id"] == item.widget_id:
                w.update(item.geometry_dict())
                break

        PlayerDisplayManager.save_display(self.display)

    def update_widget_field(self, widget_id, **kwargs):

        for w in self.display.widgets:
            if w["widget_id"] == widget_id:
                w.update(kwargs)
                break

        PlayerDisplayManager.save_display(self.display)

    #
    # Selection toolbar
    #

    def update_selection_toolbar(self):

        selected = self.scene.selectedItems()
        item = selected[0] if selected else None

        if isinstance(item, (TokenItem, HeroRingItem, MapBackgroundItem, InitiativeTrackerItem)):

            self.selected_item = item

            has_visibility = hasattr(item, "visible_to_players")

            self.visible_checkbox.blockSignals(True)
            self.visible_checkbox.setChecked(
                item.visible_to_players if has_visibility else False
            )
            self.visible_checkbox.blockSignals(False)
            self.visible_checkbox.setEnabled(has_visibility)

            self.lock_checkbox.blockSignals(True)
            self.lock_checkbox.setChecked(item.locked)
            self.lock_checkbox.blockSignals(False)
            self.lock_checkbox.setEnabled(True)

            self.remove_button.setEnabled(True)

        else:
            self.selected_item = None
            self.visible_checkbox.setEnabled(False)
            self.lock_checkbox.setEnabled(False)
            self.remove_button.setEnabled(False)

    def toggle_visibility(self, checked):

        if self.selected_item is None:
            return

        if not hasattr(self.selected_item, "visible_to_players"):
            return

        self.selected_item.visible_to_players = checked
        self.selected_item.update()

        self.update_widget_field(self.selected_item.widget_id, visible=checked)

    def toggle_lock(self, checked):

        if self.selected_item is None:
            return

        self.selected_item.set_locked(checked)

        if isinstance(self.selected_item, MapBackgroundItem):
            self.display.background_locked = checked
            PlayerDisplayManager.save_display(self.display)
        else:
            self.update_widget_field(self.selected_item.widget_id, locked=checked)

    def remove_selected(self):

        if self.selected_item is None:
            return

        if isinstance(self.selected_item, MapBackgroundItem):

            self.display.background_map = ""
            PlayerDisplayManager.save_display(self.display)

            self.scene.removeItem(self.selected_item)
            self.background_item = None

        else:

            widget_id = self.selected_item.widget_id

            self.display.widgets = [
                w for w in self.display.widgets if w["widget_id"] != widget_id
            ]
            PlayerDisplayManager.save_display(self.display)

            self.scene.removeItem(self.selected_item)

        self.selected_item = None
        self.visible_checkbox.setEnabled(False)
        self.lock_checkbox.setEnabled(False)
        self.remove_button.setEnabled(False)

    #
    # TV window
    #

    def open_tv_display(self):

        if self.tv_window is not None and self.tv_window.isVisible():
            self.tv_window.raise_()
            self.tv_window.activateWindow()
            return

        self.tv_window = TVDisplayWindow(self.scene)
        self.tv_window.show()
