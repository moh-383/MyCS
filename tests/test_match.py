from src.extract import normalize_opportunity
from src.match import evaluate_opportunity


def test_scoring_identifies_gap_and_scores_axes() -> None:
    opportunity = normalize_opportunity({
        "title": "Machine Learning Engineer Internship",
        "organization": "Example Lab",
        "url": "https://example.org/internship",
        "location": "Germany",
        "work_mode": "hybrid",
        "start_date": "2027-07-01",
        "end_date": "2027-09-30",
        "duration_months": 3,
        "funding": "stipend",
        "required_skills": ["Python", "PyTorch"],
        "domains": ["Machine Learning"],
    })
    result = evaluate_opportunity(opportunity)
    assert result["match_score"] == 50
    assert result["trajectory_score"] > 0
    assert result["constraint_fit"] == 100
    assert result["skill_gaps"] == ["PyTorch"]
