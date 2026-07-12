import shutil
from pathlib import Path

from PySide6.QtWidgets import QFileDialog


def pick_and_copy_portrait(parent, dest_folder):

    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Choose Portrait",
        "",
        "Images (*.png *.jpg *.jpeg)"
    )

    if not path:
        return None

    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    dest = dest_folder / Path(path).name
    shutil.copy(path, dest)

    return str(dest)
