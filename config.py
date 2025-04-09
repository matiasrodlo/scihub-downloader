# config.py

import os

# ---------------------- Project Directories ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ---------------------- File Paths ----------------------
BIBTEX_FILE = os.path.join(DATA_DIR, "meta-data-sample.bib")
EXTRACTED_DOIS_FILE = os.path.join(DATA_DIR, "extracted_dois.txt")
FAILED_DOIS_FILE = os.path.join(DATA_DIR, "failed_dois.txt")
LIBRARY_FILE = os.path.join(DATA_DIR, "library.txt")
LOG_FILE = os.path.join(LOGS_DIR, "downloader.log")

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
# Regular expression to validate DOI format (used in downloader.py)
DOI_REGEX = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
