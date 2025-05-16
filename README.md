# Sci-hub Downloader

Command-line tool to extract DOIs from BibTeX files and download academic papers via Sci-Hub. Built for researchers, students, and developers who want faster, automated access to scientific literature.

## Terminal Example

```bash
$ python main.py interactive

📘 Welcome to Sci-Hub Downloader (Terminal Mode)

1. 📄 Extract DOIs from a BibTeX file
2. 📥 Download PDFs from Sci-Hub
0. ❌ Exit
Enter your choice: 
```

## Features

### DOI Extraction:

- Parses a BibTeX file to extract all DOIs and save them to a text file.
- Generates an extraction summary in JSON format.

### PDF Download:

- Downloads PDFs using a working Sci‑Hub mirror from a configurable list of mirrors.
- Supports intelligent mirror selection and caching of working mirrors.
- Implements controlled delays between downloads to avoid IP blocking.
- Skips already downloaded papers to avoid duplicates.
- Maintains a record of successfully downloaded and failed DOIs.

### Modular Design:

- **Configuration (config.py):** Centralizes constants like file paths, download settings, and mirror URLs.
- **DOI Extraction Module (src/doi_extractor.py):** Handles extracting DOIs from your BibTeX data.
- **Downloader Module (src/downloader.py):** Handles fetching PDFs from Sci‑Hub with error handling.
- **Entry Point (main.py):** Provides a CLI interface with subcommands for extraction and downloading.

### User Interface:

- Command-line interface with three modes: extract, download, and interactive.
- Colored terminal output for better readability and user experience.
- Detailed progress tracking during downloads.

### Logging:

- Application logging uses a rotating file handler, storing logs in the logs/ directory.
- Comprehensive logging of all operations, errors, and download statuses.

## Project Structure

```
scihub-downloader/
├── config.py              # Centralized configuration settings
├── main.py                # Main entry point with CLI subcommands
├── requirements.txt       # List of required Python packages
├── README.md              # Project documentation
├── data/                  # Data directory
│   ├── meta-data-sample.bib  # Sample BibTeX file for input
│   ├── extracted_dois.txt    # File that stores the extracted DOIs
│   ├── failed_dois.txt       # Log file for DOIs that failed to download
│   └── library.txt           # Record of successfully downloaded DOIs
├── logs/                  # Log file directory
│   └── downloader.log     # Rotating log file for application logs
└── src/                   # Source code modules
    ├── __init__.py        # Package initialization and exports
    ├── core.py            # Simplified interface to main functionality
    ├── doi_extractor.py   # Module for extracting DOIs from BibTeX
    └── downloader.py      # Module for downloading PDFs from Sci-Hub
```

## Installation

### Clone the Repository:

```bash
git clone https://github.com/matiasrodlo/scihub-downloader.git
cd scihub-downloader
```

### Optional: Create and Activate a Virtual Environment:

```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

## How to Run the App

The project uses main.py as its entry‑point and supports three main modes: extract, download, and interactive.

### A. Extract DOIs from a BibTeX File

This command processes your BibTeX file (default path defined in config.py) and writes the extracted DOIs to a file.

#### Using Default Paths:

```bash
python main.py extract
```

#### Specifying Custom Paths:

```bash
python main.py extract --bibtex data/yourfile.bib --output data/extracted_dois.txt
```

### B. Download PDFs from Sci‑Hub

This command takes the DOI file (by default, the file generated from the extract command) and downloads the corresponding PDFs from Sci‑Hub.

#### Using Default Settings:

```bash
python main.py download
```

#### Specifying a Custom DOI File:

```bash
python main.py download --doi_file data/your_extracted_dois.txt
```

### C. Interactive Mode

For a more user-friendly experience, you can use the interactive terminal menu:

```bash
python main.py interactive
```

## Customization

You can customize various aspects of the application by modifying `config.py`:

### Change Sci-Hub Mirrors

Update the `SCI_HUB_URLS` list with current working mirrors:

```python
SCI_HUB_URLS = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    # Add new mirrors here
]
```

### Adjust Download Settings

Modify the delay between downloads or timeout settings:

```python
DOWNLOAD_TIMEOUT = 10  # Seconds
DELAY_MIN = 3          # Seconds between downloads
```

## Troubleshooting

### Module Not Found Error:

If you see an error like `ModuleNotFoundError: No module named 'src'`, ensure you are executing the command from the project's root directory (where main.py is located).

### Sci-Hub Mirror Issues:

If all mirrors fail:
1. Check your internet connection
2. Update the mirror list in config.py with current working Sci-Hub mirrors
3. Check if your IP has been temporarily blocked (consider using a VPN)

### PDF Download Failures:

If specific DOIs consistently fail to download:
1. Verify the DOI format is correct
2. Try manually accessing the paper on Sci-Hub to confirm availability
3. Check the failed_dois.txt file and logs for specific error messages

## Contributing

Feel free to fork this repository and submit pull requests. For significant changes, please open an issue first to discuss your ideas.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/matiasrodlo/scihub-downloader.git
cd scihub-downloader

# Set up virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests (if available)
python -m unittest discover tests
```

## License

This project is distributed under the MIT License.

## Acknowledgments

- **Sci‑Hub:** For providing access to academic papers.
- **Open Source Tools:** This project uses popular libraries such as requests, beautifulsoup4, colorama, and tqdm.
