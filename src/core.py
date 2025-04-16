from src.doi_extractor import extract_dois_from_bibtex
from src.downloader import download_all_papers

def extract(bibtex_path: str, output_path: str):
    extract_dois_from_bibtex(bibtex_path, output_path)

def download(doi_file_path: str, log_file_path: str):
    download_all_papers(doi_file_path, log_file_path)
