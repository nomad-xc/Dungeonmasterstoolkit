import shutil
from pathlib import Path

from PySide6.QtWidgets import QFileDialog


def pick_and_copy_portrait(parent, dest_folder):

    path, _ = QFileDialog.getOpenFileName(
        parent,
        "Choose Portrait",
        "",
        "Images (*.png *.jpg *.jpeg *.webp)"
    )

    if not path:
        return None

    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    dest = dest_folder / Path(path).name
    shutil.copy(path, dest)

    return str(dest)


def pick_and_copy_images(parent, dest_folder, title="Choose Images"):

    paths, _ = QFileDialog.getOpenFileNames(
        parent,
        title,
        "",
        "Images (*.png *.jpg *.jpeg *.webp)"
    )

    if not paths:
        return []

    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    copied = []

    for path in paths:
        dest = dest_folder / Path(path).name
        shutil.copy(path, dest)
        copied.append(str(dest))

    return copied
