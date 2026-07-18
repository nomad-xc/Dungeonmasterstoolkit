from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QFileDialog,
)

from src.widgets.primary_button import PrimaryButton
from src.database.campaign_manager import CampaignManager
from src.database.current_campaign import CurrentCampaign
from src.managers.library_backup_manager import LibraryBackupManager


class CampaignPage(QWidget):

    campaignOpened = Signal(str)

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
        self.delete_button.clicked.connect(self.delete_campaign)
        layout.addWidget(self.delete_button)

        campaign_transfer_row = QHBoxLayout()

        self.export_campaign_button = QPushButton("Export Campaign")
        self.export_campaign_button.clicked.connect(self.export_campaign)
        campaign_transfer_row.addWidget(self.export_campaign_button)

        self.import_campaign_button = QPushButton("Import Campaign")
        self.import_campaign_button.clicked.connect(self.import_campaign)
        campaign_transfer_row.addWidget(self.import_campaign_button)

        layout.addLayout(campaign_transfer_row)

        library_transfer_row = QHBoxLayout()

        self.export_library_button = QPushButton("Export Library")
        self.export_library_button.clicked.connect(self.export_library)
        library_transfer_row.addWidget(self.export_library_button)

        self.import_library_button = QPushButton("Import Library")
        self.import_library_button.clicked.connect(self.import_library)
        library_transfer_row.addWidget(self.import_library_button)

        layout.addLayout(library_transfer_row)

        layout.addStretch()

        self.refresh_campaigns()

    def refresh_campaigns(self):

        self.campaign_list.clear()

        campaigns = CampaignManager.get_campaigns()

        for campaign in campaigns:

            item = QListWidgetItem(
                f"{campaign.name}\nCreated: {campaign.created}"
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

        self.campaignOpened.emit(name)

    def delete_campaign(self):

        item = self.campaign_list.currentItem()

        if item is None:
            return

        name = item.text().split("\n")[0]

        confirm = QMessageBox.question(
            self,
            "Delete Campaign",
            f"Delete campaign '{name}' and all of its data? This cannot be undone."
        )

        if confirm != QMessageBox.Yes:
            return

        CampaignManager.delete_campaign(name)

        if CurrentCampaign.loaded() and CurrentCampaign.name() == name:
            CurrentCampaign.unload()

        self.refresh_campaigns()

    def export_campaign(self):

        item = self.campaign_list.currentItem()

        if item is None:
            return

        name = item.text().split("\n")[0]

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Campaign",
            f"{name}.zip",
            "Zip Files (*.zip)"
        )

        if not path:
            return

        CampaignManager.export_campaign(name, path)

        QMessageBox.information(
            self,
            "Campaign Exported",
            f"'{name}' was exported to:\n{path}"
        )

    def import_campaign(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Campaign",
            "",
            "Zip Files (*.zip)"
        )

        if not path:
            return

        try:
            imported_name = CampaignManager.import_campaign(path)
        except (ValueError, KeyError) as e:
            QMessageBox.warning(self, "Import Failed", str(e))
            return

        if imported_name is None:
            QMessageBox.warning(self, "Import Failed", "That file doesn't look like a valid campaign export.")
            return

        self.refresh_campaigns()

        QMessageBox.information(
            self,
            "Campaign Imported",
            f"Imported as '{imported_name}'."
        )

    def export_library(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Library",
            "library.zip",
            "Zip Files (*.zip)"
        )

        if not path:
            return

        LibraryBackupManager.export_library(path)

        QMessageBox.information(
            self,
            "Library Exported",
            f"Library was exported to:\n{path}"
        )

    def import_library(self):

        confirm = QMessageBox.question(
            self,
            "Import Library",
            "This adds the imported monsters, maps, tokens and sounds to your "
            "current library, overwriting any of your own with the same name. "
            "Continue?"
        )

        if confirm != QMessageBox.Yes:
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Library",
            "",
            "Zip Files (*.zip)"
        )

        if not path:
            return

        try:
            LibraryBackupManager.import_library(path)
        except ValueError as e:
            QMessageBox.warning(self, "Import Failed", str(e))
            return

        QMessageBox.information(self, "Library Imported", "Library import complete.")