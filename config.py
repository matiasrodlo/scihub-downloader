# config.py

import os

# ---------------------- General Application Settings ----------------------
APP_VERSION = "1.0"
DEBUG_MODE = False  # Set to True to enable verbose debug output
USE_COLOR = True    # Enable or disable colored CLI output (useful for terminals with limited support)

# ---------------------- Project Directories ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Ensure necessary directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ---------------------- File Paths ----------------------
BIBTEX_FILE = os.path.join(DATA_DIR, "meta-data-sample.bib")
EXTRACTED_DOIS_FILE = os.path.join(DATA_DIR, "extracted_dois.txt")
FAILED_DOIS_FILE = os.path.join(DATA_DIR, "failed_dois.txt")
LIBRARY_FILE = os.path.join(DATA_DIR, "library.txt")
LOG_FILE = os.path.join(LOGS_DIR, "downloader.log")

# ---------------------- Sci-Hub Download Settings ----------------------
# List of Sci-Hub mirror URLs to try for downloading PDFs
SCI_HUB_URLS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.tf",
    "https://sci-hub.wf",
]

# Timeout settings (in seconds)
PAGE_TIMEOUT = 10     # Maximum time to wait for a page to load
DOWNLOAD_TIMEOUT = 10 # Maximum time to wait for a PDF download response

# Delay range (in seconds) between download attempts to minimize rate limiting
DELAY_MIN = 2
DELAY_MAX = 5

# Maximum number of concurrent worker threads/processes to download PDFs
MAX_WORKERS = 5

# ---------------------- Logging Settings ----------------------
# Configure log file rotation: files rotate after LOG_MAX_BYTES with LOG_BACKUP_COUNT backup files.
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

# ---------------------- Regular Expressions ----------------------
# Regular expression to validate DOI format (used in downloader.py)
DOI_REGEX = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
