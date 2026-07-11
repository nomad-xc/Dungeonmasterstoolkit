from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
)

from src.widgets.primary_button import PrimaryButton
from src.database.campaign_manager import CampaignManager
from src.database.current_campaign import CurrentCampaign


class CampaignPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Campaign Manager")
        title.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        self.campaign_list = QListWidget()
        layout.addWidget(self.campaign_list)

        self.new_button = PrimaryButton("New Campaign")
        self.new_button.clicked.connect(self.new_campaign)
        layout.addWidget(self.new_button)

        self.open_button = PrimaryButton("Open Campaign")
        self.open_button.clicked.connect(self.open_campaign)
        layout.addWidget(self.open_button)

        self.delete_button = PrimaryButton("Delete Campaign")
        layout.addWidget(self.delete_button)

        layout.addStretch()

        self.refresh_campaigns()

    def refresh_campaigns(self):

        self.campaign_list.clear()

        campaigns = CampaignManager.get_campaigns()

        for campaign in campaigns:

            item = QListWidgetItem(
                f"{campaign.name}\n"
                f"Created: {campaign.created}"
            )

            self.campaign_list.addItem(item)

    def new_campaign(self):

        name, ok = QInputDialog.getText(
            self,
            "Create Campaign",
            "Campaign Name:"
        )

        if ok and name:

            CampaignManager.create_campaign(name)

            self.refresh_campaigns()
    def open_campaign(self):

        item = self.campaign_list.currentItem()

        if item is None:
            return

        name = item.text().split("\n")[0]

        CurrentCampaign.load(name)

        print("Loaded:", CurrentCampaign.name())