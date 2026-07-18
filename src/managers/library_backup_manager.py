from pathlib import Path
import zipfile

from src.database.archive_utils import safe_extract_zip


class LibraryBackupManager:

    LIBRARY_FOLDER = Path("library")

    @classmethod
    def export_library(cls, dest_zip_path):

        dest_zip_path = Path(dest_zip_path)
        project_root = cls.LIBRARY_FOLDER.parent

        with zipfile.ZipFile(dest_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:

            for file in cls.LIBRARY_FOLDER.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(project_root))

    @classmethod
    def import_library(cls, zip_path):

        # Merges into the existing library rather than replacing it - files
        # with matching relative paths are overwritten, everything else is
        # left alone, so importing a friend's library adds to/tops up yours
        # instead of wiping it out.
        zip_path = Path(zip_path)
        project_root = cls.LIBRARY_FOLDER.parent

        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract_zip(zf, project_root)
