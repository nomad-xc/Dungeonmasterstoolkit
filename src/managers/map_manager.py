import json
from pathlib import Path

from src.models.map import Map


class MapManager:

    MAPS_FOLDER = Path("library/maps")
    IMAGES_FOLDER = Path("library/maps/images")
    FOLDERS_FILE = Path("library/map_folders.json")

    @classmethod
    def images_folder(cls):
        cls.IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.IMAGES_FOLDER

    @classmethod
    def load_folders(cls):

        if not cls.FOLDERS_FILE.exists():
            return []

        with open(cls.FOLDERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save_folders(cls, folders):

        cls.FOLDERS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(cls.FOLDERS_FILE, "w") as f:
            json.dump(folders, f, indent=4)

    @classmethod
    def create_folder(cls, name):

        folders = cls.load_folders()

        if name and name not in folders:
            folders.append(name)
            cls.save_folders(folders)

        return folders

    @classmethod
    def create_map(cls, name, path, category=""):

        map_obj = Map(name=name, path=path, category=category)
        cls.save_map(map_obj)

        return map_obj

    @classmethod
    def save_map(cls, map_obj):

        cls.MAPS_FOLDER.mkdir(parents=True, exist_ok=True)
        map_obj.save(cls.MAPS_FOLDER)

    @classmethod
    def load_maps(cls):

        cls.MAPS_FOLDER.mkdir(parents=True, exist_ok=True)

        maps = []

        for file in sorted(cls.MAPS_FOLDER.glob("*.json")):
            try:
                maps.append(Map.load(file))
            except Exception as e:
                print(f"Failed to load {file}: {e}")

        return maps

    @classmethod
    def delete_map(cls, map_obj):

        file = cls.MAPS_FOLDER / f"{map_obj.name}.json"

        if file.exists():
            file.unlink()
