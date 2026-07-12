from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QFrame,
    QScrollArea,
    QMessageBox,
    QProgressBar,
)

from src.models.hero import Hero
from src.managers.hero_manager import HeroManager
from src.database.session_state import SessionState
from src.widgets.primary_button import PrimaryButton


PORTRAIT_SIZE = 72


ACTIVE_BORDER = "border:2px solid #d4af37;"
INACTIVE_BORDER = "border:2px solid #555;"


def condition_button_style():
    return """
        QPushButton {
            background:#2b2b2b;
            color:white;
            border:2px solid #555;
            border-radius:8px;
            padding:4px;
        }

        QPushButton:checked {
            background:#8b1a1a;
            border:2px solid #d4af37;
        }
    """


class HeroOverviewCard(QFrame):

    def __init__(self, hero, active, initiative_roll, changed_callback):
        super().__init__()

        self.hero = hero
        self.changed_callback = changed_callback

        self.setFrameShape(QFrame.StyledPanel)

        border = ACTIVE_BORDER if active else INACTIVE_BORDER
        self.setStyleSheet(f"""
        QFrame {{
            background:#2b2b2b;
            {border}
            border-radius:12px;
        }}

        QLabel {{
            color:white;
        }}
        """)

        layout = QVBoxLayout(self)

        #
        # Portrait + name/level
        #

        header_row = QHBoxLayout()

        self.portrait_label = QLabel()
        self.portrait_label.setFixedSize(PORTRAIT_SIZE, PORTRAIT_SIZE)
        self.portrait_label.setAlignment(Qt.AlignCenter)
        self.portrait_label.setStyleSheet("""
            background:#1a1a1a;
            border:2px solid #555;
            border-radius:8px;
        """)

        if hero.portrait and Path(hero.portrait).exists():
            pixmap = QPixmap(hero.portrait).scaled(
                PORTRAIT_SIZE,
                PORTRAIT_SIZE,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.portrait_label.setPixmap(pixmap)

        header_row.addWidget(self.portrait_label)

        name_level_col = QVBoxLayout()

        name_row = QHBoxLayout()

        name_label = QLabel(f"{hero.name} ({hero.hero_class})")
        name_label.setStyleSheet("font-size:18px; font-weight:bold;")
        name_row.addWidget(name_label)

        name_row.addStretch()

        self.level_label = QLabel()
        self.level_label.setStyleSheet("font-weight:bold;")
        name_row.addWidget(self.level_label)

        name_level_col.addLayout(name_row)

        if initiative_roll is not None:
            initiative_label = QLabel(f"Initiative: {initiative_roll}")
            initiative_label.setStyleSheet("color:#d4af37; font-weight:bold;")
            name_level_col.addWidget(initiative_label)

        header_row.addLayout(name_level_col)

        layout.addLayout(header_row)

        #
        # XP bar
        #

        xp_row = QHBoxLayout()

        self.xp_bar = QProgressBar()
        self.xp_bar.setTextVisible(True)
        xp_row.addWidget(self.xp_bar)

        xp_add = QPushButton("+XP")
        xp_add.clicked.connect(self.add_xp)
        xp_row.addWidget(xp_add)

        layout.addLayout(xp_row)

        #
        # Shared amount
        #

        self.amount = QSpinBox()
        self.amount.setRange(1, 20)
        self.amount.setValue(1)
        layout.addWidget(self.amount)

        #
        # HP / MP
        #

        stats_row = QHBoxLayout()

        hp_col = QVBoxLayout()

        self.hp_label = QLabel()
        hp_col.addWidget(self.hp_label)

        hp_buttons = QHBoxLayout()

        hp_damage = QPushButton("HP -")
        hp_damage.clicked.connect(self.damage_hp)
        hp_buttons.addWidget(hp_damage)

        hp_heal = QPushButton("HP +")
        hp_heal.clicked.connect(self.heal_hp)
        hp_buttons.addWidget(hp_heal)

        hp_col.addLayout(hp_buttons)

        stats_row.addLayout(hp_col)

        mp_col = QVBoxLayout()

        self.mp_label = QLabel()
        mp_col.addWidget(self.mp_label)

        mp_buttons = QHBoxLayout()

        mp_damage = QPushButton("MP -")
        mp_damage.clicked.connect(self.damage_mp)
        mp_buttons.addWidget(mp_damage)

        mp_heal = QPushButton("MP +")
        mp_heal.clicked.connect(self.heal_mp)
        mp_buttons.addWidget(mp_heal)

        mp_col.addLayout(mp_buttons)

        stats_row.addLayout(mp_col)

        layout.addLayout(stats_row)

        #
        # Armour / Speed
        #

        armour_speed_row = QHBoxLayout()

        self.armour_label = QLabel()
        armour_speed_row.addWidget(self.armour_label)

        self.speed_label = QLabel()
        armour_speed_row.addWidget(self.speed_label)

        layout.addLayout(armour_speed_row)

        self.update_display()

        #
        # Conditions
        #

        conditions_grid = QGridLayout()
        self.condition_buttons = {}

        for index, condition in enumerate(Hero.CONDITIONS):

            button = QPushButton(condition)
            button.setCheckable(True)
            button.setChecked(condition in hero.conditions)
            button.setStyleSheet(condition_button_style())
            button.toggled.connect(self.toggle_condition_handler(condition))

            self.condition_buttons[condition] = button

            conditions_grid.addWidget(button, index // 4, index % 4)

        layout.addLayout(conditions_grid)

    def update_display(self):

        hero = self.hero

        self.level_label.setText(f"Lv {hero.level}")

        if hero.level < Hero.MAX_LEVEL:
            threshold = 10 * hero.level
            self.xp_bar.setRange(0, threshold)
            self.xp_bar.setValue(min(hero.xp, threshold))
            self.xp_bar.setFormat(f"{hero.xp}/{threshold} XP")
        else:
            self.xp_bar.setRange(0, 1)
            self.xp_bar.setValue(1)
            self.xp_bar.setFormat("MAX LEVEL")

        self.hp_label.setText(f"HP {hero.hp}/{hero.max_hp}")
        self.mp_label.setText(f"MP {hero.mp}/{hero.max_mp}")

        armour_bonus_text = f"+{hero.armour_bonus}" if hero.armour_bonus else "+0"
        self.armour_label.setText(
            f"Armour: {hero.base_armour} {armour_bonus_text} ({hero.total_armour})"
        )
        self.speed_label.setText(f"Speed: {hero.speed}")

    def save_and_notify(self):

        HeroManager.save_hero(self.hero)
        self.update_display()
        self.changed_callback()

    def add_xp(self):

        self.hero.add_xp(self.amount.value())
        self.save_and_notify()

    def damage_hp(self):

        self.hero.hp = max(0, self.hero.hp - self.amount.value())
        self.save_and_notify()

    def heal_hp(self):

        self.hero.hp = min(self.hero.max_hp, self.hero.hp + self.amount.value())
        self.save_and_notify()

    def damage_mp(self):

        self.hero.mp = max(0, self.hero.mp - self.amount.value())
        self.save_and_notify()

    def heal_mp(self):

        self.hero.mp = min(self.hero.max_mp, self.hero.mp + self.amount.value())
        self.save_and_notify()

    def toggle_condition_handler(self, condition):

        def handler(checked):

            if checked and condition not in self.hero.conditions:
                self.hero.conditions.append(condition)
            elif not checked and condition in self.hero.conditions:
                self.hero.conditions.remove(condition)

            self.save_and_notify()

        return handler


class MonsterInstanceCard(QFrame):

    def __init__(self, instance, active, initiative_roll, changed_callback):
        super().__init__()

        self.instance = instance
        self.changed_callback = changed_callback

        self.setFrameShape(QFrame.StyledPanel)

        border = ACTIVE_BORDER if active else INACTIVE_BORDER
        self.setStyleSheet(f"""
        QFrame {{
            background:#2b2b2b;
            {border}
            border-radius:12px;
        }}

        QLabel {{
            color:white;
        }}
        """)

        layout = QVBoxLayout(self)

        title = QLabel(instance.label)
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        if initiative_roll is not None:
            initiative_label = QLabel(f"Initiative: {initiative_roll}")
            initiative_label.setStyleSheet("color:#d4af37; font-weight:bold;")
            layout.addWidget(initiative_label)

        self.hp_label = QLabel(f"HP {instance.hp}/{instance.max_hp}")
        layout.addWidget(self.hp_label)

        if instance.is_defeated:
            defeated_label = QLabel("DEFEATED")
            defeated_label.setStyleSheet("color:#e05c5c; font-weight:bold;")
            layout.addWidget(defeated_label)

        self.amount = QSpinBox()
        self.amount.setRange(1, 20)
        self.amount.setValue(1)
        layout.addWidget(self.amount)

        hp_row = QHBoxLayout()

        damage = QPushButton("Damage")
        damage.clicked.connect(self.damage)
        hp_row.addWidget(damage)

        heal = QPushButton("Heal")
        heal.clicked.connect(self.heal)
        hp_row.addWidget(heal)

        layout.addLayout(hp_row)

        remove = QPushButton("Remove")
        remove.clicked.connect(self.remove)
        layout.addWidget(remove)

    def damage(self):

        SessionState.damage_instance(self.instance.instance_id, self.amount.value())
        self.changed_callback()

    def heal(self):

        SessionState.heal_instance(self.instance.instance_id, self.amount.value())
        self.changed_callback()

    def remove(self):

        SessionState.remove_instance(self.instance.instance_id)
        self.changed_callback()


class GameplayPage(QWidget):

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)

        title = QLabel("Gameplay")
        title.setStyleSheet("font-size:28px; font-weight:bold;")
        root.addWidget(title)

        #
        # Top control bar
        #

        controls = QHBoxLayout()

        self.roll_button = PrimaryButton("Roll Initiative")
        self.roll_button.clicked.connect(self.roll_initiative)
        controls.addWidget(self.roll_button)

        self.next_turn_button = PrimaryButton("Next Turn")
        self.next_turn_button.clicked.connect(self.next_turn)
        controls.addWidget(self.next_turn_button)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size:16px; font-weight:bold;")
        controls.addWidget(self.status_label)

        controls.addStretch()

        root.addLayout(controls)

        #
        # Turn order strip
        #

        self.turn_order_container = QHBoxLayout()
        self.turn_order_container.setSpacing(10)

        turn_order_widget = QWidget()
        turn_order_widget.setLayout(self.turn_order_container)

        turn_order_scroll = QScrollArea()
        turn_order_scroll.setWidgetResizable(True)
        turn_order_scroll.setFixedHeight(70)
        turn_order_scroll.setWidget(turn_order_widget)

        root.addWidget(turn_order_scroll)

        #
        # Body
        #

        body = QHBoxLayout()

        #
        # Left: heroes
        #

        left = QVBoxLayout()
        left.addWidget(QLabel("Heroes"))

        self.heroes_container = QVBoxLayout()

        heroes_widget = QWidget()
        heroes_widget.setLayout(self.heroes_container)

        heroes_scroll = QScrollArea()
        heroes_scroll.setWidgetResizable(True)
        heroes_scroll.setWidget(heroes_widget)

        left.addWidget(heroes_scroll)

        body.addLayout(left, 1)

        #
        # Right: encounter
        #

        right = QVBoxLayout()

        self.random_encounter_button = PrimaryButton("Random Encounter")
        self.random_encounter_button.clicked.connect(self.add_random_encounter)
        right.addWidget(self.random_encounter_button)

        self.encounter_container = QVBoxLayout()

        encounter_widget = QWidget()
        encounter_widget.setLayout(self.encounter_container)

        encounter_scroll = QScrollArea()
        encounter_scroll.setWidgetResizable(True)
        encounter_scroll.setWidget(encounter_widget)

        right.addWidget(encounter_scroll)

        body.addLayout(right, 1)

        root.addLayout(body)

        self.refresh()

    def showEvent(self, event):

        super().showEvent(event)
        self.refresh()

    def active_heroes(self):
        return [h for h in HeroManager.load_heroes() if not h.is_dm]

    def roll_initiative(self):

        SessionState.roll_initiative(self.active_heroes())
        self.refresh()

    def next_turn(self):

        SessionState.next_turn()
        self.refresh()

    def add_random_encounter(self):

        instance = SessionState.add_random_encounter()

        if instance is None:
            QMessageBox.information(
                self,
                "No Monsters in Session",
                "Add monsters to the session pool on the Session tab first."
            )

        self.refresh()

    def refresh(self):

        while self.heroes_container.count():

            item = self.heroes_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        while self.encounter_container.count():

            item = self.encounter_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        while self.turn_order_container.count():

            item = self.turn_order_container.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        order = SessionState.initiative_order()
        current = SessionState.current_turn()

        roll_by_hero = {
            entry["name"]: entry["roll"]
            for entry in order if entry["kind"] == "hero"
        }
        roll_by_instance = {
            entry["instance_id"]: entry["roll"]
            for entry in order if entry["kind"] == "monster"
        }

        for hero in self.active_heroes():

            active = (
                current is not None
                and current.get("kind") == "hero"
                and current.get("name") == hero.name
            )

            self.heroes_container.addWidget(
                HeroOverviewCard(
                    hero, active, roll_by_hero.get(hero.name), self.refresh
                )
            )

        self.heroes_container.addStretch()

        for instance in SessionState.encounter():

            active = (
                current is not None
                and current.get("kind") == "monster"
                and current.get("instance_id") == instance.instance_id
            )

            self.encounter_container.addWidget(
                MonsterInstanceCard(
                    instance,
                    active,
                    roll_by_instance.get(instance.instance_id),
                    self.refresh
                )
            )

        self.encounter_container.addStretch()

        for entry in order:

            is_current = entry is current

            label_text = entry["name"] if entry["kind"] == "hero" else entry["label"]

            pill = QLabel(f"{label_text}\n({entry['roll']})")
            pill.setAlignment(Qt.AlignCenter)

            border = ACTIVE_BORDER if is_current else INACTIVE_BORDER
            pill.setStyleSheet(f"""
                background:#2b2b2b;
                color:white;
                {border}
                border-radius:8px;
                padding:6px;
            """)

            self.turn_order_container.addWidget(pill)

        self.turn_order_container.addStretch()

        if current is None:
            self.status_label.setText("No initiative rolled")
        elif current.get("kind") == "hero":
            self.status_label.setText(
                f"Round {SessionState.round_number()} — {current['name']}'s turn"
            )
        else:
            self.status_label.setText(
                f"Round {SessionState.round_number()} — {current['label']}'s turn"
            )

        self.next_turn_button.setEnabled(bool(SessionState.initiative_order()))
