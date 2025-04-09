# src/doi_extractor.py

import re
import argparse
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE

def extract_dois_from_bibtex(bibtex_path: str, output_path: str) -> int:
    """
    Extracts DOIs from a BibTeX file and writes them to the output path.
    Returns the number of DOIs extracted.
    """
    try:
        with open(bibtex_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading {bibtex_path}: {e}")
        return 0

    # Match entries like DOI = {value} or DOI = "value"
    dois = re.findall(r'DOI\s*=\s*[{"]([^}"]+)[}"]', content, re.IGNORECASE)

    if not dois:
        print("No DOIs found.")
        return 0

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for doi in dois:
                f.write(doi.strip() + "\n")
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")
        return 0

    print(f"[+] Extracted {len(dois)} DOIs to {output_path}")
    return len(dois)

def main():
    parser = argparse.ArgumentParser(description="Extract DOIs from a BibTeX file.")
    parser.add_argument("--bibtex", type=str, default=BIBTEX_FILE,
                        help="Path to the BibTeX file")
    parser.add_argument("--output", type=str, default=EXTRACTED_DOIS_FILE,
                        help="Path for the output DOIs file")
    args = parser.parse_args()

    extract_dois_from_bibtex(args.bibtex, args.output)

if __name__ == "__main__":
    main()
