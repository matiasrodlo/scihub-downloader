import os
import logging
from logging.handlers import RotatingFileHandler

# ---------------------- General Settings ----------------------
APP_VERSION = "1.0"
DEBUG_MODE = True
USE_COLOR = True

# ---------------------- Project Directories ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")

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
    "https://sci-hub.hkvisa.net",     # ✅ Alternative mirror (HK)
    "https://sci-hub.scihubtw.tw",    # ✅ TW mirror
    "https://sci-hub.ee",             # ✅ EE mirror
]

DOWNLOAD_TIMEOUT = 10     # Request timeout in seconds
DELAY_MIN = 3             # Delay between downloads to avoid IP bans
DELAY_MAX = 5             # (Reserved for future random delay support)
MAX_WORKERS = 5           # (Reserved for future parallel downloads)

# ---------------------- Logging Settings ----------------------
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

# ---------------------- DOI Pattern ----------------------
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
        logger.propagate = False
    return logger
