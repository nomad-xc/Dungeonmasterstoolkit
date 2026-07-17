from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QInputDialog,
)

from src.managers.map_manager import MapManager


PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 260

UNSORTED_OPTION = "(Unsorted)"
NEW_FOLDER_OPTION = "+ New Folder..."


class MapEditor(QDialog):

    def __init__(self, map_obj):
        super().__init__()

        self.map_obj = map_obj

        self.setWindowTitle(map_obj.name)
        self.resize(500, 550)

        layout = QVBoxLayout(self)

        #
        # Preview
        #

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(PREVIEW_WIDTH, PREVIEW_HEIGHT)
        self.preview_label.setStyleSheet("""
            background:#2b2b2b;
            border:2px solid #555;
            border-radius:8px;
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        self.update_preview()

        #
        # Form
        #

        form = QFormLayout()

        self.name = QLineEdit(map_obj.name)
        form.addRow("Name", self.name)

        self.category = QComboBox()
        self.populate_folders()
        self.category.currentIndexChanged.connect(self.handle_category_change)
        form.addRow("Category", self.category)

        layout.addLayout(form)

        self.notes = QTextEdit(map_obj.notes)
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

    def populate_folders(self, select=None):

        self.category.blockSignals(True)
        self.category.clear()

        folders = MapManager.load_folders()

        current = select if select is not None else self.map_obj.category

        if current and current not in folders:
            folders = folders + [current]

        self.category.addItem(UNSORTED_OPTION)
        self.category.addItems(folders)
        self.category.addItem(NEW_FOLDER_OPTION)

        index = self.category.findText(current) if current else 0
        self.category.setCurrentIndex(index if index >= 0 else 0)

        self.category.blockSignals(False)

    def handle_category_change(self, index):

        if self.category.currentText() != NEW_FOLDER_OPTION:
            return

        name, ok = QInputDialog.getText(
            self,
            "New Folder",
            "Folder Name:"
        )

        if ok and name:
            MapManager.create_folder(name)
            self.populate_folders(select=name)
        else:
            self.populate_folders(select=self.map_obj.category)

    def update_preview(self):

        if self.map_obj.path and Path(self.map_obj.path).exists():

            pixmap = QPixmap(self.map_obj.path).scaled(
                PREVIEW_WIDTH,
                PREVIEW_HEIGHT,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(pixmap)

        else:
            self.preview_label.clear()

    def save(self):

        self.map_obj.name = self.name.text()

        category_text = self.category.currentText()
        self.map_obj.category = "" if category_text == UNSORTED_OPTION else category_text

        self.map_obj.notes = self.notes.toPlainText()

        self.accept()
