from pathlib import Path
import logging

BASE = Path(__file__).resolve().parent.parent.parent # Should be the same level as src

def _setup_highest_dir(name):
    new_dir = (BASE / name)
    new_dir.mkdir(exist_ok=True)
    return new_dir

def setup_dir(domain, name=None):
    data_dir = _setup_highest_dir("data")
    domain_dir = (data_dir / str(domain))
    domain_dir.mkdir(exist_ok=True)
    if name:
        newdir = (domain_dir / name)
        newdir.mkdir(exist_ok=True)
        return newdir
    return domain_dir

def setup_logger(domain):
    """
    Establishes a logger singleton for the given domain
    
    :param domain: name of the domain being used
    """
    log_dir = _setup_highest_dir("logs")
    domain_dir = (log_dir / str(domain))
    domain_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(domain)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # Handlers
    error_handler = logging.FileHandler(domain_dir / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)

    warning_handler = logging.FileHandler(domain_dir / "warnings.log", encoding="utf-8")
    warning_handler.setLevel(logging.WARNING)

    info_handler = logging.FileHandler(domain_dir / "info.log", encoding="utf-8")
    info_handler.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    for h in (error_handler, warning_handler, info_handler):
        h.setFormatter(fmt)
        logger.addHandler(h)

    return logger

def destroy_logger(name):
    logger = logging.getLogger(name)
    # Remove all handlers so the files are released
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
