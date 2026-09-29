from src.extract import normalize_opportunity
from src.store import OpportunityStore


def test_store_creates_parent_and_deduplicates_by_url(tmp_path) -> None:
    store = OpportunityStore(tmp_path / "nested" / "opportunities.db")
    opportunity = normalize_opportunity({
        "title": "Data Internship", "organization": "Example", "url": "https://example.org/job",
    })
    first_id = store.upsert(opportunity)
    opportunity["title"] = "Updated Data Internship"
    assert store.upsert(opportunity) == first_id
    assert store.get_by_url(opportunity["url"])["title"] == "Updated Data Internship"
    assert len(store.list_recent()) == 1
