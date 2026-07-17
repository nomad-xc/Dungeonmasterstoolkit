from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
)


PREVIEW_WIDTH = 380
PREVIEW_HEIGHT = 240


class MapPickerDialog(QDialog):

    def __init__(self, maps, parent=None):
        super().__init__(parent)

        self.maps = maps

        self.setWindowTitle("Add Map")
        self.resize(450, 400)

        layout = QVBoxLayout(self)

        self.picker = QComboBox()

        for map_obj in maps:
            self.picker.addItem(map_obj.name)

        self.picker.currentIndexChanged.connect(self.update_preview)
        layout.addWidget(self.picker)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.preview_label.setStyleSheet("""
            background:#2b2b2b;
            border:2px solid #555;
            border-radius:8px;
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        buttons = QHBoxLayout()

        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")

        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        buttons.addWidget(ok)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

        self.update_preview()

    def update_preview(self):

        map_obj = self.selected_map()

        if map_obj and map_obj.path and Path(map_obj.path).exists():

            pixmap = QPixmap(map_obj.path).scaled(
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(pixmap)

        else:
            self.preview_label.clear()

    def selected_map(self):

        index = self.picker.currentIndex()

        if 0 <= index < len(self.maps):
            return self.maps[index]

        return None
