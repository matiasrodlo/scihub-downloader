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

# ✅ Console + log stream wrapper
def log_line(logf, message):
    print(message)
    logf.write(message + "\n")
    logf.flush()

# ✅ Custom headers to mimic a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def download_pdf(doi, logf, cached_mirror=None):
    mirrors = [cached_mirror] if cached_mirror else SCI_HUB_URLS

    for base_url in mirrors:
        if not base_url:
            continue
        try:
            full_url = f"{base_url}/{doi}"
            log_line(logf, f"TRYING MIRROR: {full_url}")

            res = requests.get(full_url, headers=HEADERS, timeout=DOWNLOAD_TIMEOUT)
            if res.status_code != 200:
                log_line(logf, f"❌ Failed to access {full_url}: {res.status_code}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            iframe = soup.find("iframe")
            if not iframe or not iframe.get("src"):
                log_line(logf, f"⚠️ No PDF iframe found for {doi} on {base_url}")
                continue

            pdf_url = iframe["src"]
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            elif pdf_url.startswith("/"):
                pdf_url = base_url + pdf_url

            log_line(logf, f"PDF URL: {pdf_url}")

            pdf_res = requests.get(pdf_url, headers=HEADERS, timeout=DOWNLOAD_TIMEOUT, stream=True)
            if pdf_res.status_code == 200 and "application/pdf" in pdf_res.headers.get("Content-Type", ""):
                filename = doi.replace("/", "_").replace(":", "_") + ".pdf"
                with open(os.path.join("data", filename), "wb") as f:
                    for chunk in pdf_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                log_line(logf, f"✅ SUCCESS: {doi}")
                return True, base_url  # success + working mirror
            else:
                log_line(logf, f"❌ PDF fetch failed: {pdf_url} ({pdf_res.status_code})")

        except Exception as e:
            log_line(logf, f"🔥 EXCEPTION at {base_url} for {doi}: {str(e)}")
            continue

    log_line(logf, f"❌ FINAL FAILURE: {doi}")
    return False, None  # fail, no mirror to reuse

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
    working_mirror = None

    open(FAILED_DOIS_FILE, "w").close()  # clear failed log

    with open(log_file_path, "a", encoding="utf-8") as logf:
        log_line(logf, f"📦 TOTAL: {total}")

        for i, doi in enumerate(dois):
            if doi in downloaded:
                skipped_count += 1
                log_line(logf, f"SKIPPED: {doi}")
                continue

            log_line(logf, f"🔄 PROCESSING: {doi} ({i + 1}/{total})")
            success, used_mirror = download_pdf(doi, logf, cached_mirror=working_mirror)

            if success:
                working_mirror = used_mirror  # ✅ update working mirror
                with open(LIBRARY_FILE, "a", encoding="utf-8") as libf:
                    libf.write(doi + "\n")
                log_line(logf, f"✅ DOWNLOADED: {doi}")
            else:
                working_mirror = None  # ❌ reset mirror cache
                failed.append(doi)
                with open(FAILED_DOIS_FILE, "a", encoding="utf-8") as failf:
                    failf.write(doi + "\n")

            time.sleep(DELAY_MIN)

        log_line(logf, f"⚠️ SKIPPED COUNT: {skipped_count}")
        log_line(logf, f"📥 DONE. TOTAL: {total}, DOWNLOADED: {total - skipped_count - len(failed)}, FAILED: {len(failed)}")
