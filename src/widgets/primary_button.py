from PySide6.QtWidgets import QPushButton


class PrimaryButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)

        self.setMinimumHeight(44)

        self.setStyleSheet("""
            QPushButton {

                background:#8b5a2b;

                color:white;

                border:none;

                border-radius:8px;

                font-size:14px;

                font-weight:bold;

            }

            QPushButton:hover{

                background:#a66b33;

            }

            QPushButton:pressed{

                background:#6d4420;

            }
        """)