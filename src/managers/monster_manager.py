from pathlib import Path

from src.models.monster import Monster


class MonsterManager:

    FOLDER = Path("library/monsters")

    @classmethod
    def folder(cls):
        cls.FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.FOLDER

    @classmethod
    def create_monster(cls, name):

        monster = Monster(name=name)
        cls.save_monster(monster)

        return monster

    @classmethod
    def save_monster(cls, monster):

        monster.save(cls.folder())

    @classmethod
    def load_monsters(cls):

        monsters = []

        for file in sorted(cls.folder().glob("*.json")):
            try:
                monsters.append(Monster.load(file))
            except Exception as e:
                print(f"Failed to load {file}: {e}")

        return monsters

    @classmethod
    def delete_monster(cls, monster):

        file = cls.folder() / f"{monster.name}.json"

        if file.exists():
            file.unlink()
