from pathlib import Path

from src.database.current_campaign import CurrentCampaign


class StoryManager:

    FILENAME = "story.txt"

    @staticmethod
    def story_file():

        if not CurrentCampaign.loaded():
            return None

        folder = CurrentCampaign.path() / "Notes"
        folder.mkdir(parents=True, exist_ok=True)

        return folder / StoryManager.FILENAME

    @classmethod
    def load_story(cls):

        file = cls.story_file()

        if file is None or not file.exists():
            return ""

        return file.read_text()

    @classmethod
    def save_story(cls, text):

        file = cls.story_file()

        if file is None:
            return

        file.write_text(text)
