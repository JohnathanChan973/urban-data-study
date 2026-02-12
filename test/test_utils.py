from utils import setup_logger, destroy_logger
from unittest.mock import patch

def test_setup_logger(tmp_path):
    test_dir = tmp_path / "test"
    with patch("utils.BASE", test_dir):
        logger = setup_logger("test_domain")
        
        # verify structure
        assert (test_dir).exists()
        test_city = test_dir / "city_data"
        assert (test_city).exists()
        test_domain = test_city / "test_domain"
        assert (test_domain).exists()
        test_logs = test_domain / "logs"
        assert (test_logs).exists()
        assert (test_logs / "info.log").exists()
        assert (test_logs / "warnings.log").exists()
        assert (test_logs / "errors.log").exists()
        
        # verify singleton behavior
        logger_again = setup_logger("test_domain")
        assert len(logger_again.handlers) == 3 # should remain 3
        destroy_logger("test_domain")
        assert len(logger.handlers) == 0