"""Transparent deterministic scoring for MyCS opportunities."""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

from .config import DEFAULT_PROFILE_PATH
from .validate import validate_opportunity, validate_profile


def evaluate_opportunity(opportunity: dict[str, Any], profile_path: str | Path = DEFAULT_PROFILE_PATH) -> dict[str, Any]:
    """Score one validated opportunity against a profile on three independent axes."""
    profile = validate_profile(profile_path)["profile"]
    opportunity = validate_opportunity(opportunity)
    required_skills = opportunity["required_skills"]
    known_skills = _known_skills(profile)
    skill_gaps = [item["name"] for item in required_skills if _normalize(item["name"]) not in known_skills]
    match_score = _match_score(required_skills, known_skills)
    trajectory_score = _trajectory_score(opportunity, profile)
    constraint_fit, constraints = _constraint_fit(opportunity, profile)
    return {
        "match_score": match_score,
        "trajectory_score": trajectory_score,
        "constraint_fit": constraint_fit,
        "skill_gaps": skill_gaps,
        "covered_skills": [item["name"] for item in required_skills if item["name"] not in skill_gaps],
        "explanation": {
            "match": f"{len(required_skills) - len(skill_gaps)}/{len(required_skills)} required skills are currently covered." if required_skills else "No explicit required skills were extracted.",
            "trajectory": "Score based on target roles, trajectory domains and learning priorities.",
            "constraints": constraints,
        },
    }


def _known_skills(profile: dict[str, Any]) -> dict[str, int]:
    known: dict[str, int] = {}
    for category in profile["skills"].values():
        for skill in category:
            if skill["status"] in {"active", "learning"} and skill["level_score"] > 0:
                normalized = _normalize(skill["name"])
                known[normalized] = max(known.get(normalized, 0), skill["level_score"])
    return known


def _match_score(required_skills: list[dict[str, str]], known_skills: dict[str, int]) -> int:
    if not required_skills:
        return 0
    weights = {"required": 2, "preferred": 1}
    total_weight = sum(weights[item.get("importance", "required")] for item in required_skills)
    covered = sum(weights[item.get("importance", "required")] * known_skills.get(_normalize(item["name"]), 0) / 3 for item in required_skills)
    return round(100 * covered / total_weight)


def _trajectory_score(opportunity: dict[str, Any], profile: dict[str, Any]) -> int:
    text = _normalize(" ".join(filter(None, [opportunity["title"], opportunity["opportunity_type"], opportunity["description"]] + opportunity["domains"] + [item["name"] for item in opportunity["required_skills"]])))
    roles = [entry for group in profile["target_roles"].values() for entry in group]
    role_score = max((int(entry["priority"]) * 20 for entry in roles if _normalize(str(entry["role"])) in text), default=0)
    high = profile["learning_priorities"]["high"] + profile["opportunity_preferences"]["highly_valued"] + profile["career_trajectory"]["next"]
    medium = profile["career_trajectory"]["medium_term"] + profile["career_trajectory"]["long_term"]
    high_score = 100 * _hits(text, high) / max(1, len({_normalize(value) for value in high}))
    medium_score = 100 * _hits(text, medium) / max(1, len({_normalize(value) for value in medium}))
    return round(min(100, 0.50 * role_score + 0.35 * high_score + 0.15 * medium_score))


def _constraint_fit(opportunity: dict[str, Any], profile: dict[str, Any]) -> tuple[int, list[str]]:
    preferences = profile["internship_preferences"]
    period = preferences["target_period"]
    checks: list[tuple[bool | None, str]] = []
    checks.append((_period_matches(opportunity, period), "period"))
    checks.append((_location_matches(opportunity["location"], preferences["geographic_priority"]), "location"))
    checks.append((_mode_matches(opportunity["work_mode"], preferences["work_modes"]), "work mode"))
    checks.append((_funding_matches(opportunity["funding"], preferences["funding"]), "funding"))
    checks.append((_education_matches(opportunity["education_level"], profile["education"]["current"]["level"]), "education level"))
    known = [match for match, _ in checks if match is not None]
    score = round(100 * sum(known) / len(known)) if known else 0
    details = [f"{label}: {'compatible' if result else 'incompatible' if result is False else 'unknown'}" for result, label in checks]
    return score, details


def _period_matches(opportunity: dict[str, Any], target: dict[str, Any]) -> bool | None:
    if not opportunity["start_date"] and not opportunity["end_date"] and not opportunity["duration_months"]:
        return None
    start = date.fromisoformat(opportunity["start_date"] or target["start"])
    end = date.fromisoformat(opportunity["end_date"] or target["end"])
    target_start, target_end = date.fromisoformat(target["start"]), date.fromisoformat(target["end"])
    duration_ok = opportunity["duration_months"] is None or opportunity["duration_months"] == target["duration_months"]
    return start <= target_end and end >= target_start and duration_ok


def _location_matches(location: str | None, priorities: dict[str, list[str]]) -> bool | None:
    if not location:
        return None
    choices = [item for values in priorities.values() for item in values]
    normalized_location = _normalize(location)
    return any(
        any(alias in normalized_location for alias in _location_aliases(choice))
        for choice in choices
    )


def _mode_matches(work_mode: str | None, accepted: list[str]) -> bool | None:
    return None if work_mode in {None, "unknown"} else work_mode in accepted


def _funding_matches(funding: str | None, preferences: dict[str, list[str]]) -> bool | None:
    if not funding:
        return None
    value = _normalize(funding)
    acceptable = preferences["strongly_preferred"] + preferences["acceptable"]
    return any(_normalize(item) in value for item in acceptable)


def _education_matches(level: str | None, current_level: str) -> bool | None:
    if not level:
        return None
    return _normalize(level) in _normalize(current_level) or _normalize(current_level) in _normalize(level)


def _hits(text: str, candidates: list[str]) -> int:
    return sum(_normalize(candidate) in text for candidate in {_normalize(value) for value in candidates})


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", "".join(character for character in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(character))).strip()


def _location_aliases(location: str) -> set[str]:
    normalized = _normalize(location)
    aliases = {
        "allemagne": {"allemagne", "germany", "deutschland"},
        "etats-unis": {"etats-unis", "united states", "usa", "us", "america"},
        "afrique de l'ouest": {"afrique de l'ouest", "west africa"},
        "burkina faso": {"burkina faso"},
    }
    return aliases.get(normalized, {normalized})
