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
    QTabWidget,
)

from src.managers.monster_manager import MonsterManager
from src.managers.story_manager import StoryManager
from src.database.session_state import SessionState


class SessionPage(QWidget):

    def __init__(self):
        super().__init__()

        outer = QVBoxLayout(self)

        self.tabs = QTabWidget()
        outer.addWidget(self.tabs)

        monster_tab = QWidget()
        self._build_monster_tab(monster_tab)
        self.tabs.addTab(monster_tab, "Monster")

        story_tab = QWidget()
        self._build_story_tab(story_tab)
        self.tabs.addTab(story_tab, "Story")

        self.refresh()

    def _build_monster_tab(self, tab):

        root = QHBoxLayout(tab)

        #
        # Left: pick from library, tweak stats, add
        #

        left = QVBoxLayout()

        title = QLabel("Monsters")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)
        left.addWidget(title)

        left.addWidget(QLabel("Start from a Library monster:"))

        self.kind_filter = QComboBox()
        self.kind_filter.addItems(["Monster", "Villain"])
        self.kind_filter.currentIndexChanged.connect(self.refresh_type_filter)
        left.addWidget(self.kind_filter)

        left.addWidget(QLabel("Type:"))

        self.type_filter = QComboBox()
        self.type_filter.currentIndexChanged.connect(self.refresh_monster_picker)
        left.addWidget(self.type_filter)

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

        self.abilities = QTextEdit()
        self.abilities.setPlaceholderText("Abilities...")
        self.abilities.setMaximumHeight(80)
        left.addWidget(self.abilities)

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

    def _build_story_tab(self, tab):

        layout = QVBoxLayout(tab)

        title = QLabel("Story")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)
        layout.addWidget(title)

        self.story_text = QTextEdit()
        self.story_text.setPlaceholderText("Write the story for this session...")
        self.story_text.textChanged.connect(self.save_story)
        layout.addWidget(self.story_text)

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()

    def refresh(self):

        self.all_monsters = MonsterManager.load_monsters()

        self.refresh_type_filter()
        self.refresh_pool_list()
        self.load_story_text()

    def selected_kind(self):
        return "villain" if self.kind_filter.currentText() == "Villain" else "monster"

    def refresh_type_filter(self):

        kind = self.selected_kind()

        types = sorted({
            m.creature_type or "Unsorted"
            for m in self.all_monsters if m.kind == kind
        })

        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems(types)
        self.type_filter.blockSignals(False)

        self.refresh_monster_picker()

    def refresh_monster_picker(self):

        kind = self.selected_kind()
        type_choice = self.type_filter.currentText()

        self.filtered_monsters = [
            m for m in self.all_monsters
            if m.kind == kind
            and (type_choice in ("All Types", "") or (m.creature_type or "Unsorted") == type_choice)
        ]

        self.monster_picker.blockSignals(True)
        self.monster_picker.clear()

        for monster in self.filtered_monsters:
            self.monster_picker.addItem(monster.name)

        self.monster_picker.blockSignals(False)

        self.load_selected_into_form()

    def load_story_text(self):

        self.story_text.blockSignals(True)
        self.story_text.setPlainText(StoryManager.load_story())
        self.story_text.blockSignals(False)

    def save_story(self):

        StoryManager.save_story(self.story_text.toPlainText())

    def load_selected_into_form(self):

        index = self.monster_picker.currentIndex()

        if not (0 <= index < len(self.filtered_monsters)):
            self.name.setText("")
            self.hp.setValue(0)
            self.max_hp.setValue(1)
            self.ac.setValue(0)
            self.speed.setValue(0)
            self.xp.setValue(0)
            self.behavior.setPlainText("")
            self.abilities.setPlainText("")
            return

        monster = self.filtered_monsters[index]

        self.name.setText(monster.name)
        self.hp.setValue(monster.hp)
        self.max_hp.setValue(monster.max_hp)
        self.ac.setValue(monster.ac)
        self.speed.setValue(monster.speed)
        self.xp.setValue(monster.xp)
        self.behavior.setPlainText(monster.behavior)
        self.abilities.setPlainText(monster.abilities)

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
            kind=self.selected_kind(),
            behavior=self.behavior.toPlainText(),
            abilities=self.abilities.toPlainText(),
        )

        self.refresh_pool_list()

    def remove_selected(self):

        item = self.pool_list.currentItem()

        if item is None:
            return

        pool_id = item.data(Qt.UserRole)

        SessionState.remove_from_pool(pool_id)

        self.refresh_pool_list()
