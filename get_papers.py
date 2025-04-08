import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
import time
import random

# List of possible Sci-Hub mirrors
SCI_HUB_URLS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.st",
    "https://sci-hub.tf",
    "https://sci-hub.wf",
]

def read_dois(file_path):
    """Read DOIs from the input file (one per line)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def load_library(library_file="library.txt"):
    """Load the set of DOIs that have already been downloaded."""
    if os.path.exists(library_file):
        with open(library_file, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def add_to_library(doi, library_file="library.txt"):
    """Append a DOI to the library file."""
    with open(library_file, "a", encoding="utf-8") as f:
        f.write(doi + "\n")

def get_working_mirror():
    """Return the first responding Sci-Hub mirror."""
    for url in SCI_HUB_URLS:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return url
        except requests.exceptions.RequestException:
            continue
    raise Exception("No working Sci-Hub mirrors found.")

def doi_to_filename(doi):
    """Convert a DOI into a filename-safe string."""
    return doi.replace("/", "_").replace(":", "_").strip()

def download_pdf(doi, base_url, output_dir="downloads"):
    """
    Download the PDF for a given DOI from the selected Sci-Hub mirror.
    Returns True if downloaded successfully, False otherwise.
    """
    url = f"{base_url}/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[!] Could not fetch page for DOI: {doi} (Status Code: {r.status_code})")
            return False

        soup = BeautifulSoup(r.content, "html.parser")
        pdf_url = None

        # Strategy 1: Look for an <iframe>
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            pdf_url = iframe.get("src")

        # Strategy 2: If no iframe, look for an <embed>
        if not pdf_url:
            embed = soup.find("embed")
            if embed and embed.get("src"):
                pdf_url = embed.get("src")

        # Strategy 3: Look for direct links in <a> tags that end with .pdf
        if not pdf_url:
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if href.lower().endswith(".pdf"):
                    pdf_url = href
                    break

        # Strategy 4: Fallback using regex on the entire HTML page
        if not pdf_url:
            matches = re.findall(r'src=["\'](https?://[^"\']+\.pdf)', r.text)
            if matches:
                pdf_url = matches[0]

        if not pdf_url:
            print(f"[!] No PDF found for DOI: {doi}")
            return False

        # Normalize URL if it is relative or protocol-less
        if pdf_url.startswith("//"):
            pdf_url = "https:" + pdf_url
        elif pdf_url.startswith("/"):
            pdf_url = base_url + pdf_url

        # Prepare output folder and filename
        os.makedirs(output_dir, exist_ok=True)
        safe_filename = doi_to_filename(doi) + ".pdf"
        filepath = os.path.join(output_dir, safe_filename)

        # Download the PDF file
        pdf_response = requests.get(pdf_url, headers=headers, stream=True, timeout=10)
        if pdf_response.status_code != 200:
            print(f"[!] Failed to download PDF for DOI: {doi} (Status Code: {pdf_response.status_code})")
            return False

        with open(filepath, 'wb') as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"[+] Downloaded: {safe_filename}")
        return True

    except Exception as e:
        print(f"[!] Exception for DOI {doi}: {e}")
        return False

def bulk_download(doi_file, library_file="library.txt"):
    """
    Process the DOI file, skipping any DOIs already present in the library,
    and downloading new papers.
    """
    all_dois = read_dois(doi_file)
    downloaded_library = load_library(library_file)
    
    # Filter out already-downloaded DOIs
    new_dois = [doi for doi in all_dois if doi not in downloaded_library]
    if not new_dois:
        print("[i] No new DOIs to process. All papers have already been downloaded.")
        return

    try:
        base_url = get_working_mirror()
    except Exception as e:
        print(e)
        return

    print(f"Using Sci-Hub mirror: {base_url}")
    for doi in tqdm(new_dois, desc="Processing DOIs"):
        success = download_pdf(doi, base_url)
        if success:
            add_to_library(doi, library_file)
        # 🕒 Add a randomized delay between downloads to avoid server overload
        delay = random.uniform(2, 5)
        print(f"[i] Sleeping for {delay:.2f} seconds to respect server load...")
        time.sleep(delay)

if __name__ == "__main__":
    # Replace "neuroscience_dois.txt" with your DOI list file (e.g., "extracted_dois.txt")
    bulk_download("extracted_dois.txt")