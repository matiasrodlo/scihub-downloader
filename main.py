import argparse
import time
from colorama import init, Fore, Style
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE, LOG_FILE
from src.core import extract, download

# Initialize color output
init(autoreset=True)

def interactive_menu():
    print(Fore.CYAN + "\n📘 Welcome to Sci-Hub Downloader (Terminal Mode)\n" + Style.RESET_ALL)
    print("1. 📄 Extract DOIs from a BibTeX file")
    print("2. 📥 Download PDFs from Sci-Hub")
    print("0. ❌ Exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        bibtex = input(f"BibTeX path [{BIBTEX_FILE}]: ").strip() or BIBTEX_FILE
        output = input(f"Output path [{EXTRACTED_DOIS_FILE}]: ").strip() or EXTRACTED_DOIS_FILE

        try:
            count = extract(bibtex, output)
            print(Fore.GREEN + f"\n✅ Extracted {count} DOIs → {output}\n")
        except Exception as e:
            print(Fore.RED + f"\n❌ Extraction failed: {e}\n")

    elif choice == "2":
        doi_file = input(f"DOI list path [{EXTRACTED_DOIS_FILE}]: ").strip() or EXTRACTED_DOIS_FILE

        try:
            start = time.time()
            download(doi_file, LOG_FILE)
            elapsed = time.time() - start
            print(Fore.GREEN + f"\n✅ Download process complete in {elapsed:.1f} seconds!\n")
        except Exception as e:
            print(Fore.RED + f"\n❌ Download failed: {e}\n")

    elif choice == "0":
        print("👋 Exiting. Goodbye!\n")
    else:
        print(Fore.YELLOW + "\n⚠️ Invalid choice. Restart and try again.\n")

def main():
    parser = argparse.ArgumentParser(
        description="🧠 Sci-Hub Downloader CLI — Extract DOIs and fetch PDFs",
        epilog="Examples:\n"
               "  python3 main.py extract\n"
               "  python3 main.py download\n"
               "  python3 main.py interactive",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # Extract
    extract_cmd = subparsers.add_parser("extract", help="Extract DOIs from BibTeX file")
    extract_cmd.add_argument("--bibtex", type=str, default=BIBTEX_FILE, help="Path to .bib file")
    extract_cmd.add_argument("--output", type=str, default=EXTRACTED_DOIS_FILE, help="Output file path")

    # Download
    download_cmd = subparsers.add_parser("download", help="Download PDFs from DOI list")
    download_cmd.add_argument("--doi_file", type=str, default=EXTRACTED_DOIS_FILE, help="DOI file path")

    # Interactive mode
    subparsers.add_parser("interactive", help="Run interactive terminal menu")

    args = parser.parse_args()

    if args.command == "extract":
        count = extract(args.bibtex, args.output)
        print(Fore.GREEN + f"\n✅ Extracted {count} DOIs → {args.output}\n")

    elif args.command == "download":
        start = time.time()
        download(args.doi_file, LOG_FILE)
        elapsed = time.time() - start
        print(Fore.GREEN + f"\n✅ Download process complete in {elapsed:.1f} seconds!\n")

    elif args.command == "interactive":
        interactive_menu()
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⛔ Interrupted by user. Exiting gracefully...\n")
