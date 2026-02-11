from unittest.mock import patch, MagicMock
from socrata_interface.domain import Domain

def test_datasets_generator(mock_socrata_class):
    mock_client = mock_socrata_class.return_value
    mock_client.datasets.return_value = ["x5fx-4tmu", "devm-es8b", "em4n-zidu"]
    
    domain = Domain("data.weho.org")
    gen = domain.datasets_generator()
    
    results = list(gen) # Convert to list to check values
    assert len(results) == 3
    assert results[0] == "x5fx-4tmu"

def test_datasets_count():
    domain = Domain("data.weho.org")
    assert domain.city_datasets_count()

# @patch('socrata_interface.domain.Socrata') 
# def test_city_datasets_ids_fetches_and_caches(mock_socrata_class, tmp_path):
#     # mock_client = MagicMock()
#     # mock_socrata_class.return_value = mock_client
    
#     expected_data = ["x5fx-4tmu", "devm-es8b", "em4n-zidu"]
#     # mock_client.datasets.return_value = expected_data
    
#     domain = Domain("data.cityofnewyork.us")
#     domain.base = tmp_path / "base"
#     domain.logdir = domain.base / "logs"
#     result = domain.city_datasets_ids()
    
#     assert result == expected_data
#     # mock_socrata_class.assert_called_once_with(None)
#     # mock_client.datasets.assert_called_once()