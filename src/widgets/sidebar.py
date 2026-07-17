from PySide6.QtWidgets import QListWidget


class Sidebar(QListWidget):

    HOME_MENU = [
        "Campaigns",
        "Library",
    ]

    CAMPAIGN_MENU = [
        "Campaigns",
        "Library",
        "",
        "Heroes",
        "Session",
        "Gameplay",
        "Player Display",
        "Settings",
    ]

    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)

        self.show_home()

    def show_home(self):

        self.clear()

        for item in self.HOME_MENU:
            self.addItem(item)

    def show_campaign(self, campaign_name):

        self.clear()

        for item in self.CAMPAIGN_MENU:

            self.addItem(item)

        self.addItem("")
        self.addItem("Current Campaign")
        self.addItem(campaign_name)