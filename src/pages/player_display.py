from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPixmap, QPen, QColor, QTransform
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QScrollArea,
    QStackedWidget,
    QButtonGroup,
    QGraphicsView,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QMessageBox,
)

from src.managers.token_manager import TokenManager
from src.managers.hero_manager import HeroManager
from src.managers.player_display_manager import PlayerDisplayManager
from src.database.current_campaign import CurrentCampaign
from src.database.session_state import SessionState
from src.widgets.portrait_picker import pick_and_copy_portrait
from src.widgets.primary_button import PrimaryButton
from src.widgets.sound_player import play_sound
from src.widgets.canvas_items import (
    DisplayScene,
    TokenItem,
    HeroRingItem,
    MapBackgroundItem,
    FogOverlayItem,
    InitiativeTrackerItem,
    MiniInitiativeTrackerItem,
    SCENE_WIDTH,
    SCENE_HEIGHT,
)
from src.widgets.tv_display_window import TVDisplayWindow


MAP_THUMB_WIDTH = 180
MAP_THUMB_HEIGHT = 115

TOKEN_THUMB_SIZE = 90
HERO_THUMB_SIZE = 90

TAB_BUTTON_STYLE = """
    QPushButton {
        background:#2b2b2b;
        color:white;
        border:2px solid #555;
        border-radius:6px;
        padding:6px;
    }

    QPushButton:checked {
        background:#3a2f18;
        border:2px solid #d4af37;
        font-weight:bold;
    }
"""


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


class MiniInitiativePickerCard(QFrame):

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

        title = QLabel("Mini Tracker")
        title.setStyleSheet("font-weight:bold; font-size:16px;")
        layout.addWidget(title)

        subtitle = QLabel("Current turn + next 2")
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
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # DM-only viewing convenience - rotates how this view renders the
        # scene (e.g. when the physical TV is mounted sideways relative to
        # where the DM is sitting). Purely a local transform on this one
        # QGraphicsView; the TV window is a separate QGraphicsView on the
        # same scene and is never touched by this.
        self.dm_rotation = 0

        # Fog of War interaction - None | "sizing" | "explore". While one of
        # these is active, mouse events are consumed here instead of being
        # handed to the scene's normal item selection/drag handling.
        self.fog_item = None
        self.fog_mode = None
        self.fog_reveal_callback = None
        self.fog_size_callback = None

        self._sizing_start = None
        self._sizing_preview = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_fit()

    def apply_fit(self):

        self.resetTransform()

        viewport_rect = self.viewport().rect()
        scene_rect = self.sceneRect()

        if scene_rect.width() <= 0 or scene_rect.height() <= 0:
            return

        if self.dm_rotation in (90, 270):

            # A 90/270 rotation swaps which scene axis maps to which viewport
            # axis, so stretching non-uniformly here (like the 0/180 case)
            # would visibly distort the picture. Scale uniformly instead -
            # letterboxed if the rotated content doesn't exactly match the
            # viewport's proportions - so rotating only reorients the view,
            # never stretches it.
            candidate_x = viewport_rect.height() / scene_rect.width()
            candidate_y = viewport_rect.width() / scene_rect.height()
            scale_x = scale_y = min(candidate_x, candidate_y)

        else:
            scale_x = viewport_rect.width() / scene_rect.width()
            scale_y = viewport_rect.height() / scene_rect.height()

        transform = QTransform()
        transform.rotate(self.dm_rotation)
        transform.scale(scale_x, scale_y)

        self.setTransform(transform)
        self.centerOn(scene_rect.center())

    def set_dm_rotation(self, degrees):

        self.dm_rotation = degrees % 360
        self.apply_fit()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete and self.delete_callback:
            self.delete_callback()
            event.accept()
            return

        super().keyPressEvent(event)

    def mousePressEvent(self, event):

        if self.fog_mode == "sizing" and self.fog_item is not None:

            self._sizing_start = self.mapToScene(event.pos())

            self._sizing_preview = QGraphicsRectItem()
            self._sizing_preview.setPen(QPen(QColor("#d4af37"), 2, Qt.DashLine))
            self._sizing_preview.setZValue(1000)
            self.scene().addItem(self._sizing_preview)

            event.accept()
            return

        if self.fog_mode == "explore" and self.fog_item is not None:

            local_pos = self.fog_item.mapFromScene(self.mapToScene(event.pos()))
            tile = self.fog_item.tile_at(local_pos)

            if tile is not None and self.fog_reveal_callback:
                self.fog_reveal_callback(tile)

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.fog_mode == "sizing" and self._sizing_start is not None:

            current = self.mapToScene(event.pos())
            rect = QRectF(self._sizing_start, current).normalized()

            if self._sizing_preview is not None:
                self._sizing_preview.setRect(rect)

            event.accept()
            return

        if self.fog_mode == "explore" and self.fog_item is not None:

            local_pos = self.fog_item.mapFromScene(self.mapToScene(event.pos()))
            tile = self.fog_item.tile_at(local_pos)

            if tile != self.fog_item.hover_tile:
                self.fog_item.hover_tile = tile
                self.fog_item.update()

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if self.fog_mode == "sizing" and self._sizing_start is not None:

            current = self.mapToScene(event.pos())
            rect = QRectF(self._sizing_start, current).normalized()

            if self._sizing_preview is not None:
                self.scene().removeItem(self._sizing_preview)
                self._sizing_preview = None

            self._sizing_start = None
            self.fog_mode = None

            if rect.width() >= 5 and rect.height() >= 5 and self.fog_size_callback:
                self.fog_size_callback(rect.width(), rect.height())

            event.accept()
            return

        super().mouseReleaseEvent(event)


