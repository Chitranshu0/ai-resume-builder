from typing import Any

from pydantic import BaseModel, Field, field_validator


class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


class EducationItem(BaseModel):
    degree: str = ""
    year: str = ""
    institute: str = ""
    board: str = ""
    score: str = ""


class Skills(BaseModel):
    programming_languages: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    libraries_frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class InternshipItem(BaseModel):
    company: str = ""
    role: str = ""
    description: str = ""


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    github_link: str = ""


class Projects(BaseModel):
    project1: ProjectItem = Field(default_factory=ProjectItem)
    project2: ProjectItem = Field(default_factory=ProjectItem)


class ResumeSchema(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    career_objective: str = ""
    education: list[EducationItem] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: list[str] = Field(default_factory=list)
    internships: list[InternshipItem] = Field(default_factory=list)
    projects: Projects = Field(default_factory=Projects)
    achievements: list[str] = Field(default_factory=list)
    positions_of_responsibility: list[str] = Field(default_factory=list)
    research_work: list[str] = Field(default_factory=list)
    languages_known: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    @field_validator(
        "certifications",
        "achievements",
        "positions_of_responsibility",
        "research_work",
        "languages_known",
        "interests",
        mode="before",
    )
    @classmethod
    def normalize_string_lists(cls, value: Any) -> list[str]:
        def flatten_item(item: Any) -> str:
            if item is None:
                return ""
            if isinstance(item, str):
                return item.strip()
            if isinstance(item, list):
                parts = [flatten_item(part) for part in item]
                return "; ".join(part for part in parts if part)
            if isinstance(item, dict):
                parts = [flatten_item(part) for part in item.values()]
                return " - ".join(part for part in parts if part)
            return str(item).strip()

        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]

        normalized_items: list[str] = []
        for item in value:
            text = flatten_item(item)
            if text:
                normalized_items.append(text)

        return normalized_items
