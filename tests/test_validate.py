from pathlib import Path

import pytest

from src.config import DEFAULT_PROFILE_PATH
from src.validate import ProfileValidationError, validate_profile


def test_profile_is_valid() -> None:
    assert validate_profile()["profile"]["id"] == "user_001"


def test_profile_rejects_mismatched_periods(tmp_path: Path) -> None:
    content = DEFAULT_PROFILE_PATH.read_text(encoding="utf-8").replace('end: "2027-09-30"\n      duration_months: 3\n\n  career_preferences', 'end: "2027-08-30"\n      duration_months: 3\n\n  career_preferences', 1)
    path = tmp_path / "profile.yaml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ProfileValidationError, match="must match"):
        validate_profile(path)
