"""JSON Schema validation for MyCS profile and opportunity data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from .config import (
    DEFAULT_PROFILE_PATH,
    OPPORTUNITY_SCHEMA_PATH,
    PROFILE_SCHEMA_PATH,
    ConfigurationError,
    load_profile,
    load_yaml,
)


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


class ProfileValidationError(ValueError):
    """Raised when data does not comply with its schema."""

    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{item.path}: {item.message}" for item in issues))


def validate_data(data: dict[str, Any], schema_path: str | Path) -> list[ValidationIssue]:
    """Return sorted JSON Schema errors without printing or exiting."""
    schema = load_yaml(schema_path)
    try:
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except SchemaError as error:
        raise ConfigurationError(f"Invalid schema '{schema_path}': {error.message}") from error
    return [
        ValidationIssue(".".join(str(part) for part in error.absolute_path) or "<root>", error.message)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    ]


def validate_profile(
    profile_path: str | Path = DEFAULT_PROFILE_PATH,
    schema_path: str | Path = PROFILE_SCHEMA_PATH,
) -> dict[str, Any]:
    """Load, validate and return a profile; raise a useful error if invalid."""
    payload = load_profile(profile_path)
    issues = validate_data(payload, schema_path)
    _validate_profile_semantics(payload, issues)
    if issues:
        raise ProfileValidationError(issues)
    return payload


def validate_opportunity(opportunity: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a normalized opportunity payload."""
    issues = validate_data(opportunity, OPPORTUNITY_SCHEMA_PATH)
    if issues:
        raise ProfileValidationError(issues)
    return opportunity


def _validate_profile_semantics(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    profile = payload.get("profile", {})
    preferences = profile.get("internship_preferences", {})
    availability = profile.get("availability", {}).get("internship", {})
    target_period = preferences.get("target_period", {})
    if availability and target_period and availability != target_period:
        issues.append(ValidationIssue("profile.availability.internship", "must match internship_preferences.target_period"))
    for path, period in (("profile.availability.internship", availability), ("profile.internship_preferences.target_period", target_period)):
        try:
            if date.fromisoformat(period["start"]) > date.fromisoformat(period["end"]):
                issues.append(ValidationIssue(path, "start must be on or before end"))
        except (KeyError, TypeError, ValueError):
            continue


def main() -> int:
    """Provide a small command-line profile validation entry point."""
    try:
        validate_profile()
    except (ConfigurationError, ProfileValidationError) as error:
        print(f"Profile invalid: {error}")
        return 1
    print("Profile valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
