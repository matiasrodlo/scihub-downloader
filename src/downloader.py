# src/downloader.py

import os
import re
import time
import random
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from config import (
    SCI_HUB_URLS, PAGE_TIMEOUT, DOWNLOAD_TIMEOUT,
    DELAY_MIN, DELAY_MAX, MAX_WORKERS,
    LIBRARY_FILE, FAILED_DOIS_FILE, EXTRACTED_DOIS_FILE, LOG_FILE, DOI_REGEX,
    DATA_DIR
)

# ------------------------- Logging Setup ------------------------------
logger = logging.getLogger("SciHubDownloader")
logger.setLevel(logging.INFO)
# Create a rotating file handler
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
# -----------------------------------------------------------------------

# ------------------------ Session Configuration ------------------------
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
# -----------------------------------------------------------------------

DOI_PATTERN = re.compile(DOI_REGEX, re.IGNORECASE)

def read_dois(file_path: str) -> list:
    """Read and validate DOIs from a file."""
    dois = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                doi = line.strip()
                if doi and DOI_PATTERN.fullmatch(doi):
                    dois.append(doi)
    except Exception as e:
        logger.error(f"Error reading DOIs from {file_path}: {e}")
    return dois

def load_library(library_file: str = LIBRARY_FILE) -> set:
    """Load DOIs already downloaded."""
    if os.path.exists(library_file):
        with open(library_file, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def add_to_library(doi: str, library_file: str = LIBRARY_FILE):
    """Append a DOI to the library file."""
    with open(library_file, "a", encoding="utf-8") as f:
        f.write(doi + "\n")
    logger.info(f"Added DOI to library: {doi}")

def log_failed_doi(doi: str, file_path: str = FAILED_DOIS_FILE):
    """Log a DOI as failed (avoid duplicates)."""
    existing_failed = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_failed = set(line.strip() for line in f if line.strip())
    if doi not in existing_failed:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(doi + "\n")
        logger.info(f"Logged failed DOI: {doi}")
    else:
        logger.info(f"DOI already logged as failed: {doi}")

def get_working_mirror() -> str:
    """Return a working Sci-Hub mirror."""
    for url in SCI_HUB_URLS:
        try:
            r = session.get(url, timeout=5)
            if r.status_code == 200:
                logger.info(f"Using Sci-Hub mirror: {url}")
                return url
        except requests.exceptions.RequestException:
            continue
    raise Exception("No working Sci-Hub mirrors found.")

def doi_to_filename(doi: str) -> str:
    """Convert DOI to a safe filename."""
    return doi.replace("/", "_").replace(":", "_").strip() + ".pdf"

def download_pdf_for_doi(doi: str, base_url: str, output_dir: str = os.path.join(DATA_DIR, "downloads")) -> bool:
    """Download PDF for a given DOI using the specified Sci-Hub mirror."""
    url = f"{base_url}/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = session.get(url, headers=headers, timeout=PAGE_TIMEOUT)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching page for DOI {doi}: {e}")
        return False

    pdf_url = None
    try:
        soup = BeautifulSoup(r.content, "html.parser")
        # Try to find the PDF link in various tags
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            pdf_url = iframe.get("src")
        if not pdf_url:
            embed = soup.find("embed")
            if embed and embed.get("src"):
                pdf_url = embed.get("src")
        if not pdf_url:
            links = soup.find_all("a", href=True)
            for link in links:
                if link["href"].lower().endswith(".pdf"):
                    pdf_url = link["href"]
                    break
        if not pdf_url:
            matches = re.findall(r'src=["\'](https?://[^"\']+\.pdf)', r.text)
            if matches:
                pdf_url = matches[0]
    except Exception as parse_err:
        logger.error(f"Error parsing PDF URL for DOI {doi}: {parse_err}")
        return False

    if not pdf_url:
        logger.warning(f"No PDF link found for DOI: {doi}")
        return False

    # Normalize URL if needed
    if pdf_url.startswith("//"):
        pdf_url = "https:" + pdf_url
    elif pdf_url.startswith("/"):
        pdf_url = base_url + pdf_url

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, doi_to_filename(doi))

    try:
        pdf_resp = session.get(pdf_url, headers=headers, timeout=DOWNLOAD_TIMEOUT)
        pdf_resp.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(pdf_resp.content)
        logger.info(f"Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download PDF for DOI {doi}: {e}")
        return False

def process_doi(doi: str, base_url: str) -> None:
    """Download PDF and update library or failed log based on result."""
    if download_pdf_for_doi(doi, base_url):
        add_to_library(doi)
    else:
        log_failed_doi(doi)
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

def download_all_papers(doi_file: str) -> None:
    dois = read_dois(doi_file)
    if not dois:
        logger.info("No valid DOIs found to process.")
        return

    library = load_library()
    dois_to_process = [doi for doi in dois if doi not in library]
    if not dois_to_process:
        logger.info("No new DOIs to download.")
        return

    try:
        mirror = get_working_mirror()
    except Exception as e:
        logger.error(str(e))
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_doi, doi, mirror): doi for doi in dois_to_process}
        for future in as_completed(futures):
            doi = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing DOI {doi}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download PDFs from Sci-Hub using a list of DOIs.")
    parser.add_argument("--doi_file", type=str, default=EXTRACTED_DOIS_FILE,
                        help="Path to the file containing DOIs")
    args = parser.parse_args()
    download_all_papers(args.doi_file)

if __name__ == "__main__":
    main()
