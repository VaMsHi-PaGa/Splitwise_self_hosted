import os
import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_bill_image(file: UploadFile) -> str:
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return filename


def get_bill_path(filename: str) -> Path:
    return UPLOAD_DIR / filename