class PlayerDisplayPage(QWidget):

    def __init__(self, open_library_tokens=None):
        super().__init__()

        self.open_library_tokens = open_library_tokens

        self.display = PlayerDisplayManager.load_display()
        self.scene = DisplayScene()
        self.backdrop_item = None
        self.background_item = None
        self.fog_item = None
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

        self.random_encounter_button = QPushButton("Random Encounter")
        self.random_encounter_button.clicked.connect(self.add_random_encounter)
        top_bar.addWidget(self.random_encounter_button)

        self.rotate_view_button = QPushButton("Rotate View (0°)")
        self.rotate_view_button.setToolTip(
            "Rotates only this screen's preview, in 90° steps - the TV Display is unaffected."
        )
        self.rotate_view_button.clicked.connect(self.rotate_dm_view)
        top_bar.addWidget(self.rotate_view_button)

        self.tv_button = PrimaryButton("TV Display")
        self.tv_button.clicked.connect(self.open_tv_display)
        top_bar.addWidget(self.tv_button)

        root.addLayout(top_bar)

        #
        # Body: left tabs + canvas
        #

        body = QHBoxLayout()

        left = QVBoxLayout()

        tabs_container = QWidget()
        tabs_container.setFixedWidth(270)

        tabs_container_layout = QVBoxLayout(tabs_container)
        tabs_container_layout.setContentsMargins(0, 0, 0, 0)

        tab_button_grid = QGridLayout()
        tab_button_grid.setSpacing(4)
        tabs_container_layout.addLayout(tab_button_grid)

        self.tab_stack = QStackedWidget()
        tabs_container_layout.addWidget(self.tab_stack)

        self.tab_button_group = QButtonGroup(self)
        self.tab_button_group.setExclusive(True)

        def add_tab(widget, label, row, col):

            self.tab_stack.addWidget(widget)

            button = QPushButton(label)
            button.setCheckable(True)
            button.setStyleSheet(TAB_BUTTON_STYLE)
            button.clicked.connect(lambda checked=False, w=widget: self.tab_stack.setCurrentWidget(w))

            self.tab_button_group.addButton(button)
            tab_button_grid.addWidget(button, row, col)

            return button

        maps_tab = QWidget()
        maps_tab_layout = QVBoxLayout(maps_tab)

        self.maps_container = QVBoxLayout()

        maps_inner = QWidget()
        maps_inner.setLayout(self.maps_container)

        maps_scroll = QScrollArea()
        maps_scroll.setWidgetResizable(True)
        maps_scroll.setWidget(maps_inner)

        maps_tab_layout.addWidget(maps_scroll)

        maps_button = add_tab(maps_tab, "Maps", 0, 0)

        widgets_tab = QWidget()
        widgets_tab_layout = QVBoxLayout(widgets_tab)

        self.widgets_container = QVBoxLayout()

        widgets_inner = QWidget()
        widgets_inner.setLayout(self.widgets_container)

        widgets_scroll = QScrollArea()
        widgets_scroll.setWidgetResizable(True)
        widgets_scroll.setWidget(widgets_inner)

        widgets_tab_layout.addWidget(widgets_scroll)

        add_tab(widgets_tab, "Widgets", 1, 0)

        fog_tab = QWidget()
        fog_tab_layout = QVBoxLayout(fog_tab)

        self.fog_hide_all_button = QPushButton("Hide All")
        self.fog_hide_all_button.clicked.connect(self.fog_hide_all)
        fog_tab_layout.addWidget(self.fog_hide_all_button)

        self.fog_clear_button = QPushButton("Clear Fog")
        self.fog_clear_button.clicked.connect(self.fog_clear)
        fog_tab_layout.addWidget(self.fog_clear_button)

        self.fog_set_grid_button = QPushButton("Set Grid Size")
        self.fog_set_grid_button.clicked.connect(self.fog_start_set_grid)
        fog_tab_layout.addWidget(self.fog_set_grid_button)

        self.fog_explore_button = QPushButton("Explore")
        self.fog_explore_button.setCheckable(True)
        self.fog_explore_button.toggled.connect(self.fog_toggle_explore)
        fog_tab_layout.addWidget(self.fog_explore_button)

        fog_form = QFormLayout()

        self.fog_size_spinbox = QDoubleSpinBox()
        self.fog_size_spinbox.setRange(5, 2000)
        self.fog_size_spinbox.setSingleStep(5)
        self.fog_size_spinbox.setValue(100)
        self.fog_size_spinbox.valueChanged.connect(self.fog_size_changed)
        fog_form.addRow("Tile Size", self.fog_size_spinbox)

        self.fog_offset_x_spinbox = QDoubleSpinBox()
        self.fog_offset_x_spinbox.setRange(-1000, 1000)
        self.fog_offset_x_spinbox.setSingleStep(1)
        self.fog_offset_x_spinbox.valueChanged.connect(self.fog_offset_changed)
        fog_form.addRow("Offset X", self.fog_offset_x_spinbox)

        self.fog_offset_y_spinbox = QDoubleSpinBox()
        self.fog_offset_y_spinbox.setRange(-1000, 1000)
        self.fog_offset_y_spinbox.setSingleStep(1)
        self.fog_offset_y_spinbox.valueChanged.connect(self.fog_offset_changed)
        fog_form.addRow("Offset Y", self.fog_offset_y_spinbox)

        fog_tab_layout.addLayout(fog_form)

        fog_hint = QLabel(
            "Set Grid Size: drag a box on the map to size one tile,\n"
            "or dial in the exact size and nudge the grid below.\n"
            "Explore: click tiles to reveal them to players."
        )
        fog_hint.setWordWrap(True)
        fog_hint.setStyleSheet("color:#999;")
        fog_tab_layout.addWidget(fog_hint)

        fog_tab_layout.addStretch()

        add_tab(fog_tab, "FOG", 0, 1)

        sounds_tab = QWidget()
        sounds_tab_layout = QVBoxLayout(sounds_tab)

        self.sounds_container = QVBoxLayout()

        sounds_inner = QWidget()
        sounds_inner.setLayout(self.sounds_container)

        sounds_scroll = QScrollArea()
        sounds_scroll.setWidgetResizable(True)
        sounds_scroll.setWidget(sounds_inner)

        sounds_tab_layout.addWidget(sounds_scroll)

        add_tab(sounds_tab, "Sounds", 1, 1)

        maps_button.setChecked(True)
        self.tab_stack.setCurrentWidget(maps_tab)

        left.addWidget(tabs_container)

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

        self.aspect_lock_checkbox = QCheckBox("Lock Ratio")
        self.aspect_lock_checkbox.setToolTip(
            "Snaps the map to the ratio on the right and keeps it locked "
            "while resizing, so it always lines up cleanly with a square grid."
        )
        self.aspect_lock_checkbox.toggled.connect(self.toggle_aspect_lock)
        self.selection_toolbar.addWidget(self.aspect_lock_checkbox)

        self.ratio_x_spinbox = QSpinBox()
        self.ratio_x_spinbox.setRange(1, 100)
        self.ratio_x_spinbox.setValue(4)
        self.ratio_x_spinbox.valueChanged.connect(self.ratio_value_changed)
        self.selection_toolbar.addWidget(self.ratio_x_spinbox)

        self.selection_toolbar.addWidget(QLabel(":"))

        self.ratio_y_spinbox = QSpinBox()
        self.ratio_y_spinbox.setRange(1, 100)
        self.ratio_y_spinbox.setValue(3)
        self.ratio_y_spinbox.valueChanged.connect(self.ratio_value_changed)
        self.selection_toolbar.addWidget(self.ratio_y_spinbox)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        self.selection_toolbar.addWidget(self.remove_button)

        self.selection_toolbar.addStretch()

        self.selection_toolbar_widget = QWidget()
        self.selection_toolbar_widget.setLayout(self.selection_toolbar)
        self.visible_checkbox.setEnabled(False)
        self.lock_checkbox.setEnabled(False)
        self.aspect_lock_checkbox.setEnabled(False)
        self.ratio_x_spinbox.setEnabled(False)
        self.ratio_y_spinbox.setEnabled(False)
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
        self.view.apply_fit()

    #
    # Refresh
    #

    def refresh(self):

        self.display = PlayerDisplayManager.load_display()

        self.scene.clear()
        self.backdrop_item = None
        self.background_item = None
        self.fog_item = None
        self.selected_item = None
        self.visible_checkbox.setEnabled(False)
        self.lock_checkbox.setEnabled(False)
        self.aspect_lock_checkbox.setEnabled(False)
        self.ratio_x_spinbox.setEnabled(False)
        self.ratio_y_spinbox.setEnabled(False)
        self.remove_button.setEnabled(False)

        self.view.fog_item = None
        self.view.fog_mode = None
        self.view.fog_reveal_callback = None
        self.view.fog_size_callback = None

        self.redraw_backdrop()
        self.redraw_background()

        for widget_dict in self.display.widgets:

            if widget_dict.get("type") == "token":
                self.add_token_item(widget_dict)
            elif widget_dict.get("type") == "hero":
                self.add_hero_item(widget_dict)
            elif widget_dict.get("type") == "initiative":
                self.add_initiative_tracker_item(widget_dict)
            elif widget_dict.get("type") == "mini_initiative":
                self.add_mini_initiative_tracker_item(widget_dict)

        self.refresh_maps_list()
        self.refresh_widgets_list()
        self.refresh_fog_tab()
        self.refresh_sounds_tab()

    def refresh_maps_list(self):

        while self.maps_container.count():

            item = self.maps_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        for map_obj in SessionState.scene_maps():
            self.maps_container.addWidget(DisplayMapCard(map_obj, self.select_map))

        self.maps_container.addStretch()

    def refresh_sounds_tab(self):

        while self.sounds_container.count():

            item = self.sounds_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        for sound in SessionState.session_sounds():

            button = QPushButton(sound.name)
            button.clicked.connect(lambda checked=False, path=sound.path: play_sound(path))

            self.sounds_container.addWidget(button)

        self.sounds_container.addStretch()

    def refresh_widgets_list(self):

        while self.widgets_container.count():

            item = self.widgets_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        self.widgets_container.addWidget(
            InitiativePickerCard(self.add_initiative_tracker)
        )

        self.widgets_container.addWidget(
            MiniInitiativePickerCard(self.add_mini_initiative_tracker)
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

        # Fog is defined in this map's own pixel space, so it can't carry over
        # to a different map - a freshly-selected map starts unexplored.
        self.display.fog_enabled = False
        self.display.fog_grid_width = 0
        self.display.fog_grid_height = 0
        self.display.fog_offset_x = 0
        self.display.fog_offset_y = 0
        self.display.fog_revealed = []

        PlayerDisplayManager.save_display(self.display)

        self.redraw_background()
        self.refresh_fog_tab()

    def redraw_background(self):

        if self.background_item is not None:
            self.scene.removeItem(self.background_item)
            self.background_item = None

        if self.fog_item is not None:
            self.scene.removeItem(self.fog_item)
            self.fog_item = None
            self.view.fog_item = None

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
            item.locked_aspect_ratio = (
                self.display.background_ratio_x / self.display.background_ratio_y
                if self.display.background_aspect_locked else None
            )
            item.geometryChanged.connect(lambda: self.save_background_geometry(item))

            self.scene.addItem(item)
            self.background_item = item

            fog_item = FogOverlayItem()
            fog_item.sync_to(item)
            fog_item.fog_enabled = self.display.fog_enabled
            fog_item.grid_width = self.display.fog_grid_width
            fog_item.grid_height = self.display.fog_grid_height
            fog_item.offset_x = self.display.fog_offset_x
            fog_item.offset_y = self.display.fog_offset_y
            fog_item.revealed = {tuple(pair) for pair in self.display.fog_revealed}

            self.scene.addItem(fog_item)
            self.fog_item = fog_item
            self.view.fog_item = fog_item

    def save_background_geometry(self, item):

        geometry = item.geometry_dict()

        self.display.background_x = geometry["x"]
        self.display.background_y = geometry["y"]
        self.display.background_width = geometry["width"]
        self.display.background_height = geometry["height"]
        self.display.background_rotation = geometry["rotation"]

        PlayerDisplayManager.save_display(self.display)

        if self.fog_item is not None:
            self.fog_item.sync_to(item)

    #
    # Fog of War
    #

    def refresh_fog_tab(self):

        has_map = bool(self.display.background_map)

        self.fog_hide_all_button.setEnabled(has_map)
        self.fog_clear_button.setEnabled(has_map)
        self.fog_set_grid_button.setEnabled(has_map)
        self.fog_size_spinbox.setEnabled(has_map)
        self.fog_offset_x_spinbox.setEnabled(has_map)
        self.fog_offset_y_spinbox.setEnabled(has_map)

        self.fog_explore_button.blockSignals(True)
        self.fog_explore_button.setChecked(False)
        self.fog_explore_button.blockSignals(False)
        self.fog_explore_button.setEnabled(has_map)

        self.view.fog_mode = None
        self.view.fog_reveal_callback = None
        self.view.fog_size_callback = None

        self.sync_fog_controls()

    def sync_fog_controls(self):

        self.fog_size_spinbox.blockSignals(True)
        self.fog_size_spinbox.setValue(self.display.fog_grid_width or 100)
        self.fog_size_spinbox.blockSignals(False)

        self.fog_offset_x_spinbox.blockSignals(True)
        self.fog_offset_x_spinbox.setValue(self.display.fog_offset_x)
        self.fog_offset_x_spinbox.blockSignals(False)

        self.fog_offset_y_spinbox.blockSignals(True)
        self.fog_offset_y_spinbox.setValue(self.display.fog_offset_y)
        self.fog_offset_y_spinbox.blockSignals(False)

    def fog_hide_all(self):

        if not self.display.background_map or self.fog_item is None:
            return

        self.display.fog_enabled = True
        self.display.fog_revealed = []
        PlayerDisplayManager.save_display(self.display)

        self.fog_item.fog_enabled = True
        self.fog_item.revealed = set()
        self.fog_item.update()

    def fog_clear(self):

        if not self.display.background_map or self.fog_item is None:
            return

        self.display.fog_enabled = False
        PlayerDisplayManager.save_display(self.display)

        self.fog_item.fog_enabled = False
        self.fog_item.update()

    def fog_start_set_grid(self):

        if not self.display.background_map or self.fog_item is None:
            return

        self.fog_explore_button.setChecked(False)

        self.view.fog_mode = "sizing"
        self.view.fog_size_callback = self.fog_set_grid_size

    def fog_set_grid_size(self, width, height):

        self.display.fog_grid_width = width
        self.display.fog_grid_height = height
        self.display.fog_offset_x = 0
        self.display.fog_offset_y = 0
        PlayerDisplayManager.save_display(self.display)

        if self.fog_item is not None:
            self.fog_item.grid_width = width
            self.fog_item.grid_height = height
            self.fog_item.offset_x = 0
            self.fog_item.offset_y = 0
            self.fog_item.update()

        self.sync_fog_controls()

    def fog_size_changed(self, value):

        if not self.display.background_map or self.fog_item is None:
            return

        self.display.fog_grid_width = value
        self.display.fog_grid_height = value
        PlayerDisplayManager.save_display(self.display)

        self.fog_item.grid_width = value
        self.fog_item.grid_height = value
        self.fog_item.update()

    def fog_offset_changed(self, _value):

        if not self.display.background_map or self.fog_item is None:
            return

        self.display.fog_offset_x = self.fog_offset_x_spinbox.value()
        self.display.fog_offset_y = self.fog_offset_y_spinbox.value()
        PlayerDisplayManager.save_display(self.display)

        self.fog_item.offset_x = self.display.fog_offset_x
        self.fog_item.offset_y = self.display.fog_offset_y
        self.fog_item.update()

    def fog_toggle_explore(self, checked):

        if checked and (not self.display.background_map or self.fog_item is None):
            self.fog_explore_button.blockSignals(True)
            self.fog_explore_button.setChecked(False)
            self.fog_explore_button.blockSignals(False)
            return

        self.view.fog_mode = "explore" if checked else None
        self.view.fog_reveal_callback = self.fog_reveal_tile if checked else None

        if self.fog_item is not None:
            self.fog_item.hover_tile = None
            self.fog_item.update()

    def fog_reveal_tile(self, tile):

        tile_key = list(tile)

        if tile_key not in self.display.fog_revealed:
            self.display.fog_revealed.append(tile_key)
            PlayerDisplayManager.save_display(self.display)

        if self.fog_item is not None:
            self.fog_item.revealed.add(tile)
            self.fog_item.update()

    #
    # Tokens
    #

    def next_widget_id(self):

        existing = [w.get("widget_id", 0) for w in self.display.widgets]

        return (max(existing) + 1) if existing else 1

    def last_size_for_type(self, widget_type, fallback_width, fallback_height):

        matches = [w for w in self.display.widgets if w.get("type") == widget_type]

        if not matches:
            return fallback_width, fallback_height

        last = matches[-1]

        return last.get("width", fallback_width), last.get("height", fallback_height)

    def add_token_from_library(self, token):

        width, height = self.last_size_for_type("token", 150, 150)

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "token",
            "x": 100,
            "y": 100,
            "width": width,
            "height": height,
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

        width, height = self.last_size_for_type("hero", 160, 200)

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "hero",
            "x": 100,
            "y": 100,
            "width": width,
            "height": height,
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
    # Random encounter monsters
    #

    def add_random_encounter(self):

        instance = SessionState.add_random_encounter()

        if instance is None:
            QMessageBox.information(
                self,
                "No Random Encounters in Session",
                "Tick 'Random Encounter' on a monster in the session pool "
                "(Session tab) first."
            )
        else:
            play_sound(instance.sound)

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

    def add_mini_initiative_tracker(self):

        widget_dict = {
            "widget_id": self.next_widget_id(),
            "type": "mini_initiative",
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

        self.add_mini_initiative_tracker_item(widget_dict)

    def add_mini_initiative_tracker_item(self, widget_dict):

        item = MiniInitiativeTrackerItem(
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

        if isinstance(item, (TokenItem, HeroRingItem, MapBackgroundItem, InitiativeTrackerItem, MiniInitiativeTrackerItem)):

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

            is_background = isinstance(item, MapBackgroundItem)

            self.aspect_lock_checkbox.blockSignals(True)
            self.aspect_lock_checkbox.setChecked(bool(item.locked_aspect_ratio) if is_background else False)
            self.aspect_lock_checkbox.blockSignals(False)
            self.aspect_lock_checkbox.setEnabled(is_background)

            self.ratio_x_spinbox.blockSignals(True)
            self.ratio_y_spinbox.blockSignals(True)
            self.ratio_x_spinbox.setValue(int(self.display.background_ratio_x) if is_background else 4)
            self.ratio_y_spinbox.setValue(int(self.display.background_ratio_y) if is_background else 3)
            self.ratio_x_spinbox.blockSignals(False)
            self.ratio_y_spinbox.blockSignals(False)
            self.ratio_x_spinbox.setEnabled(is_background)
            self.ratio_y_spinbox.setEnabled(is_background)

            self.remove_button.setEnabled(True)

        else:
            self.selected_item = None
            self.visible_checkbox.setEnabled(False)
            self.lock_checkbox.setEnabled(False)
            self.aspect_lock_checkbox.setEnabled(False)
            self.ratio_x_spinbox.setEnabled(False)
            self.ratio_y_spinbox.setEnabled(False)
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

    def toggle_aspect_lock(self, checked):

        if not isinstance(self.selected_item, MapBackgroundItem):
            return

        self.display.background_aspect_locked = checked

        if checked:
            ratio = self.ratio_x_spinbox.value() / self.ratio_y_spinbox.value()
            self.selected_item.snap_to_aspect_ratio(ratio)
        else:
            self.selected_item.locked_aspect_ratio = None

        self.save_background_geometry(self.selected_item)

    def ratio_value_changed(self):

        self.display.background_ratio_x = self.ratio_x_spinbox.value()
        self.display.background_ratio_y = self.ratio_y_spinbox.value()

        if isinstance(self.selected_item, MapBackgroundItem) and self.aspect_lock_checkbox.isChecked():

            ratio = self.ratio_x_spinbox.value() / self.ratio_y_spinbox.value()
            self.selected_item.snap_to_aspect_ratio(ratio)
            self.save_background_geometry(self.selected_item)
        else:
            PlayerDisplayManager.save_display(self.display)

    def remove_selected(self):

        if self.selected_item is None:
            return

        if isinstance(self.selected_item, MapBackgroundItem):

            self.display.background_map = ""
            self.display.fog_enabled = False
            self.display.fog_grid_width = 0
            self.display.fog_grid_height = 0
            self.display.fog_offset_x = 0
            self.display.fog_offset_y = 0
            self.display.fog_revealed = []
            PlayerDisplayManager.save_display(self.display)

            self.scene.removeItem(self.selected_item)
            self.background_item = None

            if self.fog_item is not None:
                self.scene.removeItem(self.fog_item)
                self.fog_item = None
                self.view.fog_item = None

            self.refresh_fog_tab()

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
        self.aspect_lock_checkbox.setEnabled(False)
        self.ratio_x_spinbox.setEnabled(False)
        self.ratio_y_spinbox.setEnabled(False)
        self.remove_button.setEnabled(False)

    #
    # DM view rotation (this screen only - never the TV window)
    #

    def rotate_dm_view(self):

        new_rotation = (self.view.dm_rotation + 90) % 360
        self.view.set_dm_rotation(new_rotation)
        self.rotate_view_button.setText(f"Rotate View ({new_rotation}°)")

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
