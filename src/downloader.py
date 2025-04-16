import os
import time
import requests
from bs4 import BeautifulSoup
from config import (
    SCI_HUB_URLS,
    DOWNLOAD_TIMEOUT,
    DELAY_MIN,
    FAILED_DOIS_FILE,
    LIBRARY_FILE
)

def download_pdf(doi, logf):
    for base_url in SCI_HUB_URLS:
        try:
            full_url = f"{base_url}/{doi}"
            logf.write(f"TRYING MIRROR: {full_url}\n")

            res = requests.get(full_url, timeout=DOWNLOAD_TIMEOUT)
            if res.status_code != 200:
                logf.write(f"❌ Failed to access {full_url}: {res.status_code}\n")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            iframe = soup.find("iframe")
            if not iframe or not iframe.get("src"):
                logf.write(f"⚠️ No PDF iframe found for {doi} on {base_url}\n")
                continue

            pdf_url = iframe["src"]
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            elif pdf_url.startswith("/"):
                pdf_url = base_url + pdf_url

            logf.write(f"PDF URL: {pdf_url}\n")

            pdf_res = requests.get(pdf_url, timeout=DOWNLOAD_TIMEOUT, stream=True)
            if pdf_res.status_code == 200 and "application/pdf" in pdf_res.headers.get("Content-Type", ""):
                filename = doi.replace("/", "_").replace(":", "_") + ".pdf"
                with open(os.path.join("data", filename), "wb") as f:
                    for chunk in pdf_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                logf.write(f"✅ SUCCESS: {doi}\n")
                return True
            else:
                logf.write(f"❌ PDF fetch failed: {pdf_url} ({pdf_res.status_code})\n")

        except Exception as e:
            logf.write(f"🔥 EXCEPTION at {base_url} for {doi}: {str(e)}\n")
            continue

    logf.write(f"❌ FINAL FAILURE: {doi}\n")
    return False

def download_all_papers(doi_file_path, log_file_path=None):
    with open(doi_file_path, "r") as f:
        dois = [line.strip() for line in f if line.strip()]

    downloaded = set()
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r") as lib:
            downloaded = set(lib.read().splitlines())

    failed = []
    skipped_count = 0
    total = len(dois)

    # Open log file
    with open(log_file_path, "a", encoding="utf-8") as logf:
        logf.write(f"📦 TOTAL: {total}\n")
        logf.flush()

        for i, doi in enumerate(dois):
            if doi in downloaded:
                skipped_count += 1
                logf.write(f"SKIPPED: {doi}\n")
                logf.flush()
                continue

            logf.write(f"🔄 PROCESSING: {doi} ({i + 1}/{total})\n")
            logf.flush()
            success = download_pdf(doi, logf)

            if success:
                with open(LIBRARY_FILE, "a", encoding="utf-8") as libf:
                    libf.write(doi + "\n")
                logf.write(f"DOWNLOADED: {i + 1}\n")
            else:
                failed.append(doi)
                with open(FAILED_DOIS_FILE, "a", encoding="utf-8") as failf:
                    failf.write(doi + "\n")

            logf.flush()
            time.sleep(DELAY_MIN)

        logf.write(f"⚠️ SKIPPED COUNT: {skipped_count}\n")
        logf.write(f"📥 DONE. TOTAL: {total}, DOWNLOADED: {total - skipped_count - len(failed)}, FAILED: {len(failed)}\n")
        logf.flush()
