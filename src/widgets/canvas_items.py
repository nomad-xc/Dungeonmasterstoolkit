import math
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPen, QPixmap, QPainterPath, QFont, QPainter
from PySide6.QtWidgets import QGraphicsObject, QGraphicsScene

from src.managers.hero_manager import HeroManager
from src.database.session_state import SessionState
from src.pages.gameplay import hp_ratio_rgb


HANDLE_SIZE = 10
ROTATE_HANDLE_OFFSET = 24
MIN_SIZE = 20

SCENE_WIDTH = 1600
SCENE_HEIGHT = 1200


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
                    event.accept()
                    return

        self._active_handle = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self._active_handle == "resize":

            local = event.pos()

            self.prepareGeometryChange()
            self._width = max(MIN_SIZE, local.x())
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
PILL_HEIGHT = 60
PILL_SPACING = 8


class InitiativeTrackerItem(ResizableRotatableItem):

    def __init__(self, widget_id, x, y, rotation=0, visible_to_players=True):
        super().__init__(widget_id, x, y, PILL_WIDTH, PILL_HEIGHT, rotation)

        self.visible_to_players = visible_to_players

    def handles(self):

        all_handles = super().handles()

        return {"rotate": all_handles["rotate"]}

    def paint_content(self, painter, option, widget=None):

        is_tv_view = self.scene() is not None and widget is self.scene().tv_viewport

        if is_tv_view and not self.visible_to_players:
            return

        order = SessionState.initiative_order()
        current = SessionState.current_turn()

        count = max(1, len(order))
        new_width = count * PILL_WIDTH + (count - 1) * PILL_SPACING
        new_height = PILL_HEIGHT

        if new_width != self._width or new_height != self._height:
            self.prepareGeometryChange()
            self._width = new_width
            self._height = new_height
            self.setTransformOriginPoint(self._width / 2, self._height / 2)

        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(0, 0, self._width, self._height)
        painter.fillRect(rect, QColor("#232323"))

        if not order:
            painter.setPen(QPen(QColor("white")))
            painter.drawText(rect, Qt.AlignCenter, "No initiative rolled")

            if not is_tv_view and not self.visible_to_players:
                painter.fillRect(rect, QColor(0, 0, 0, 120))

            return

        font = QFont()
        font.setBold(True)
        painter.setFont(font)

        x = 0.0

        for entry in order:

            is_current = entry is current
            label = entry["name"] if entry["kind"] == "hero" else entry["label"]
            roll = entry["roll"]

            pill_rect = QRectF(x, 0, PILL_WIDTH, PILL_HEIGHT)

            border_color = QColor("#d4af37") if is_current else QColor("#555")
            painter.setPen(QPen(border_color, 2))
            painter.setBrush(QColor("#2b2b2b"))
            painter.drawRoundedRect(pill_rect, 8, 8)

            painter.setPen(QPen(QColor("white")))
            painter.drawText(pill_rect, Qt.AlignCenter, f"{label}\n({roll})")

            x += PILL_WIDTH + PILL_SPACING

        if not is_tv_view and not self.visible_to_players:
            painter.fillRect(rect, QColor(0, 0, 0, 120))
