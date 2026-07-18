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
    QFrame,
    QScrollArea,
    QMessageBox,
    QProgressBar,
    QInputDialog,
)

from src.models.hero import Hero
from src.managers.hero_manager import HeroManager
from src.managers.soundboard_manager import SoundboardManager
from src.database.session_state import SessionState
from src.widgets.primary_button import PrimaryButton
from src.widgets.sound_player import play_sound


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


def hp_ratio_rgb(ratio):

    ratio = max(0.0, min(1.0, ratio))

    red = (224, 60, 60)
    green = (60, 200, 80)

    r = int(red[0] + (green[0] - red[0]) * ratio)
    g = int(red[1] + (green[1] - red[1]) * ratio)
    b = int(red[2] + (green[2] - red[2]) * ratio)

    return (r, g, b)


def hp_bar_color(ratio):

    r, g, b = hp_ratio_rgb(ratio)

    return f"rgb({r},{g},{b})"


def bar_style(chunk_color):
    return f"""
        QProgressBar {{
            border:2px solid #555;
            border-radius:6px;
            text-align:center;
            color:white;
            background:#1a1a1a;
        }}

        QProgressBar::chunk {{
            background-color:{chunk_color};
            border-radius:4px;
        }}
    """


def make_step_row(deltas, handler):

    row = QHBoxLayout()

    for delta in deltas:

        button = QPushButton(f"{delta:+d}")
        button.clicked.connect(lambda checked=False, d=delta: handler(d))
        row.addWidget(button)

    return row


