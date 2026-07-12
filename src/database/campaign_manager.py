from pathlib import Path
import json
import shutil
from datetime import datetime

from src.models.campaign_info import CampaignInfo


class CampaignManager:

    CAMPAIGN_FOLDER = Path("campaigns")

    @classmethod
    def create_campaign(cls, name):

        folder = cls.CAMPAIGN_FOLDER / name

        folder.mkdir(parents=True, exist_ok=True)

        for subfolder in [
            "heroes",
            "Maps",
            "Scenes",
            "Saves",
            "Notes",
            "Images",
        ]:
            (folder / subfolder).mkdir(exist_ok=True)

        campaign = {
            "name": name,
            "version": "0.4 Alpha",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_opened": ""
        }

        with open(folder / "campaign.json", "w") as file:
            json.dump(campaign, file, indent=4)

    @classmethod
    def get_campaigns(cls):

        campaigns = []

        if not cls.CAMPAIGN_FOLDER.exists():
            return campaigns

        for folder in cls.CAMPAIGN_FOLDER.iterdir():

            if not folder.is_dir():
                continue

            info = folder / "campaign.json"

            if not info.exists():
                continue

            with open(info) as file:

                data = json.load(file)

            campaigns.append(CampaignInfo(**data))

        campaigns.sort(key=lambda c: c.name)

        return campaigns

    @classmethod
    def delete_campaign(cls, name):

        folder = cls.CAMPAIGN_FOLDER / name

        if folder.exists():
            shutil.rmtree(folder)