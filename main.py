# main.py

import argparse
from src import doi_extractor, downloader
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE

def main():
    parser = argparse.ArgumentParser(
        description="Tool for extracting DOIs from BibTeX and downloading PDFs from Sci-Hub."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Subparser for DOI extraction
    extract_parser = subparsers.add_parser("extract", help="Extract DOIs from a BibTeX file")
    extract_parser.add_argument("--bibtex", type=str, default=BIBTEX_FILE,
                                help="Path to the BibTeX file")
    extract_parser.add_argument("--output", type=str, default=EXTRACTED_DOIS_FILE,
                                help="Output path for extracted DOIs")

    # Subparser for downloading papers
    download_parser = subparsers.add_parser("download", help="Download PDFs from Sci-Hub")
    download_parser.add_argument("--doi_file", type=str, default=EXTRACTED_DOIS_FILE,
                                 help="File containing DOIs to download")

    args = parser.parse_args()

    if args.command == "extract":
        doi_extractor.extract_dois_from_bibtex(args.bibtex, args.output)
    elif args.command == "download":
        downloader.download_all_papers(args.doi_file)

if __name__ == "__main__":
    main()
