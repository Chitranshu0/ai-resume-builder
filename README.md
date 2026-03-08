# ai-resume-builder
A LangChain and RAG based resume parser that connects a FastAPI backend and a browser frontend. Users upload a resume, the backend loads the document, splits it into chunks, embeds it, retrieves relevant context from Chroma, sends that context through a prompt template with ChatGroq, validates the result with Pydantic, and stores the final structured JSON output.

## Run
1. Install dependencies:
   `pip install -r requirements.txt`
2. Add `GROQ_API_KEY` to `.env`.
3. Start the app:
   `uvicorn Backend.main:app --reload`
4. Open:
   `http://127.0.0.1:8000`
