import argparse
from colorama import init, Fore, Style
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE
from src.core import extract, download

# Initialize color output
init(autoreset=True)

def interactive_menu():
    print(Fore.CYAN + "\nWelcome to Sci-Hub Downloader CLI (Interactive Mode)" + Style.RESET_ALL)
    print("Select an option:")
    print("  1. Extract DOIs from a BibTeX file")
    print("  2. Download PDFs from Sci-Hub")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        bibtex = input(f"BibTeX path [{BIBTEX_FILE}]: ").strip() or BIBTEX_FILE
        output = input(f"Output path [{EXTRACTED_DOIS_FILE}]: ").strip() or EXTRACTED_DOIS_FILE

        try:
            extract(bibtex, output)
            print(Fore.GREEN + f"\n✅ Extraction successful! DOIs saved to {output}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"\n❌ Extraction failed: {e}" + Style.RESET_ALL)

    elif choice == "2":
        doi_file = input(f"DOI file path [{EXTRACTED_DOIS_FILE}]: ").strip() or EXTRACTED_DOIS_FILE

        try:
            download(doi_file)
            print(Fore.GREEN + "\n✅ Download process finished!" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"\n❌ Download failed: {e}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "\n⚠️  Invalid choice. Please restart and select a valid option." + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(description="Sci-Hub Downloader CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands: extract, download, or interactive")

    parser_extract = subparsers.add_parser("extract", help="Extract DOIs from BibTeX file")
    parser_extract.add_argument("--bibtex", type=str, default=BIBTEX_FILE, help="Path to BibTeX file")
    parser_extract.add_argument("--output", type=str, default=EXTRACTED_DOIS_FILE, help="Output file for DOIs")

    parser_download = subparsers.add_parser("download", help="Download PDFs from DOI list")
    parser_download.add_argument("--doi_file", type=str, default=EXTRACTED_DOIS_FILE, help="DOI file path")

    parser_interactive = subparsers.add_parser("interactive", help="Run interactive menu")

    args = parser.parse_args()

    if args.command == "extract":
        extract(args.bibtex, args.output)
    elif args.command == "download":
        download(args.doi_file)
    elif args.command == "interactive":
        interactive_menu()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
