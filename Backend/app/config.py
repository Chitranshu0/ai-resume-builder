import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
PDF_DIR = BASE_DIR / "pdf"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_DIR = BASE_DIR / "prompts"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"

PDF_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_DIR / ".env")


def load_schema_template() -> dict[str, Any]:
    schema_path = OUTPUT_DIR / "schema.json"
    if not schema_path.exists():
        return {}
    return json.loads(schema_path.read_text(encoding="utf-8"))


SCHEMA_TEMPLATE = load_schema_template()
