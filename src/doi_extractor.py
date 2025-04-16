import re
import argparse
import json
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE, EXTRACTION_SUMMARY_FILE, get_logger

# Initialize logger
logger = get_logger("doi_extractor")

def extract_dois_from_bibtex(bibtex_path: str, output_path: str) -> int:
    """
    Extracts DOIs from a BibTeX file and writes them to the output path.
    Also writes an extraction summary to EXTRACTION_SUMMARY_FILE.
    Returns the number of DOIs extracted.
    """
    errors = []

    try:
        with open(bibtex_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        logger.error(f"Error reading {bibtex_path}: {e}")
        return 0

    # Match entries like DOI = {value} or DOI = "value"
    dois = re.findall(r'DOI\s*=\s*[{"]([^}"]+)[}"]', content, re.IGNORECASE)

    if not dois:
        logger.warning("No DOIs found.")
        errors.append("No valid DOI entries were found in the BibTeX file.")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for doi in dois:
                f.write(doi.strip() + "\n")
    except Exception as e:
        logger.error(f"Error writing to {output_path}: {e}")
        errors.append(f"Failed to write output file: {e}")
        return 0

    summary = {
        "total_extracted": len(dois),
        "total_errors": len(errors),
        "failed_entries": errors
    }

    try:
        with open(EXTRACTION_SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"✓ Summary written to {EXTRACTION_SUMMARY_FILE}")
    except Exception as e:
        logger.error(f"Error writing summary: {e}")

    logger.info(f"Extracted {len(dois)} DOIs to {output_path}")
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
