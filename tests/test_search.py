from src.search import generate_queries


def test_queries_are_profile_driven_and_unique() -> None:
    queries = generate_queries(limit=10)
    assert queries
    assert len(queries) == len({query.casefold() for query in queries})
    assert any("Data Scientist" in query for query in queries)
