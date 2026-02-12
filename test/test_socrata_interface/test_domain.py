from unittest.mock import patch, MagicMock
from socrata_interface.domain import Domain
import pytest

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_datasets_generator_logic(mock_setup_logger, mock_socrata_class):
    mock_client = MagicMock()
    mock_socrata_class.return_value = mock_client
    
    # Simulate the API returning a list of IDs
    mock_client.datasets.return_value = ["id_1", "id_2", "id_3"]
    
    domain = Domain("test.org")
    results = list(domain.datasets_generator())
    
    # 3. verify the API response
    assert results == ["id_1", "id_2", "id_3"]

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_datasets_count(mock_setup_logger, mock_socrata_class):
    mock_client = MagicMock()
    mock_socrata_class.return_value = mock_client
    
    # Simulate the API returning a list of IDs
    mock_client.datasets.return_value = ["id_1", "id_2", "id_3"]
    
    domain = Domain("test.org")

    assert domain.city_datasets_count() == 3
    
@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_city_datasets_ids(mock_setup_logger, mock_socrata_class):
    # Setup the mock to return nested dictionaries
    mock_client = MagicMock()
    mock_socrata_class.return_value = mock_client
    mock_client.datasets.return_value = [
        {"resource": {"id": "abc-123"}},
        {"resource": {"id": "def-456"}},
        {'resource': {'name': 'NOPD Use of Force Incidents',
   'id': '9mnw-mbde',
   'resource_name': None}}
    ]
    
    domain = Domain("test.org")
    ids = list(domain.city_datasets_ids())
    
    assert ids == ["abc-123", "def-456", "9mnw-mbde"]

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_dataset(mock_setup_logger, mock_socrata_class):
    mock_client = MagicMock()
    mock_socrata_class.return_value = mock_client
    mock_client.get.return_value = [{'service_request': '2021-847416',
  'geocoded_column': {'latitude': '0.0', 'longitude': '0.0'}}]
    
    domain = Domain("test.org")
    data = list(domain.dataset("test"))

    assert len(data) == 1

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_metadata(mock_setup_logger, mock_socrata_class):
    mock_client = MagicMock()
    mock_socrata_class.return_value = mock_client
    mock_client.get_metadata.return_value = {'id': '9mnw-mbde',
 'name': 'NOPD Use of Force Incidents',
 'columns': [{'id': 550825285,
   'name': 'PIB File Number',
   'dataTypeName': 'text',
   'fieldName': 'pib_file_number',
   'position': 1,
   'renderTypeName': 'text',
   'tableColumnId': 37647720,
   'width': 208},
  {'id': 550825317,
   'name': 'Officer Injured',
   'dataTypeName': 'text',
   'description': '',
   'fieldName': 'officer_injured',
   'position': 33,
   'renderTypeName': 'text',
   'tableColumnId': 37647753,
   'width': 280,
   'format': {}}],
 'grants': [{'inherited': False, 'type': 'viewer', 'flags': ['public']}],
 'tags': ['use of force', 'police'],
 'flags': ['default',
  'ownerMayBeContacted',
  'restorable',
  'restorePossibleForType']}

    domain = Domain("test.org")
    data = domain.metadata("test")

    assert isinstance(data, dict)
    assert data.get("id") == "9mnw-mbde"

TEST1 = "@TEST"
TEST2 = TEST1[1:]

# Helpers (Don't call API thesmselves)
def test_build_chunk_select_clause():
    domain = Domain("data.test.org")
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
    domain = Domain("data.test.org")
    quoted = domain._quote_field_name(TEST1)
    no_quotes = domain._quote_field_name(TEST2)

    assert '`' in quoted
    assert '`' not in no_quotes

@pytest.fixture(autouse=True)
def cleanup_loggers():
    yield
    # After every test, clear the logging registry
    import logging
    logger_dict = logging.root.manager.loggerDict
    for name in list(logger_dict.keys()):
        from utils import destroy_logger
        destroy_logger(name)
