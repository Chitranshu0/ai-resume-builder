from pathlib import Path
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "pdf"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}

PDF_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Resume Loader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"message": "Resume Loader API is running"}


@app.get("/documents")
def list_documents() -> dict:
    files = sorted(
        [
            {
                "name": file.name,
                "size": file.stat().st_size,
            }
            for file in PDF_DIR.iterdir()
            if file.is_file()
        ],
        key=lambda item: item["name"].lower(),
    )
    return {"documents": files}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed.",
        )

    destination = PDF_DIR / Path(file.filename).name
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully.",
        "filename": destination.name,
        "saved_to": str(destination),
    }

# Serve static frontend files
app.mount("/", StaticFiles(directory=str(BASE_DIR.parent / "Frontend"), html=True), name="frontend")
