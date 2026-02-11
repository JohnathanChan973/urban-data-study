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

# def test_build_chunk_select_clause():
#     pass

# def test_quote_field_name():
#     pass
    