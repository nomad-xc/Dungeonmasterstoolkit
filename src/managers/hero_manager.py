from pathlib import Path

from src.models.hero import Hero
from src.database.current_campaign import CurrentCampaign


class HeroManager:

    @staticmethod
    def hero_folder():

        if not CurrentCampaign.loaded():
            return None

        folder = CurrentCampaign.path() / "heroes"
        folder.mkdir(parents=True, exist_ok=True)

        return folder

    @classmethod
    def create_hero(cls, name, hero_class):

        hero = Hero(
            name=name,
            hero_class=hero_class
        )

        cls.save_hero(hero)

        return hero

    @classmethod
    def save_hero(cls, hero):

        folder = cls.hero_folder()

        if folder is None:
            return

        hero.save(folder)

    @classmethod
    def load_heroes(cls):

        folder = cls.hero_folder()

        if folder is None:
            return []

        heroes = []

        for file in sorted(folder.glob("*.json")):
            try:
                hero = Hero.load(file)
                heroes.append(hero)
            except Exception as e:
                print(f"Failed to load {file}: {e}")

        return heroes

    @classmethod
    def delete_hero(cls, hero):

        folder = cls.hero_folder()

        if folder is None:
            return

        file = folder / f"{hero.name}.json"

        if file.exists():
            file.unlink()