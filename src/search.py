"""Profile-driven search-query generation without external crawling."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .config import DEFAULT_PROFILE_PATH
from .validate import validate_profile


def generate_queries(profile_path: str | Path = DEFAULT_PROFILE_PATH, limit: int = 30) -> list[str]:
    """Build stable, de-duplicated opportunity queries from a validated profile."""
    if limit < 1:
        raise ValueError("limit must be greater than zero")
    profile = validate_profile(profile_path)["profile"]
    roles = _role_names(profile["target_roles"])
    priorities = profile["learning_priorities"]["high"] + profile["opportunity_preferences"]["highly_valued"]
    locations = _search_locations(profile["internship_preferences"]["geographic_priority"])
    opportunity_types = profile["internship_preferences"]["opportunity_types"]
    queries: list[str] = []
    for role in roles:
        queries.append(f'"{role}" internship 2027')
        for skill in priorities[:4]:
            queries.append(f'"{role}" "{skill}" internship 2027')
        for location in locations:
            queries.append(f'"{role}" internship "{location}" 2027')
    for opportunity_type in opportunity_types:
        for skill in priorities[:3]:
            queries.append(f'"{opportunity_type}" "{skill}" 2027')
    return _unique(queries)[:limit]


def _role_names(target_roles: dict[str, list[dict[str, object]]]) -> list[str]:
    roles = [entry["role"] for group in target_roles.values() for entry in group]
    return [str(role) for role in roles]


def _search_locations(priority: dict[str, list[str]]) -> list[str]:
    keys = ("preferred_country", "tier_1", "tier_2", "tier_3", "tier_4")
    return [location for key in keys for location in priority.get(key, [])]


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    return [value for value in values if not (value.casefold() in seen or seen.add(value.casefold()))]
