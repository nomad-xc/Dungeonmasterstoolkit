from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
)

from src.widgets.sound_player import play_sound


class SoundPickerDialog(QDialog):

    def __init__(self, sounds, parent=None):
        super().__init__(parent)

        self.sounds = sounds

        self.setWindowTitle("Add Sound(s)")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()

        for sound in sounds:

            item = QListWidgetItem(sound.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        play_button = QPushButton("Play Selected")
        play_button.clicked.connect(self.play_selected)
        layout.addWidget(play_button)

        buttons = QHBoxLayout()

        add = QPushButton("Add")
        cancel = QPushButton("Cancel")

        add.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        buttons.addWidget(add)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

    def play_selected(self):

        for sound in self.selected_sounds():
            play_sound(sound.path)

    def selected_sounds(self):

        selected = []

        for row in range(self.list_widget.count()):

            item = self.list_widget.item(row)

            if item.checkState() == Qt.Checked:
                selected.append(self.sounds[row])

        return selected