class HeroOverviewCard(QFrame):

    def __init__(self, hero, active, initiative_roll, changed_callback):
        super().__init__()

        self.hero = hero
        self.active = active
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

        xp_row.addLayout(make_step_row([1, 5], self.add_xp))

        layout.addLayout(xp_row)

        #
        # HP / MP
        #

        stats_row = QHBoxLayout()

        hp_col = QVBoxLayout()

        self.hp_bar = QProgressBar()
        self.hp_bar.setTextVisible(True)
        hp_col.addWidget(self.hp_bar)

        hp_col.addLayout(make_step_row([-1, 1], self.adjust_hp))

        stats_row.addLayout(hp_col)

        mp_col = QVBoxLayout()

        self.mp_bar = QProgressBar()
        self.mp_bar.setTextVisible(True)
        self.mp_bar.setStyleSheet(bar_style("#3b82f6"))
        mp_col.addWidget(self.mp_bar)

        mp_col.addLayout(make_step_row([-1, 1], self.adjust_mp))

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

        #
        # Weapon
        #

        self.weapon_label = QLabel()
        layout.addWidget(self.weapon_label)

        #
        # Notes (read-only, edited on the Heroes page)
        #

        self.notes_label = QLabel()
        self.notes_label.setWordWrap(True)
        self.notes_label.setStyleSheet("color:#bbb; font-style:italic;")
        layout.addWidget(self.notes_label)

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

        self.conditions_widget = QWidget()
        self.conditions_widget.setLayout(conditions_grid)
        layout.addWidget(self.conditions_widget)

        # Weapon and conditions stay hidden unless it's this hero's turn -
        # click anywhere on the card to peek at them regardless.
        self.detail_widgets = [self.weapon_label, self.conditions_widget]

        for widget in self.detail_widgets:
            widget.setVisible(active)

    def mousePressEvent(self, event):

        for widget in self.detail_widgets:
            widget.setVisible(widget.isHidden())

        super().mousePressEvent(event)

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

        self.hp_bar.setRange(0, max(1, hero.max_hp))
        self.hp_bar.setValue(hero.hp)
        self.hp_bar.setFormat(f"HP {hero.hp}/{hero.max_hp}")
        ratio = hero.hp / hero.max_hp if hero.max_hp else 0
        self.hp_bar.setStyleSheet(bar_style(hp_bar_color(ratio)))

        self.mp_bar.setRange(0, max(1, hero.max_mp))
        self.mp_bar.setValue(hero.mp)
        self.mp_bar.setFormat(f"MP {hero.mp}/{hero.max_mp}")

        armour_bonus_text = f"+{hero.armour_bonus}" if hero.armour_bonus else "+0"
        self.armour_label.setText(
            f"Armour: {hero.base_armour} {armour_bonus_text} ({hero.total_armour})"
        )
        self.speed_label.setText(f"Speed: {hero.speed}")

        weapon_text = hero.weapon if hero.weapon else "—"
        self.weapon_label.setText(
            f"Weapon: {weapon_text} ({hero.weapon_bonus_type} +{hero.weapon_bonus})"
        )

        self.notes_label.setText(f"Notes: {hero.notes}" if hero.notes else "")

    def save_and_notify(self):

        HeroManager.save_hero(self.hero)
        self.update_display()
        self.changed_callback()

    def add_xp(self, amount):

        before_level = self.hero.level
        self.hero.add_xp(amount)

        if self.hero.level > before_level:
            play_sound(SoundboardManager.load_auto_sounds().level_up)

        self.save_and_notify()

    def adjust_hp(self, delta):

        before = self.hero.hp
        self.hero.hp = max(0, min(self.hero.max_hp, self.hero.hp + delta))

        if self.hero.hp != before:

            auto = SoundboardManager.load_auto_sounds()

            if delta < 0:
                if self.hero.hp <= 0:
                    death_sound = (
                        auto.hero_death_female if self.hero.gender == "Female"
                        else auto.hero_death_male
                    )
                    play_sound(death_sound)
                else:
                    play_sound(auto.hero_hit)
            else:
                play_sound(auto.hero_heal)

        self.save_and_notify()

    def adjust_mp(self, delta):

        self.hero.mp = max(0, min(self.hero.max_mp, self.hero.mp + delta))
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
        background = "#4a1a6b" if instance.kind == "villain" else "#2b2b2b"
        self.setStyleSheet(f"""
        QFrame {{
            background:{background};
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

        self.hp_bar = QProgressBar()
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setRange(0, max(1, instance.max_hp))
        self.hp_bar.setValue(instance.hp)
        self.hp_bar.setFormat(f"HP {instance.hp}/{instance.max_hp}")
        ratio = instance.hp / instance.max_hp if instance.max_hp else 0
        self.hp_bar.setStyleSheet(bar_style(hp_bar_color(ratio)))
        layout.addWidget(self.hp_bar)

        stats_row = QHBoxLayout()
        stats_row.addWidget(QLabel(f"Armour: {instance.ac}"))
        stats_row.addWidget(QLabel(f"Speed: {instance.speed}"))
        layout.addLayout(stats_row)

        self.detail_widgets = []

        if instance.behavior:

            behavior_label = QLabel(f"Behavior: {instance.behavior}")
            behavior_label.setWordWrap(True)
            behavior_label.setStyleSheet("color:#bbb; font-style:italic;")
            behavior_label.setVisible(active)
            layout.addWidget(behavior_label)

            self.detail_widgets.append(behavior_label)

        if instance.abilities:

            abilities_label = QLabel(f"Abilities: {instance.abilities}")
            abilities_label.setWordWrap(True)
            abilities_label.setStyleSheet("color:#bbb; font-style:italic;")
            abilities_label.setVisible(active)
            layout.addWidget(abilities_label)

            self.detail_widgets.append(abilities_label)

        #
        # Conditions
        #

        conditions_grid = QGridLayout()
        self.condition_buttons = {}

        for index, condition in enumerate(Hero.CONDITIONS):

            button = QPushButton(condition)
            button.setCheckable(True)
            button.setChecked(condition in instance.conditions)
            button.setStyleSheet(condition_button_style())
            button.toggled.connect(self.toggle_condition_handler(condition))

            self.condition_buttons[condition] = button

            conditions_grid.addWidget(button, index // 4, index % 4)

        self.conditions_widget = QWidget()
        self.conditions_widget.setLayout(conditions_grid)
        self.conditions_widget.setVisible(active)
        layout.addWidget(self.conditions_widget)

        self.detail_widgets.append(self.conditions_widget)

        if instance.is_defeated:
            defeated_label = QLabel("DEFEATED")
            defeated_label.setStyleSheet("color:#e05c5c; font-weight:bold;")
            layout.addWidget(defeated_label)

        layout.addLayout(make_step_row([-1, 1], self.adjust_hp))

        remove = QPushButton("Remove")
        remove.clicked.connect(self.remove)
        layout.addWidget(remove)

    def mousePressEvent(self, event):

        for widget in self.detail_widgets:
            widget.setVisible(widget.isHidden())

        super().mousePressEvent(event)

    def toggle_condition_handler(self, condition):

        def handler(checked):

            SessionState.set_instance_condition(self.instance.instance_id, condition, checked)
            self.changed_callback()

        return handler

    def adjust_hp(self, delta):

        before = self.instance.hp

        if delta < 0:
            SessionState.damage_instance(self.instance.instance_id, -delta)
        else:
            SessionState.heal_instance(self.instance.instance_id, delta)

        if delta < 0 and self.instance.hp != before:

            auto = SoundboardManager.load_auto_sounds()

            if self.instance.hp <= 0:
                play_sound(auto.monster_dead)
            else:
                play_sound(auto.monster_hit)

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

        self.miss_button = QPushButton("Miss")
        self.miss_button.clicked.connect(self.play_miss_sound)
        controls.addWidget(self.miss_button)

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
        turn_order_scroll.setFixedHeight(96)
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

        encounter_buttons = QHBoxLayout()

        self.random_encounter_button = PrimaryButton("Random Encounter")
        self.random_encounter_button.clicked.connect(self.add_random_encounter)
        encounter_buttons.addWidget(self.random_encounter_button)

        self.select_monster_button = PrimaryButton("Select Monster")
        self.select_monster_button.clicked.connect(self.select_monster)
        encounter_buttons.addWidget(self.select_monster_button)

        right.addLayout(encounter_buttons)

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

    def play_miss_sound(self):
        play_sound(SoundboardManager.load_auto_sounds().miss)

    def active_heroes(self):
        return [h for h in HeroManager.load_heroes() if not h.is_dm]

    def roll_initiative(self):

        SessionState.roll_initiative(self.active_heroes())
        self.refresh()

    def next_turn(self):

        current = SessionState.current_turn()

        if current is not None:
            self.confirm_condition_expiry(current)

        SessionState.next_turn(self.active_heroes())
        self.refresh()

    def confirm_condition_expiry(self, entry):

        if entry["kind"] == "hero":

            hero = next((h for h in self.active_heroes() if h.name == entry["name"]), None)

            if hero is None or not hero.conditions:
                return

            changed = False

            for condition in list(hero.conditions):

                answer = QMessageBox.question(
                    self,
                    "Condition Check",
                    f"Has '{condition}' ended for {hero.name}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if answer == QMessageBox.Yes:
                    hero.conditions.remove(condition)
                    changed = True

            if changed:
                HeroManager.save_hero(hero)

        else:

            instance = next(
                (i for i in SessionState.encounter() if i.instance_id == entry["instance_id"]),
                None
            )

            if instance is None or not instance.conditions:
                return

            for condition in list(instance.conditions):

                answer = QMessageBox.question(
                    self,
                    "Condition Check",
                    f"Has '{condition}' ended for {instance.label}?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if answer == QMessageBox.Yes:
                    SessionState.set_instance_condition(instance.instance_id, condition, False)

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

        self.refresh()

    def select_monster(self):

        pool = SessionState.pool()

        if not pool:
            QMessageBox.information(
                self,
                "No Monsters in Session",
                "Add monsters to the session pool on the Session tab first."
            )
            return

        names = [entry.name for entry in pool]

        name, ok = QInputDialog.getItem(
            self,
            "Select Monster",
            "Monster:",
            names,
            0,
            False
        )

        if not ok or not name:
            return

        entry = next((e for e in pool if e.name == name), None)

        if entry is not None:

            instance = SessionState.add_specific_encounter(entry.pool_id)

            if instance is not None:
                play_sound(instance.sound)

        self.refresh()

    def show_conditions_handler(self, hero_name, conditions):

        def handler():
            QMessageBox.information(
                self,
                f"{hero_name} — Conditions",
                ", ".join(conditions)
            )

        return handler

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

        heroes_by_name = {hero.name: hero for hero in self.active_heroes()}

        for entry in order:

            is_current = entry is current

            label_text = entry["name"] if entry["kind"] == "hero" else entry["label"]

            pill_column = QVBoxLayout()
            pill_column.setSpacing(2)

            hero = heroes_by_name.get(entry["name"]) if entry["kind"] == "hero" else None

            if hero and hero.conditions:

                condition_button = QPushButton("!")
                condition_button.setFixedSize(22, 22)
                condition_button.setToolTip(", ".join(hero.conditions))
                condition_button.setStyleSheet("""
                    QPushButton {
                        background:#8b1a1a;
                        color:white;
                        border:2px solid #d4af37;
                        border-radius:11px;
                        font-weight:bold;
                    }
                """)
                condition_button.clicked.connect(
                    self.show_conditions_handler(hero.name, hero.conditions)
                )

                pill_column.addWidget(condition_button, alignment=Qt.AlignHCenter)

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

            pill_column.addWidget(pill)

            pill_column_widget = QWidget()
            pill_column_widget.setLayout(pill_column)

            self.turn_order_container.addWidget(pill_column_widget)

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
