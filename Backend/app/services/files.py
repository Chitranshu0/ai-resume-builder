import json
import shutil
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from Backend.app.config import ALLOWED_EXTENSIONS, OUTPUT_DIR, PDF_DIR
from Backend.app.schemas import ResumeSchema


def clear_previous_resume_data() -> None:
    for file_path in PDF_DIR.iterdir():
        if file_path.is_file():
            file_path.unlink()

    for file_path in OUTPUT_DIR.glob("*_structured.json"):
        if file_path.is_file():
            file_path.unlink()


def cleanup_resume_artifacts() -> None:
    clear_previous_resume_data()


def save_upload(file: UploadFile) -> Path:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported by the LangChain RAG pipeline.",
        )

    clear_previous_resume_data()
    destination = PDF_DIR / Path(file.filename).name
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination


def save_json_output(file_path: Path, payload: dict[str, ResumeSchema]) -> Path:
    json_output_path = OUTPUT_DIR / f"{file_path.stem}_structured.json"
    json_output_path.write_text(
        json.dumps(
            {key: value.model_dump() for key, value in payload.items()},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return json_output_path
