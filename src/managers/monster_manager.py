from pathlib import Path

from src.models.monster import Monster


class MonsterManager:

    MONSTERS_FOLDER = Path("library/monsters")
    VILLAINS_FOLDER = Path("library/villains")

    @classmethod
    def folder_for_kind(cls, kind):

        folder = cls.VILLAINS_FOLDER if kind == "villain" else cls.MONSTERS_FOLDER
        folder.mkdir(parents=True, exist_ok=True)

        return folder

    @classmethod
    def create_monster(cls, name, kind="monster"):

        monster = Monster(name=name, kind=kind)
        cls.save_monster(monster)

        return monster

    @classmethod
    def save_monster(cls, monster):

        monster.save(cls.folder_for_kind(monster.kind))

    @classmethod
    def load_monsters(cls, kind=None):

        kinds = [kind] if kind is not None else ["monster", "villain"]

        monsters = []

        for k in kinds:

            for file in sorted(cls.folder_for_kind(k).glob("*.json")):
                try:
                    monsters.append(Monster.load(file))
                except Exception as e:
                    print(f"Failed to load {file}: {e}")

        return monsters

    @classmethod
    def delete_monster(cls, monster):

        file = cls.folder_for_kind(monster.kind) / f"{monster.name}.json"

        if file.exists():
            file.unlink()
