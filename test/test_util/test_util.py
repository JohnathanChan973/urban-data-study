from util.util import _setup_highest_dir, setup_dir, setup_logger, destroy_logger
from unittest.mock import patch

def test_setup_highest_dir(tmp_path):
    test_dir = tmp_path
    
    with patch("util.util.BASE", test_dir):
        result = _setup_highest_dir("test")
        assert (result).exists()

def test_setup_dir(tmp_path):
    test_dir = tmp_path / "test"
    test_dir.mkdir()

    with patch("util.util._setup_highest_dir", return_value=test_dir) as mock_highest:
        setup_dir("test_domain")
        mock_highest.assert_called_once()
        # verify structure
        assert (test_dir).exists()
        test_domain = test_dir / "test_domain"
        assert (test_domain).exists()

def test_setup_newdir(tmp_path):
    test_dir = tmp_path / "test"
    test_dir.mkdir()

    with patch("util.util._setup_highest_dir", return_value=test_dir) as mock_highest:        
        new_dir = setup_dir("test_domain", "new_dir")
        mock_highest.assert_called_once()
        assert (new_dir).exists

def test_logger(tmp_path):
    test_dir = tmp_path / "test"
    test_dir.mkdir()

    with patch("util.util._setup_highest_dir", return_value=test_dir) as mock_highest:
        logger = setup_logger("test_domain")

        mock_highest.assert_called_once()

        test_domain = test_dir / "test_domain"
        assert (test_domain / "info.log").exists()
        assert (test_domain / "warnings.log").exists()
        assert (test_domain / "errors.log").exists()
        
        # verify singleton behavior
        logger_again = setup_logger("test_domain")
        assert len(logger_again.handlers) == 3 # should remain 3
        destroy_logger("test_domain")
        assert len(logger.handlers) == 0