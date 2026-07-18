import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.ui.mainwindow import MainWindow
from src.ui.theme import load_stylesheet


app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet())
app.setWindowIcon(QIcon("assets/icon.png"))

window = MainWindow()
window.show()

app.exec()