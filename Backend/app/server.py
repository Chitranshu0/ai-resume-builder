from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from Backend.app.config import OUTPUT_DIR, PROJECT_DIR, SCHEMA_TEMPLATE
from Backend.app.services.files import (
    list_generated_outputs,
    list_uploaded_documents,
    save_json_output,
    save_upload,
)
from Backend.app.services.parser import extract_resume_data_with_rag


def create_app() -> FastAPI:
    app = FastAPI(title="Resume Loader API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"message": "Resume Loader API is running"}

    @app.get("/documents")
    def list_documents() -> dict[str, list[dict[str, Any]]]:
        return {"documents": list_uploaded_documents()}

    @app.get("/outputs")
    def list_outputs() -> dict[str, list[dict[str, Any]]]:
        return {"outputs": list_generated_outputs()}

    @app.get("/schema")
    def get_schema() -> dict[str, Any]:
        return SCHEMA_TEMPLATE

    @app.post("/upload")
    async def upload_document(file: UploadFile = File(...)) -> dict[str, str]:
        destination = save_upload(file)
        return {
            "message": "File uploaded successfully.",
            "filename": destination.name,
            "saved_to": str(destination),
        }

    @app.post("/parse-resume")
    async def parse_resume(file: UploadFile = File(...)) -> JSONResponse:
        try:
            saved_file = save_upload(file)
            structured_resume = extract_resume_data_with_rag(saved_file)
            json_file = save_json_output(saved_file, structured_resume)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return JSONResponse(
            content={
                "message": "Resume parsed successfully with LangChain RAG.",
                "filename": saved_file.name,
                "output_file": json_file.name,
                "data": structured_resume.model_dump(),
            }
        )

    if OUTPUT_DIR.exists():
        app.mount("/", StaticFiles(directory=str(PROJECT_DIR / "Frontend"), html=True), name="frontend")

    return app
