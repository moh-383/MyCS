"""Deterministic normalization of externally collected opportunities."""

from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlparse

from .validate import validate_opportunity

_KEYWORDS = {
    "Python", "R", "SQL", "PyTorch", "Docker", "Linux", "Django", "Machine Learning",
    "Deep Learning", "Computer Vision", "Data Science", "Data Engineering", "Statistics",
    "Robotics", "ROS2", "MLOps", "Git", "Excel",
}


class ExtractionError(ValueError):
    """Raised when mandatory source fields cannot form an opportunity."""


def normalize_opportunity(raw: dict[str, Any], source: str | None = None) -> dict[str, Any]:
    """Normalize a collected record and never infer unavailable factual fields."""
    title = _required_text(raw, "title")
    organization = _required_text(raw, "organization")
    url = _required_text(raw, "url")
    if not urlparse(url).scheme or not urlparse(url).netloc:
        raise ExtractionError("url must be an absolute HTTP(S) URL")
    description = _optional_text(raw.get("description"))
    skills = raw.get("required_skills") or _extract_skills(description or "")
    normalized = {
        "title": title,
        "organization": organization,
        "url": url,
        "source": source or _optional_text(raw.get("source")) or urlparse(url).netloc,
        "opportunity_type": _optional_text(raw.get("opportunity_type")) or "Opportunity",
        "location": _optional_text(raw.get("location")),
        "work_mode": _enum_or_unknown(raw.get("work_mode"), {"onsite", "hybrid", "remote"}),
        "start_date": _iso_date(raw.get("start_date")),
        "end_date": _iso_date(raw.get("end_date")),
        "duration_months": _positive_int_or_none(raw.get("duration_months")),
        "deadline": _iso_date(raw.get("deadline")),
        "education_level": _optional_text(raw.get("education_level")),
        "funding": _optional_text(raw.get("funding")),
        "domains": _string_list(raw.get("domains", [])),
        "required_skills": _normalize_skills(skills),
        "description": description,
    }
    return validate_opportunity(normalized)


def _required_text(raw: dict[str, Any], key: str) -> str:
    value = _optional_text(raw.get(key))
    if value is None:
        raise ExtractionError(f"Missing required field: {key}")
    return value


def _optional_text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _iso_date(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ExtractionError("dates must use ISO format YYYY-MM-DD")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise ExtractionError(f"Invalid ISO date: {value}") from error


def _positive_int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ExtractionError("duration_months must be a positive integer")
    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ExtractionError("domains must be a list of non-empty strings")
    return list(dict.fromkeys(item.strip() for item in value))


def _enum_or_unknown(value: Any, allowed: set[str]) -> str:
    return value.casefold() if isinstance(value, str) and value.casefold() in allowed else "unknown"


def _normalize_skills(skills: Any) -> list[dict[str, str]]:
    if not isinstance(skills, list):
        raise ExtractionError("required_skills must be a list")
    normalized: list[dict[str, str]] = []
    for item in skills:
        if isinstance(item, str):
            name, importance = item, "required"
        elif isinstance(item, dict):
            name, importance = item.get("name"), item.get("importance", "required")
        else:
            raise ExtractionError("each required skill must be a string or mapping")
        text = _optional_text(name)
        if text is None or importance not in {"required", "preferred"}:
            raise ExtractionError("invalid required skill")
        if text.casefold() not in {entry["name"].casefold() for entry in normalized}:
            normalized.append({"name": text, "importance": importance})
    return normalized


def _extract_skills(description: str) -> list[dict[str, str]]:
    text = description.casefold()
    return [{"name": skill, "importance": "required"} for skill in sorted(_KEYWORDS) if skill.casefold() in text]
