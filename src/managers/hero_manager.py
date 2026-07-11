from importlib.metadata import files
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

        hero.save(cls.hero_folder())

        return hero

    @classmethod
    def save_hero(cls, hero):

        hero.save(cls.hero_folder())

    @classmethod
    def load_heroes(cls):

        folder = cls.hero_folder()

        print("--------------------------------")
        print("Current Campaign:", CurrentCampaign.name())
        print("Hero Folder:", folder)

        heroes = []

        if folder is None:
             print("No campaign loaded")
             return heroes

        files = list(folder.glob("*.json"))

    print("JSON Files:", files)

    for file in files:

        print("Loading:", file)

        hero = Hero.load(file)

        print("Loaded:", hero.name)

        heroes.append(hero)

    print("Heroes Loaded:", len(heroes))
    print("--------------------------------")

    return heroes

    @classmethod
    def delete_hero(cls, hero):

        file = cls.hero_folder() / f"{hero.name}.json"

        if file.exists():
            file.unlink()