from unittest.mock import patch, MagicMock
from socrata_interface.domain import Domain

# def test_datasets_generator(mock_socrata_class):
#     mock_client = mock_socrata_class.return_value
#     mock_client.datasets.return_value = ["x5fx-4tmu", "devm-es8b", "em4n-zidu"]
    
#     domain = Domain("data.weho.org")
#     gen = domain.datasets_generator()
    
#     results = list(gen) # Convert to list to check values
#     assert len(results) == 3
#     assert results[0] == "x5fx-4tmu"

# def test_datasets_count():
#     domain = Domain("data.weho.org")
#     assert domain.city_datasets_count()
    
# def test_city_datasets_ids():
#     pass

# def test_dataset():
#     pass

# def test_metadata():
#     pass

# def test_select():
#     pass

# def test_row_counts():
#     pass

# def test_null_counts():
#     pass

TEST1 = "@TEST"
TEST2 = TEST1[1:]

def test_build_chunk_select_clause():
    domain = Domain("data.weho.org")
    quoted = f"`{TEST1}`"
    with patch.object(domain, "_quote_field_name", return_value = quoted):
        test1 = domain._build_chunk_select_clause(f"{TEST1}", "url")    
    expected1 = f"(count(*) - count({quoted})) AS _{TEST2}_nulls, sum(CASE WHEN {quoted} IS NULL OR trim({quoted}) = '' THEN 1 ELSE 0 END) AS _{TEST2}_semantic_nulls"
    assert test1 == expected1

    with patch.object(domain, "_quote_field_name", return_value = TEST2):
        test2 = domain._build_chunk_select_clause(f"{TEST2}", "number")
    expected2 = f"(count(*) - count({TEST2})) AS {TEST2}_nulls"
    assert test2 == expected2

def test_quote_field_name():
    domain = Domain("data.weho.org")
    quoted = domain._quote_field_name(TEST1)
    no_quotes = domain._quote_field_name(TEST2)

    assert '`' in quoted
    assert '`' not in no_quotes
