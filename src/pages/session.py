from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QTextEdit,
)

from src.managers.monster_manager import MonsterManager
from src.database.session_state import SessionState


class SessionPage(QWidget):

    def __init__(self):
        super().__init__()

        root = QHBoxLayout(self)

        #
        # Left: pick from library, tweak stats, add
        #

        left = QVBoxLayout()

        title = QLabel("Session")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)
        left.addWidget(title)

        left.addWidget(QLabel("Start from a Library monster:"))

        self.monster_picker = QComboBox()
        self.monster_picker.currentIndexChanged.connect(self.load_selected_into_form)
        left.addWidget(self.monster_picker)

        form = QFormLayout()

        self.name = QLineEdit()
        form.addRow("Name", self.name)

        self.hp = QSpinBox()
        self.hp.setRange(0, 9999)
        form.addRow("HP", self.hp)

        self.max_hp = QSpinBox()
        self.max_hp.setRange(1, 9999)
        form.addRow("Max HP", self.max_hp)

        self.ac = QSpinBox()
        self.ac.setRange(0, 99)
        form.addRow("AC", self.ac)

        self.speed = QSpinBox()
        self.speed.setRange(0, 200)
        form.addRow("Speed", self.speed)

        self.xp = QSpinBox()
        self.xp.setRange(0, 99999999)
        form.addRow("XP", self.xp)

        left.addLayout(form)

        self.behavior = QTextEdit()
        self.behavior.setPlaceholderText("Behavior...")
        self.behavior.setMaximumHeight(80)
        left.addWidget(self.behavior)

        self.add_button = QPushButton("Add to Session")
        self.add_button.clicked.connect(self.add_to_session)
        left.addWidget(self.add_button)

        left.addStretch()

        root.addLayout(left, 1)

        #
        # Right: session pool
        #

        right = QVBoxLayout()

        pool_title = QLabel("In This Session")
        pool_title.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
        """)
        right.addWidget(pool_title)

        self.pool_list = QListWidget()
        right.addWidget(self.pool_list)

        self.remove_button = QPushButton("Remove from Session")
        self.remove_button.clicked.connect(self.remove_selected)
        right.addWidget(self.remove_button)

        root.addLayout(right, 1)

        self.refresh()

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()

    def refresh(self):

        self.monsters = MonsterManager.load_monsters()

        self.monster_picker.blockSignals(True)
        self.monster_picker.clear()

        for monster in self.monsters:
            self.monster_picker.addItem(monster.name)

        self.monster_picker.blockSignals(False)

        self.load_selected_into_form()
        self.refresh_pool_list()

    def load_selected_into_form(self):

        index = self.monster_picker.currentIndex()

        if not (0 <= index < len(self.monsters)):
            self.name.setText("")
            self.hp.setValue(0)
            self.max_hp.setValue(1)
            self.ac.setValue(0)
            self.speed.setValue(0)
            self.xp.setValue(0)
            self.behavior.setPlainText("")
            return

        monster = self.monsters[index]

        self.name.setText(monster.name)
        self.hp.setValue(monster.hp)
        self.max_hp.setValue(monster.max_hp)
        self.ac.setValue(monster.ac)
        self.speed.setValue(monster.speed)
        self.xp.setValue(monster.xp)
        self.behavior.setPlainText(monster.behavior)

    def refresh_pool_list(self):

        self.pool_list.clear()

        for entry in SessionState.pool():

            self.pool_list.addItem(entry.name)

            item = self.pool_list.item(self.pool_list.count() - 1)
            item.setData(Qt.UserRole, entry.pool_id)

    def add_to_session(self):

        name = self.name.text().strip()

        if not name:
            return

        SessionState.add_to_pool(
            name=name,
            hp=self.hp.value(),
            max_hp=self.max_hp.value(),
            ac=self.ac.value(),
            speed=self.speed.value(),
            xp=self.xp.value(),
            behavior=self.behavior.toPlainText(),
        )

        self.refresh_pool_list()

    def remove_selected(self):

        item = self.pool_list.currentItem()

        if item is None:
            return

        pool_id = item.data(Qt.UserRole)

        SessionState.remove_from_pool(pool_id)

        self.refresh_pool_list()
