import re

def extract_dois_from_bibtex(bibtex_path, output_path):
    with open(bibtex_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to match DOI entries
    dois = re.findall(r'DOI\s*=\s*[{"]([^}"]+)[}"]', content, re.IGNORECASE)

    if not dois:
        print("No DOIs found.")
        return

    # Save DOIs to a new text file
    with open(output_path, 'w', encoding='utf-8') as f:
        for doi in dois:
            f.write(doi.strip() + '\n')

    print(f"[+] Extracted {len(dois)} DOIs to {output_path}")

# Example usage
if __name__ == "__main__":
    extract_dois_from_bibtex("neuroscience.bib", "neuroscience_dois.txt")
