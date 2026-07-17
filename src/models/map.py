from dataclasses import dataclass, asdict, fields
import json
from pathlib import Path


@dataclass
class Map:

    name: str

    category: str = ""
    path: str = ""
    notes: str = ""

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
