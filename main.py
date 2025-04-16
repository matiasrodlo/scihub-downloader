import sys
import argparse
from colorama import init, Fore, Style
from src import doi_extractor, downloader
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE

# Initialize Colorama for cross-platform colored output
init(autoreset=True)

def interactive_menu():
    print(Fore.CYAN + "\nWelcome to Sci-Hub Downloader CLI (Interactive Mode)" + Style.RESET_ALL)
    print("Select an option:")
    print("  1. Extract DOIs from a BibTeX file")
    print("  2. Download PDFs from Sci-Hub")
    
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        print("\n[Extraction Mode]")
        bibtex_input = input(
            f"Confirm with Enter that your BibTeX file is at the default location [{BIBTEX_FILE}],\n"
            "or type a new path: "
        ).strip()
        bibtex = bibtex_input if bibtex_input else BIBTEX_FILE

        output_input = input(
            f"Confirm with Enter that the output file for the extracted DOIs will be [{EXTRACTED_DOIS_FILE}],\n"
            "or type a new path: "
        ).strip()
        output = output_input if output_input else EXTRACTED_DOIS_FILE

        try:
            doi_extractor.extract_dois_from_bibtex(bibtex, output)
            print(Fore.GREEN + f"\n✅ DOI extraction successful! Output saved to {output}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"\n❌ Extraction failed: {e}" + Style.RESET_ALL)
    elif choice == "2":
        print("\n[Download Mode]")
        doi_file_input = input(
            f"Confirm with Enter that your DOI file is located at the default path [{EXTRACTED_DOIS_FILE}],\n"
            "or type a new path: "
        ).strip()
        doi_file = doi_file_input if doi_file_input else EXTRACTED_DOIS_FILE

        try:
            downloader.download_all_papers(doi_file)
            print(Fore.GREEN + "\n✅ Download process finished!" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"\n❌ Download failed: {e}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "\n⚠️  Invalid choice. Please restart the application and select a valid option.\n" + Style.RESET_ALL)

def run_extract(bibtex, output):
    try:
        doi_extractor.extract_dois_from_bibtex(bibtex, output)
        print(Fore.GREEN + f"\n✅ DOI extraction successful! Output saved to {output}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\n❌ Extraction failed: {e}" + Style.RESET_ALL)

def run_download(doi_file):
    try:
        downloader.download_all_papers(doi_file)
        print(Fore.GREEN + "\n✅ Download process finished!" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\n❌ Download failed: {e}" + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(description="Sci-Hub Downloader CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands: extract or download")

    # Subparser for extract
    parser_extract = subparsers.add_parser("extract", help="Extract DOIs from a BibTeX file")
    parser_extract.add_argument("--bibtex", type=str, default=BIBTEX_FILE, help="Path to BibTeX file")
    parser_extract.add_argument("--output", type=str, default=EXTRACTED_DOIS_FILE, help="Path to
