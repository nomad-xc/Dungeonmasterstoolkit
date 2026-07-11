from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QInputDialog,
)

from src.widgets.primary_button import PrimaryButton
from src.database.campaign_manager import CampaignManager


class CampaignPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Campaign Manager")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)
        layout.addSpacing(20)

        # New Campaign Button
        self.new_button = PrimaryButton("New Campaign")
        self.new_button.clicked.connect(self.new_campaign)
        layout.addWidget(self.new_button)

        # Open Campaign Button
        self.open_button = PrimaryButton("Open Campaign")
        layout.addWidget(self.open_button)

        # Delete Campaign Button
        self.delete_button = PrimaryButton("Delete Campaign")
        layout.addWidget(self.delete_button)

        layout.addStretch()

    def new_campaign(self):
        name, ok = QInputDialog.getText(
            self,
            "Create Campaign",
            "Campaign Name:"
        )

        if ok and name:
            CampaignManager.create_campaign(name)