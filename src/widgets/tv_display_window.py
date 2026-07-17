from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView


class TVDisplayWindow(QWidget):

    def __init__(self, scene):
        super().__init__()

        self.scene = scene

        self.setWindowTitle("Dungeon Master's Toolkit - Player Display")
        self.resize(1024, 768)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = QGraphicsView(scene)
        self.view.setBackgroundBrush(QColor("#000000"))
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)

        layout.addWidget(self.view)

        scene.tv_viewport = self.view.viewport()

        self.fit_view()

    def fit_view(self):
        # Stretch to fill the whole window/screen (no letterboxing bars) -
        # the scene's internal 4:3 coordinate space stays fixed for widget
        # placement math, this just controls how it's presented on screen.
        self.view.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_view()

    def showEvent(self, event):
        super().showEvent(event)
        self.fit_view()

    def closeEvent(self, event):

        if self.scene.tv_viewport is self.view.viewport():
            self.scene.tv_viewport = None

        super().closeEvent(event)
