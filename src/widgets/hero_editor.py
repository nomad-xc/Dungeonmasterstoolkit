from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)


class HeroEditor(QDialog):

    def __init__(self, hero):
        super().__init__()

        self.hero = hero

        self.setWindowTitle(hero.name)
        self.resize(500, 650)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name = QLineEdit(hero.name)
        form.addRow("Name", self.name)

        self.hero_class = QLineEdit(hero.hero_class)
        form.addRow("Class", self.hero_class)

        self.level = QSpinBox()
        self.level.setRange(1, 20)
        self.level.setValue(hero.level)
        form.addRow("Level", self.level)

        self.hp = QSpinBox()
        self.hp.setRange(0, 9999)
        self.hp.setValue(hero.hp)
        form.addRow("HP", self.hp)

        self.max_hp = QSpinBox()
        self.max_hp.setRange(1, 9999)
        self.max_hp.setValue(hero.max_hp)
        form.addRow("Max HP", self.max_hp)

        self.mp = QSpinBox()
        self.mp.setRange(0, 9999)
        self.mp.setValue(hero.mp)
        form.addRow("MP", self.mp)

        self.max_mp = QSpinBox()
        self.max_mp.setRange(0, 9999)
        self.max_mp.setValue(hero.max_mp)
        form.addRow("Max MP", self.max_mp)

        self.ac = QSpinBox()
        self.ac.setRange(0, 99)
        self.ac.setValue(hero.ac)
        form.addRow("AC", self.ac)

        self.speed = QSpinBox()
        self.speed.setRange(0, 200)
        self.speed.setValue(hero.speed)
        form.addRow("Speed", self.speed)

        self.gold = QSpinBox()
        self.gold.setRange(0, 999999)
        self.gold.setValue(hero.gold)
        form.addRow("Gold", self.gold)

        self.xp = QSpinBox()
        self.xp.setRange(0, 99999999)
        self.xp.setValue(hero.xp)
        form.addRow("XP", self.xp)

        layout.addLayout(form)

        self.notes = QTextEdit(hero.notes)
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

    def save(self):

        self.hero.name = self.name.text()
        self.hero.hero_class = self.hero_class.text()

        self.hero.level = self.level.value()

        self.hero.hp = self.hp.value()
        self.hero.max_hp = self.max_hp.value()

        self.hero.mp = self.mp.value()
        self.hero.max_mp = self.max_mp.value()

        self.hero.ac = self.ac.value()
        self.hero.speed = self.speed.value()

        self.hero.gold = self.gold.value()
        self.hero.xp = self.xp.value()

        self.hero.notes = self.notes.toPlainText()

        self.accept()