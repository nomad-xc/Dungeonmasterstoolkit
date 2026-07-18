from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class AutoSounds:

    monster_hit: str = ""
    monster_dead: str = ""

    hero_hit: str = ""
    hero_heal: str = ""
    hero_death_male: str = ""
    hero_death_female: str = ""

    level_up: str = ""
    miss: str = ""

    def save(self, file):

        file = Path(file)
        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def load(cls, file):

        file = Path(file)

        if not file.exists():
            return cls()

        with open(file, "r") as f:
            data = json.load(f)

        known = {
            "monster_hit", "monster_dead",
            "hero_hit", "hero_heal", "hero_death_male", "hero_death_female",
            "level_up", "miss",
        }
        data = {k: v for k, v in data.items() if k in known}

        return cls(**data)
