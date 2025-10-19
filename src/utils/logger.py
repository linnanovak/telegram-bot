import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.INFO
    )
    return logging.getLogger("ash")

def setup_user_logger():
    user_logger = logging.getLogger("user_logger")
    user_logger.setLevel(logging.INFO)
    
    log_file = Path("data/logs/users.log")
    log_file.parent.mkdir(exist_ok=True)
    
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    user_logger.addHandler(fh)
    
    return user_logger
