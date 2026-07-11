from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class Hero:

    name: str
    hero_class: str

    level: int = 1

    hp: int = 10
    max_hp: int = 10

    mp: int = 0
    max_mp: int = 0

    ac: int = 10
    speed: int = 30

    gold: int = 0
    xp: int = 0

    portrait: str = ""

    notes: str = ""

    inventory: list = None

    def __post_init__(self):

        if self.inventory is None:
            self.inventory = []

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

        return cls(**data)