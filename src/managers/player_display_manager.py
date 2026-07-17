from pathlib import Path

from src.models.player_display import PlayerDisplay
from src.database.current_campaign import CurrentCampaign


class PlayerDisplayManager:

    FILENAME = "player_display.json"

    @staticmethod
    def display_file():

        if not CurrentCampaign.loaded():
            return None

        folder = CurrentCampaign.path() / "Saves"
        folder.mkdir(parents=True, exist_ok=True)

        return folder / PlayerDisplayManager.FILENAME

    @classmethod
    def load_display(cls):

        file = cls.display_file()

        if file is None:
            return PlayerDisplay()

        return PlayerDisplay.load(file)

    @classmethod
    def save_display(cls, display):

        file = cls.display_file()

        if file is None:
            return

        display.save(file)
