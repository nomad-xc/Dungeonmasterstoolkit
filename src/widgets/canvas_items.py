import math
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPen, QPixmap, QPainterPath, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QGraphicsObject, QGraphicsScene

from src.managers.hero_manager import HeroManager
from src.database.session_state import SessionState
from src.pages.gameplay import hp_ratio_rgb


HANDLE_SIZE = 10
ROTATE_HANDLE_OFFSET = 24
MIN_SIZE = 20

SCENE_WIDTH = 1600
SCENE_HEIGHT = 900


class DisplayScene(QGraphicsScene):

    def __init__(self):
        super().__init__()

        self.tv_viewport = None

        self.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)


class ResizableRotatableItem(QGraphicsObject):

    geometryChanged = Signal()

    def __init__(self, widget_id, x, y, width, height, rotation=0):
        super().__init__()

        self.widget_id = widget_id

        self._width = width
        self._height = height

        self._active_handle = None
        self.locked = False
        self.locked_aspect_ratio = None

        self.setPos(x, y)
        self.setRotation(rotation)
        self.setTransformOriginPoint(width / 2, height / 2)

        self.setFlag(QGraphicsObject.ItemIsMovable)
        self.setFlag(QGraphicsObject.ItemIsSelectable)
        self.setFlag(QGraphicsObject.ItemSendsGeometryChanges)

    def set_locked(self, locked):

        self.locked = locked
        self.setFlag(QGraphicsObject.ItemIsMovable, not locked)
        self.update()

    def snap_to_aspect_ratio(self, ratio):

        self.prepareGeometryChange()

        self._height = max(MIN_SIZE, self._width / ratio)
        self.setTransformOriginPoint(self._width / 2, self._height / 2)

        self.locked_aspect_ratio = ratio
        self.update()

    def width(self):
        return self._width

    def height(self):
        return self._height

    def geometry_dict(self):

        return {
            "x": self.pos().x(),
            "y": self.pos().y(),
            "width": self._width,
            "height": self._height,
            "rotation": self.rotation(),
        }

    def handles(self):

        return {
            "resize": QRectF(
                self._width - HANDLE_SIZE, self._height - HANDLE_SIZE,
                HANDLE_SIZE * 2, HANDLE_SIZE * 2
            ),
            "rotate": QRectF(
                self._width / 2 - HANDLE_SIZE,
                -ROTATE_HANDLE_OFFSET - HANDLE_SIZE,
                HANDLE_SIZE * 2, HANDLE_SIZE * 2
            ),
        }

    def boundingRect(self):

        margin = HANDLE_SIZE

        return QRectF(
            -margin,
            -ROTATE_HANDLE_OFFSET - margin,
            self._width + margin * 2,
            self._height + ROTATE_HANDLE_OFFSET + margin * 2
        )

    def paint(self, painter, option, widget=None):

        self.paint_content(painter, option, widget)

        if self.isSelected():

            outline_color = QColor("#888") if self.locked else QColor("#d4af37")

            painter.setPen(QPen(outline_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(QRectF(0, 0, self._width, self._height))

            if not self.locked:

                painter.setBrush(QColor("#d4af37"))
                painter.setPen(Qt.NoPen)

                for rect in self.handles().values():
                    painter.drawEllipse(rect)

    def paint_content(self, painter, option, widget=None):
        pass

    def mousePressEvent(self, event):

        pos = event.pos()

        if self.isSelected() and not self.locked:
            for name, rect in self.handles().items():
                if rect.contains(pos):
                    self._active_handle = name
                    # Without an explicit grab, dragging the mouse outside the
                    # view (easy to do when rotating something near the edge
                    # of the screen) can lose the release event entirely,
                    # leaving the gesture never finalized/saved.
                    self.grabMouse()
                    event.accept()
                    return

        self._active_handle = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self._active_handle == "resize":

            local = event.pos()

            self.prepareGeometryChange()
            self._width = max(MIN_SIZE, local.x())

            if self.locked_aspect_ratio:
                self._height = max(MIN_SIZE, self._width / self.locked_aspect_ratio)
            else:
                self._height = max(MIN_SIZE, local.y())

            self.setTransformOriginPoint(self._width / 2, self._height / 2)
            self.update()

        elif self._active_handle == "rotate":

            center = self.mapToScene(self._width / 2, self._height / 2)
            v = event.scenePos() - center

            angle = math.degrees(math.atan2(v.y(), v.x())) + 90
            self.setRotation(angle)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if self._active_handle is not None:
            self.ungrabMouse()

        self._active_handle = None

        super().mouseReleaseEvent(event)

        self.geometryChanged.emit()


class TokenItem(ResizableRotatableItem):

    def __init__(self, widget_id, image_path, x, y, width, height, rotation, visible_to_players):
        super().__init__(widget_id, x, y, width, height, rotation)

        self.image_path = image_path
        self.visible_to_players = visible_to_players

        self._pixmap = None

        if image_path and Path(image_path).exists():
            self._pixmap = QPixmap(image_path)

    def paint_content(self, painter, option, widget=None):

        is_tv_view = self.scene() is not None and widget is self.scene().tv_viewport

        if is_tv_view and not self.visible_to_players:
            return

        rect = QRectF(0, 0, self._width, self._height)

        if self._pixmap and not self._pixmap.isNull():
            painter.drawPixmap(rect, self._pixmap, QRectF(self._pixmap.rect()))
        else:
            painter.fillRect(rect, QColor("#555"))

        if not is_tv_view and not self.visible_to_players:
            painter.fillRect(rect, QColor(0, 0, 0, 120))


class MapBackgroundItem(ResizableRotatableItem):

    def __init__(self, image_path, x, y, width, height, rotation):
        super().__init__("background", x, y, width, height, rotation)

        self.image_path = image_path

        self._pixmap = None

        if image_path and Path(image_path).exists():
            self._pixmap = QPixmap(image_path)

        self.setZValue(-1000)

    def paint_content(self, painter, option, widget=None):

        rect = QRectF(0, 0, self._width, self._height)

        if self._pixmap and not self._pixmap.isNull():
            painter.drawPixmap(rect, self._pixmap, QRectF(self._pixmap.rect()))
        else:
            painter.fillRect(rect, QColor("#333"))


FOG_DM_COLOR = QColor(40, 40, 40, 170)
FOG_TV_COLOR = QColor(0, 0, 0, 255)
FOG_GRID_LINE_COLOR = QColor(255, 255, 255, 90)
FOG_HOVER_COLOR = QColor(212, 175, 55, 110)


class FogOverlayItem(QGraphicsObject):

    # Always kept pixel-aligned with a MapBackgroundItem via sync_to() - not a
    # ResizableRotatableItem itself, it has no handles of its own and is purely
    # a rendering + hit-testing layer driven by the view's fog interaction modes.

    def __init__(self):
        super().__init__()

        self._width = 0
        self._height = 0

        self.fog_enabled = False
        self.grid_width = 0
        self.grid_height = 0
        self.offset_x = 0
        self.offset_y = 0
        self.revealed = set()
        self.hover_tile = None

        self.setZValue(-999)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(False)

    def sync_to(self, background_item):

        self.prepareGeometryChange()

        self.setPos(background_item.pos())
        self.setRotation(background_item.rotation())

        self._width = background_item.width()
        self._height = background_item.height()
        self.setTransformOriginPoint(self._width / 2, self._height / 2)

        self.update()

    def tile_size(self):

        width = self.grid_width if self.grid_width > 0 else self._width
        height = self.grid_height if self.grid_height > 0 else self._height

        return max(width, 1), max(height, 1)

    def tile_origin(self):

        tile_w, tile_h = self.tile_size()

        return self.offset_x % tile_w, self.offset_y % tile_h

    def tile_range(self):

        # col/row 0 sits at (x0, y0); a positive offset can leave a partial
        # leading tile before that, hence the -1 start when x0/y0 > 0.

        tile_w, tile_h = self.tile_size()
        x0, y0 = self.tile_origin()

        col_start = -1 if x0 > 0 else 0
        row_start = -1 if y0 > 0 else 0

        col_end = max(col_start, math.ceil((self._width - x0) / tile_w) - 1)
        row_end = max(row_start, math.ceil((self._height - y0) / tile_h) - 1)

        return col_start, col_end, row_start, row_end

    def tile_rect(self, col, row):

        tile_w, tile_h = self.tile_size()
        x0, y0 = self.tile_origin()

        rect = QRectF(x0 + col * tile_w, y0 + row * tile_h, tile_w, tile_h)

        return rect.intersected(QRectF(0, 0, self._width, self._height))

    def tile_at(self, local_pos):

        if not (0 <= local_pos.x() <= self._width and 0 <= local_pos.y() <= self._height):
            return None

        tile_w, tile_h = self.tile_size()
        x0, y0 = self.tile_origin()

        col = math.floor((local_pos.x() - x0) / tile_w)
        row = math.floor((local_pos.y() - y0) / tile_h)

        return (col, row)

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget=None):

        if not self.fog_enabled or self._width <= 0 or self._height <= 0:
            return

        is_tv_view = self.scene() is not None and widget is self.scene().tv_viewport

        tile_w, tile_h = self.tile_size()
        x0, y0 = self.tile_origin()
        col_start, col_end, row_start, row_end = self.tile_range()

        painter.setPen(Qt.NoPen)

        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):

                if (col, row) in self.revealed:
                    continue

                tile_rect = self.tile_rect(col, row)

                if tile_rect.isEmpty():
                    continue

                painter.setBrush(FOG_TV_COLOR if is_tv_view else FOG_DM_COLOR)
                painter.drawRect(tile_rect)

        if is_tv_view:
            return

        painter.setPen(QPen(FOG_GRID_LINE_COLOR, 1))
        painter.setBrush(Qt.NoBrush)

        for col in range(col_start, col_end + 2):
            x = x0 + col * tile_w
            if 0 < x < self._width:
                painter.drawLine(QPointF(x, 0), QPointF(x, self._height))

        for row in range(row_start, row_end + 2):
            y = y0 + row * tile_h
            if 0 < y < self._height:
                painter.drawLine(QPointF(0, y), QPointF(self._width, y))

        if self.hover_tile is not None:

            hover_rect = self.tile_rect(*self.hover_tile)

            if not hover_rect.isEmpty():
                painter.setPen(QPen(QColor("#d4af37"), 2))
                painter.setBrush(FOG_HOVER_COLOR)
                painter.drawRect(hover_rect)


