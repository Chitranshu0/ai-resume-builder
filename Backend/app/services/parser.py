import json
import os
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import Docx2txtLoader, PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter

from Backend.app.config import EMBEDDING_MODEL, GROQ_MODEL, PROMPT_DIR, SCHEMA_TEMPLATE
from Backend.app.schemas import ResumeSchema


def load_prompt_template() -> PromptTemplate:
    prompt_text = (PROMPT_DIR / "resume_extraction_prompt.txt").read_text(encoding="utf-8")
    return PromptTemplate(
        template=prompt_text,
        input_variables=["context", "question"],
        partial_variables={"schema": json.dumps(SCHEMA_TEMPLATE, indent=2)},
    )


def load_document(file_path: Path) -> list[Any]:
    if file_path.suffix.lower() == ".pdf":
        return PyMuPDFLoader(str(file_path)).load()
    if file_path.suffix.lower() == ".docx":
        return Docx2txtLoader(str(file_path)).load()
    raise RuntimeError(f"Unsupported file type: {file_path.suffix}")


def split_documents(file_path: Path) -> list[Any]:
    documents = load_document(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=1200)
    return text_splitter.split_documents(documents)


def build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY2") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY or GROQ_API_KEY2 in .env.")
    return ChatGroq(model=GROQ_MODEL, api_key=api_key, temperature=0)


def extract_json_from_text(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("RAG response did not return a valid JSON object.")
    return json.loads(text[start : end + 1])


def extract_resume_data_with_rag(file_path: Path) -> ResumeSchema:
    docs = split_documents(file_path)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    llm = build_llm()
    prompt = load_prompt_template()
    query = (
        "Extract all resume details into the exact JSON schema. Include personal_info, "
        "career_objective, education, skills, certifications, internships, projects, "
        "achievements, positions_of_responsibility, research_work, languages_known, and interests."
    )

    vectordb = Chroma.from_documents(documents=docs, embedding=embeddings)
    try:
        retriever = vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.25},
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )
        result = qa_chain.invoke({"query": query})
    finally:
        if hasattr(vectordb, "_client"):
            try:
                vectordb._client.clear_system_cache()
            except Exception:
                pass

    parsed_json = extract_json_from_text(result["result"])
    return ResumeSchema.model_validate(parsed_json)
