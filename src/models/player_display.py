from dataclasses import dataclass, asdict, field
import json
from pathlib import Path


@dataclass
class PlayerDisplay:

    backdrop_image: str = ""

    background_map: str = ""
    background_x: float = 0
    background_y: float = 0
    background_width: float = 0
    background_height: float = 0
    background_rotation: float = 0
    background_locked: bool = False

    widgets: list = field(default_factory=list)

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
            "backdrop_image",
            "background_map", "background_x", "background_y",
            "background_width", "background_height", "background_rotation",
            "background_locked", "widgets",
        }
        data = {k: v for k, v in data.items() if k in known}

        return cls(**data)