RING_WIDTH = 10
RING_TRACK_COLOR = QColor(255, 255, 255, 60)
MP_COLOR = QColor("#3b82f6")


class HeroRingItem(ResizableRotatableItem):

    def __init__(self, widget_id, hero_name, x, y, width, height, rotation, visible_to_players=True):
        super().__init__(widget_id, x, y, width, height, rotation)

        self.hero_name = hero_name
        self.visible_to_players = visible_to_players

    def find_hero(self):

        for hero in HeroManager.load_heroes():
            if hero.name == self.hero_name:
                return hero

        return None

    def paint_content(self, painter, option, widget=None):

        is_tv_view = self.scene() is not None and widget is self.scene().tv_viewport

        if is_tv_view and not self.visible_to_players:
            return

        hero = self.find_hero()

        ring_area = min(self._width, self._height)
        inset = RING_WIDTH
        portrait_rect = QRectF(
            (self._width - ring_area) / 2 + inset,
            (self._height - ring_area) / 2 + inset,
            ring_area - inset * 2,
            ring_area - inset * 2
        )

        painter.setRenderHint(QPainter.Antialiasing)

        painter.save()
        clip_path = QPainterPath()
        clip_path.addEllipse(portrait_rect)
        painter.setClipPath(clip_path)

        if hero and hero.portrait and Path(hero.portrait).exists():
            pixmap = QPixmap(hero.portrait)
            painter.drawPixmap(portrait_rect, pixmap, QRectF(pixmap.rect()))
        else:
            painter.fillRect(portrait_rect, QColor("#2b2b2b"))

        painter.restore()

        hp_ratio = (hero.hp / hero.max_hp) if hero and hero.max_hp else 0
        mp_ratio = (hero.mp / hero.max_mp) if hero and hero.max_mp else 0

        painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(RING_TRACK_COLOR, RING_WIDTH, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(portrait_rect, 270 * 16, -180 * 16)
        painter.drawArc(portrait_rect, 270 * 16, 180 * 16)

        if hero:
            r, g, b = hp_ratio_rgb(hp_ratio)
            hp_color = QColor(r, g, b)
        else:
            hp_color = QColor("#555")

        painter.setPen(QPen(hp_color, RING_WIDTH, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(portrait_rect, 270 * 16, int(-180 * hp_ratio * 16))

        painter.setPen(QPen(MP_COLOR, RING_WIDTH, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(portrait_rect, 270 * 16, int(180 * mp_ratio * 16))

        painter.setPen(QPen(QColor("white")))
        font = QFont()
        font.setBold(True)
        painter.setFont(font)
        name_rect = QRectF(0, portrait_rect.bottom(), self._width, self._height - portrait_rect.bottom())
        painter.drawText(name_rect, Qt.AlignHCenter | Qt.AlignTop, hero.name if hero else self.hero_name)

        if not is_tv_view and not self.visible_to_players:
            painter.fillRect(QRectF(0, 0, self._width, self._height), QColor(0, 0, 0, 120))


PILL_WIDTH = 100
PILL_HEIGHT = 28
PILL_SPACING = 8

# Each pill is sized to fit its own text, not a fixed box - these are just
# the breathing room kept around that text (tight, since this is meant to
# still read clearly from across a room on a big TV).
PILL_H_PADDING = 32
PILL_V_PADDING = 6
PILL_MIN_WIDTH = 46
PILL_MIN_HEIGHT = 26


class BaseInitiativeTrackerItem(ResizableRotatableItem):

    # None shows the whole turn order; otherwise shows at most this many
    # entries, starting from whoever's turn it currently is.
    max_entries = None

    def __init__(self, widget_id, x, y, rotation=0, visible_to_players=True):
        super().__init__(widget_id, x, y, PILL_WIDTH, PILL_HEIGHT, rotation)

        self.visible_to_players = visible_to_players

    def handles(self):

        all_handles = super().handles()

        return {"rotate": all_handles["rotate"]}

    def visible_entries(self, order, current):

        if self.max_entries is None or not order:
            return order

        start = next((i for i, entry in enumerate(order) if entry is current), 0)
        count = min(self.max_entries, len(order))

        return [order[(start + i) % len(order)] for i in range(count)]

    def paint_content(self, painter, option, widget=None):

        is_tv_view = self.scene() is not None and widget is self.scene().tv_viewport

        if is_tv_view and not self.visible_to_players:
            return

        order = self.visible_entries(SessionState.initiative_order(), SessionState.current_turn())
        current = SessionState.current_turn()

        font = QFont()
        font.setBold(True)
        painter.setFont(font)

        if not order:

            new_width = PILL_WIDTH
            new_height = PILL_HEIGHT

            if new_width != self._width or new_height != self._height:
                self.prepareGeometryChange()
                self._width = new_width
                self._height = new_height
                self.setTransformOriginPoint(self._width / 2, self._height / 2)

            painter.setRenderHint(QPainter.Antialiasing)

            rect = QRectF(0, 0, self._width, self._height)
            painter.fillRect(rect, QColor("#232323"))

            painter.setPen(QPen(QColor("white")))
            painter.drawText(rect, Qt.AlignCenter, "No initiative rolled")

            if not is_tv_view and not self.visible_to_players:
                painter.fillRect(rect, QColor(0, 0, 0, 120))

            return

        metrics = QFontMetrics(font)
        heroes_by_name = {hero.name: hero for hero in HeroManager.load_heroes()}

        badge_size = 16
        badge_reserve = badge_size + 12

        pills = []

        for entry in order:

            label = entry["name"] if entry["kind"] == "hero" else entry["label"]
            text = f"{label} ({entry['roll']})"

            hero = heroes_by_name.get(entry["name"]) if entry["kind"] == "hero" else None
            has_badge = bool(hero and hero.conditions)

            # boundingRect (actual rendered glyph extent) rather than
            # horizontalAdvance - the advance metric can under-report the
            # visual width for bold text on some fonts, clipping the edges.
            text_width = metrics.boundingRect(text).width()
            pill_width = max(PILL_MIN_WIDTH, text_width + PILL_H_PADDING)

            if has_badge:
                pill_width += badge_reserve

            pills.append((entry, text, pill_width, has_badge))

        new_width = sum(p[2] for p in pills) + (len(pills) - 1) * PILL_SPACING
        new_height = max(PILL_MIN_HEIGHT, metrics.height() + PILL_V_PADDING)

        if new_width != self._width or new_height != self._height:
            self.prepareGeometryChange()
            self._width = new_width
            self._height = new_height
            self.setTransformOriginPoint(self._width / 2, self._height / 2)

        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 0, self._width, self._height)
        painter.fillRect(rect, QColor("#232323"))

        x = 0.0

        for entry, text, pill_width, has_badge in pills:

            is_current = entry is current

            pill_rect = QRectF(x, 0, pill_width, self._height)

            border_color = QColor("#d4af37") if is_current else QColor("#555")
            painter.setPen(QPen(border_color, 2))
            painter.setBrush(QColor("#2b2b2b"))
            painter.drawRoundedRect(pill_rect, 8, 8)

            # Text is centered in the space left of the badge reserve (if any)
            # so the badge never has to sit on top of the roll number.
            text_rect = QRectF(pill_rect)
            if has_badge:
                text_rect.setRight(text_rect.right() - badge_reserve)

            painter.setFont(font)
            painter.setPen(QPen(QColor("white")))
            painter.drawText(text_rect, Qt.AlignCenter, text)

            if has_badge:

                badge_rect = QRectF(
                    pill_rect.right() - badge_size - 4,
                    pill_rect.top() + 4,
                    badge_size, badge_size
                )

                painter.save()

                painter.setBrush(QColor("#8b1a1a"))
                painter.setPen(QPen(QColor("#d4af37"), 1.5))
                painter.drawEllipse(badge_rect)

                badge_font = QFont()
                badge_font.setBold(True)
                badge_font.setPointSize(8)
                painter.setFont(badge_font)
                painter.setPen(QPen(QColor("white")))
                painter.drawText(badge_rect, Qt.AlignCenter, "!")

                painter.restore()

            x += pill_width + PILL_SPACING

        if not is_tv_view and not self.visible_to_players:
            painter.fillRect(rect, QColor(0, 0, 0, 120))


class InitiativeTrackerItem(BaseInitiativeTrackerItem):
    max_entries = None


class MiniInitiativeTrackerItem(BaseInitiativeTrackerItem):
    # Current turn plus the next 2 - a compact strip for a corner of the TV.
    max_entries = 3
