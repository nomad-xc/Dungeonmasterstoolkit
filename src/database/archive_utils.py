from pathlib import Path


def safe_extract_zip(zf, dest_root):

    dest_root = Path(dest_root).resolve()

    members = zf.infolist()

    for member in members:

        target = (dest_root / member.filename).resolve()

        try:
            target.relative_to(dest_root)
        except ValueError:
            raise ValueError(f"Refusing to extract unsafe archive entry: {member.filename}")

    zf.extractall(dest_root)
