from dataclasses import dataclass, asdict, fields
import json
from pathlib import Path


@dataclass
class Monster:

    CREATURE_TYPES = [
        {
            "name": "Aberration",
            "description": "Utterly alien beings with strange anatomies, bizarre psionic powers, and incomprehensible minds.",
            "examples": "Mind Flayers, Beholders",
        },
        {
            "name": "Beast",
            "description": "Natural or giant animals, dinosaurs, and mundane creatures.",
            "examples": "Wolves, Giant Eagles",
        },
        {
            "name": "Celestial",
            "description": "Divine, holy beings native to the Upper Planes.",
            "examples": "Angels, Pegasi",
        },
        {
            "name": "Construct",
            "description": "Artificial beings created through magic or technology.",
            "examples": "Golems, Animated Armor",
        },
        {
            "name": "Dragon",
            "description": "Large, winged, reptilian creatures known for their elemental breath and hoards.",
            "examples": "Chromatic and Metallic Dragons",
        },
        {
            "name": "Elemental",
            "description": "Beings made of raw, elemental matter or energy native to the Inner Planes.",
            "examples": "Fire Elementals, Djinn",
        },
        {
            "name": "Fey",
            "description": "Magical creatures intimately tied to the forces of nature, emotion, and the Feywild.",
            "examples": "Dryads, Satyrs",
        },
        {
            "name": "Fiend",
            "description": "Creatures of pure evil native to the Lower Planes.",
            "examples": "Devils, Demons",
        },
        {
            "name": "Giant",
            "description": "Massive, humanoid-shaped creatures of incredible strength.",
            "examples": "Hill Giants, Cloud Giants",
        },
        {
            "name": "Humanoid",
            "description": "The civilized, main playable races and their NPC counterparts.",
            "examples": "Humans, Elves, Goblins",
        },
        {
            "name": "Monstrosity",
            "description": "Frightening, unnatural creatures that do not fit the magical criteria of fey or fiends.",
            "examples": "Minotaurs, Medusas",
        },
        {
            "name": "Ooze",
            "description": "Amorphous, gelatinous creatures that typically lurk in dungeons.",
            "examples": "Gelatinous Cubes",
        },
        {
            "name": "Plant",
            "description": "Vegetable creatures and sentient flora.",
            "examples": "Treants, Shambling Mounds",
        },
        {
            "name": "Undead",
            "description": "Once-living creatures animated by dark magic or necromancy.",
            "examples": "Vampires, Zombies",
        },
    ]

    name: str

    kind: str = "monster"
    creature_type: str = ""

    hp: int = 10
    max_hp: int = 10

    ac: int = 10
    speed: int = 30

    xp: int = 0

    portrait: str = ""
    sound: str = ""

    description: str = ""
    abilities: str = ""
    behavior: str = ""
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
