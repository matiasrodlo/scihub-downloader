import os
import logging
from logging.handlers import RotatingFileHandler

# ---------------------- General Application Settings ----------------------
APP_VERSION = "1.0"
DEBUG_MODE = True
USE_COLOR = True
SECRET_KEY = "replace-this-with-a-secure-key"

# ---------------------- Project Directories ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ---------------------- File Paths ----------------------
BIBTEX_FILE = os.path.join(DATA_DIR, "meta-data-sample.bib")
EXTRACTED_DOIS_FILE = os.path.join(DATA_DIR, "extracted_dois.txt")
FAILED_DOIS_FILE = os.path.join(DATA_DIR, "failed_dois.txt")
LIBRARY_FILE = os.path.join(DATA_DIR, "library.txt")
LOG_FILE = os.path.join(LOGS_DIR, "downloader.log")
EXTRACTION_SUMMARY_FILE = os.path.join(DATA_DIR, "extraction_summary.json")

# ---------------------- Sci-Hub Download Settings ----------------------
SCI_HUB_URLS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.tf",
    "https://sci-hub.wf",
]

PAGE_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 10
DELAY_MIN = 2
DELAY_MAX = 5
MAX_WORKERS = 5

# ---------------------- Logging Settings ----------------------
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

# ---------------------- Regular Expressions ----------------------
DOI_REGEX = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'

# ---------------------- Logger Initialization ----------------------
def get_logger(name="app"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False  # Avoid duplicate logs from root
    return logger
