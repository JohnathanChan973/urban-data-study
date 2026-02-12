from unittest.mock import MagicMock, patch
from decorators import setup, Socrata
from requests import ReadTimeout
import pytest

INIT_TIMEOUT = 15
class MockDomain:
    def __init__(self):
        self.client = None
        self.domain = "test.org"
        self.token = None
        self.timeout = INIT_TIMEOUT
        self.log = None

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_setup_decorator(mock_setup_logger, mock_socrata_class):
    mock_instance = MagicMock(spec=Socrata)
    mock_instance.timeout = INIT_TIMEOUT
    mock_socrata_class.return_value = mock_instance

    # function to be wrapped
    mock_func = MagicMock(side_effect=[Exception("First Attempt Fail"), ReadTimeout("Timeout"), "Data Found"])
    mock_func.__name__ = "get_data_method"

    decorated_func = setup(times=3, delay=0)(mock_func)
    domain_instance = MockDomain()
    
    result = decorated_func(domain_instance)

    assert result == "Data Found"
    
    # verify retry logic
    assert mock_func.call_count == 3

    # verify client logic
    mock_socrata_class.assert_called_once_with(
        domain_instance.domain, 
        domain_instance.token, 
        timeout=INIT_TIMEOUT
    )

    # verify timeout logic
    assert mock_instance.timeout == 30

@patch("decorators.Socrata")
@patch("decorators.setup_logger")
def test_setup_failure(mock_setup_logger, mock_socrata_class):
    mock_instance = MagicMock(spec=Socrata)
    mock_socrata_class.return_value = mock_instance
    logger_mock = mock_setup_logger.return_value

    mock_func = MagicMock(side_effect=Exception("API is down"))
    mock_func.__name__ = "get_data_method"

    decorated_func = setup(times=3, delay=0)(mock_func)
    domain_instance = MockDomain()

    with pytest.raises(Exception) as excinfo:
        decorated_func(domain_instance)

    assert "API is down" in str(excinfo.value)
    
    assert logger_mock.error.called # verify the error log is made
    assert mock_func.call_count == 3