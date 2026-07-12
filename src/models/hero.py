from dataclasses import dataclass, asdict, fields
import json
from pathlib import Path


@dataclass
class Hero:

    CONDITIONS = [
        "Burning", "Poisoned", "Frozen", "Blind",
        "Weak", "Stunned", "Fear", "Crippled",
    ]

    MAX_LEVEL = 5
    MAX_HP_CAP = 20
    MAX_ARMOUR_CAP = 20

    name: str
    hero_class: str

    race: str = ""

    level: int = 1

    hp: int = 10
    max_hp: int = 10

    mp: int = 0
    max_mp: int = 0

    base_armour: int = 10
    armour_bonus: int = 0

    weapon_bonus: int = 0
    trinket: str = ""

    speed: int = 30

    xp: int = 0

    portrait: str = ""

    notes: str = ""

    conditions: list = None

    is_dm: bool = False

    def __post_init__(self):

        if self.conditions is None:
            self.conditions = []

    @property
    def total_armour(self):
        return self.base_armour + self.armour_bonus

    def add_xp(self, amount):

        self.xp += amount

        while self.level < self.MAX_LEVEL:

            threshold = 10 * self.level

            if self.xp < threshold:
                break

            self.xp -= threshold
            self.level += 1

            self.max_hp = min(self.max_hp + 2, self.MAX_HP_CAP)
            self.hp = min(self.hp + 2, self.max_hp)

            self.base_armour = min(self.base_armour + 1, self.MAX_ARMOUR_CAP)

    def save(self, folder):

        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        file = folder / f"{self.name}.json"

        with open(file, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, file):

        with open(file, "r") as f:
            data = json.load(f)

        known = {f.name for f in fields(cls)}
        data = {k: v for k, v in data.items() if k in known}

        return cls(**data)
