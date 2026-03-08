from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from Backend.app.config import OUTPUT_DIR, PROJECT_DIR, SCHEMA_TEMPLATE
from Backend.app.services.files import cleanup_resume_artifacts, save_json_output, save_upload
from Backend.app.services.parser import extract_both_resume_results


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
            structured_results = extract_both_resume_results(saved_file)
            json_file = save_json_output(saved_file, structured_results)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return JSONResponse(
            content={
                "message": "Resume parsed successfully with direct extraction and AI-powered RAG output.",
                "filename": saved_file.name,
                "output_file": json_file.name,
                "data": {key: value.model_dump() for key, value in structured_results.items()},
            }
        )

    @app.delete("/cleanup")
    def cleanup_files() -> dict[str, str]:
        cleanup_resume_artifacts()
        return {"message": "Resume and generated JSON files deleted successfully."}

    if OUTPUT_DIR.exists():
        app.mount("/", StaticFiles(directory=str(PROJECT_DIR / "Frontend"), html=True), name="frontend")

    return app
