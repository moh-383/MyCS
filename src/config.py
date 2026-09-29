"""Configuration paths and UTF-8 YAML loading for MyCS."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_PATH = PROJECT_ROOT / "profile.yaml"
PROFILE_SCHEMA_PATH = PROJECT_ROOT / "profile_schema.yaml"
OPPORTUNITY_SCHEMA_PATH = PROJECT_ROOT / "opportunity_schema.yaml"
DATA_DIRECTORY = PROJECT_ROOT / "data"
DEFAULT_DATABASE_PATH = DATA_DIRECTORY / "opportunities.db"


class ConfigurationError(ValueError):
    """Raised when a configuration file cannot be safely loaded."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a mapping from a UTF-8 YAML file."""
    yaml_path = Path(path)
    try:
        content = yaml_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigurationError(f"Unable to read '{yaml_path}': {error}") from error
    try:
        payload = yaml.safe_load(content)
    except yaml.YAMLError as error:
        raise ConfigurationError(f"Invalid YAML in '{yaml_path}': {error}") from error
    if not isinstance(payload, dict):
        raise ConfigurationError(f"'{yaml_path}' must contain a YAML mapping.")
    return payload


def load_profile(path: str | Path = DEFAULT_PROFILE_PATH) -> dict[str, Any]:
    """Load the profile wrapper as stored in ``profile.yaml``."""
    return load_yaml(path)
