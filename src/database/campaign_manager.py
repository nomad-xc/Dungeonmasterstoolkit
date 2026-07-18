from pathlib import Path
import json
import shutil
import zipfile
import tempfile
from datetime import datetime

from src.models.campaign_info import CampaignInfo
from src.database.archive_utils import safe_extract_zip


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

    @classmethod
    def export_campaign(cls, name, dest_zip_path):

        folder = cls.CAMPAIGN_FOLDER / name
        dest_zip_path = Path(dest_zip_path)

        with zipfile.ZipFile(dest_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

            for file in folder.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(cls.CAMPAIGN_FOLDER))

    @classmethod
    def import_campaign(cls, zip_path):

        zip_path = Path(zip_path)

        with zipfile.ZipFile(zip_path, "r") as zf:

            names = zf.namelist()

            if not names:
                return None

            top_level = names[0].split("/")[0]

            dest_name = top_level
            counter = 2

            while (cls.CAMPAIGN_FOLDER / dest_name).exists():
                dest_name = f"{top_level} ({counter})"
                counter += 1

            if dest_name == top_level:
                safe_extract_zip(zf, cls.CAMPAIGN_FOLDER)
            else:
                with tempfile.TemporaryDirectory() as tmp:
                    safe_extract_zip(zf, tmp)
                    shutil.move(str(Path(tmp) / top_level), str(cls.CAMPAIGN_FOLDER / dest_name))

        return dest_name