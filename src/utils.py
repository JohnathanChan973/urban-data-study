from pathlib import Path
import logging

BASE = Path(__file__).resolve().parent.parent / "data"

def setup_dir(domain, name=None):
    BASE.mkdir(exist_ok=True)
    citydir = (BASE / "domain_data")
    citydir.mkdir(exist_ok=True)
    domaindir = (citydir / str(domain))
    domaindir.mkdir(exist_ok=True)
    if name:
        newdir = (domaindir / name)
        newdir.mkdir(exist_ok=True)
        return newdir

def setup_logger(domain):
    """
    Establishes a logger singleton for the given domain
    
    :param domain: name of the domain being used
    """
    logdir = setup_dir(domain, "logs")

    logger = logging.getLogger(domain)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # Handlers
    error_handler = logging.FileHandler(logdir / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)

    warning_handler = logging.FileHandler(logdir / "warnings.log", encoding="utf-8")
    warning_handler.setLevel(logging.WARNING)

    info_handler = logging.FileHandler(logdir / "info.log", encoding="utf-8")
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

"""
Utility functions for DeepJoin
"""
def build_column_text(col_name, values):
    """
    Create DeepJoin's text representation:
    'column: borough. sample values: Manhattan, Queens, Bronx'
    """
    sample_text = ", ".join([str(v) for v in values if v])
    return f"Column: {col_name}. Sample values: {sample_text}"