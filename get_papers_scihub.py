import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
import time
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    filename='downloader.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# List of possible Sci-Hub mirrors
SCI_HUB_URLS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.tf",
    "https://sci-hub.wf",
]

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

DOI_REGEX = re.compile(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.IGNORECASE)


def read_dois(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and DOI_REGEX.fullmatch(line.strip())]


def load_library(library_file="library.txt"):
    if os.path.exists(library_file):
        with open(library_file, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def add_to_library(doi, library_file="library.txt"):
    with open(library_file, "a", encoding="utf-8") as f:
        f.write(doi + "\n")
    logging.info(f"Added DOI to library: {doi}")


def log_failed_doi(doi, file_path="failed_dois.txt"):
    # Check if failed_dois.txt exists and contains this DOI already
    existing_failed = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_failed = set(line.strip() for line in f if line.strip())
    if doi in existing_failed:
        logging.info(f"DOI already in failed_dois.txt: {doi}")
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(doi + "\n")
        logging.info(f"Added DOI to failed_dois.txt: {doi}")


def get_working_mirror():
    for url in SCI_HUB_URLS:
        try:
            r = session.get(url, timeout=5)
            if r.status_code == 200:
                return url
        except requests.exceptions.RequestException:
            continue
    raise Exception("No working Sci-Hub mirrors found.")


def doi_to_filename(doi):
    return doi.replace("/", "_").replace(":", "_").strip()


def download_pdf(doi, base_url, output_dir="downloads"):
    url = f"{base_url}/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            logging.warning(f"Could not fetch page for DOI: {doi} (Status Code: {r.status_code})")
            return False

        soup = BeautifulSoup(r.content, "html.parser")
        pdf_url = None

        try:
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
                    href = link["href"]
                    if href.lower().endswith(".pdf"):
                        pdf_url = href
                        break

            if not pdf_url:
                matches = re.findall(r'src=["\'](https?://[^"\']+\.pdf)', r.text)
                if matches:
                    pdf_url = matches[0]
        except Exception as parse_err:
            logging.error(f"Error parsing PDF URL for DOI {doi}: {parse_err}")
            return False

        if not pdf_url:
            logging.warning(f"No PDF found for DOI: {doi}")
            return False

        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            pdf_url = base_url + pdf_url

        os.makedirs(output_dir, exist_ok=True)
        safe_filename = doi_to_filename(doi) + ".pdf"
        filepath = os.path.join(output_dir, safe_filename)

        pdf_response = session.get(pdf_url, headers=headers, stream=True, timeout=10)
        if pdf_response.status_code != 200:
            logging.warning(f"Failed to download PDF for DOI: {doi} (Status Code: {pdf_response.status_code})")
            return False

        with open(filepath, 'wb') as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"Downloaded: {safe_filename}")
        return True

    except Exception as e:
        logging.error(f"Exception for DOI {doi}: {e}")
        return False


def bulk_download(doi_file, library_file="library.txt"):
    all_dois = read_dois(doi_file)
    downloaded_library = load_library(library_file)
    
    # Log DOIs that are already in library.txt
    for doi in all_dois:
        if doi in downloaded_library:
            logging.info(f"DOI already in library.txt: {doi}")

    # Filter only new DOIs for download
    new_dois = [doi for doi in all_dois if doi not in downloaded_library]

    if not new_dois:
        logging.info("No new DOIs to process. All papers have already been downloaded.")
        return

    try:
        base_url = get_working_mirror()
    except Exception as e:
        logging.error(f"Error getting Sci-Hub mirror: {e}")
        return

    logging.info(f"Using Sci-Hub mirror: {base_url}")
    for doi in tqdm(new_dois, desc="Processing DOIs"):
        success = download_pdf(doi, base_url)
        if success:
            add_to_library(doi, library_file)
        else:
            log_failed_doi(doi)

        delay = random.uniform(2, 5)
        time.sleep(delay)


if __name__ == "__main__":
    bulk_download("extracted_dois.txt")
