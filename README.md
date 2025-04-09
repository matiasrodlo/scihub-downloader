# GetPapers

GetPapers is a command‑line application for managing academic papers by extracting DOIs from a BibTeX file and downloading the corresponding PDFs from Sci‑Hub. The project is organized into modular components to ensure maintainability, ease of configuration, and efficient execution.

## Features

### DOI Extraction:

- Parses a BibTeX file to extract all DOIs and save them to a text file.

### PDF Download:

- Downloads PDFs using a working Sci‑Hub mirror based on the list of extracted DOIs.
- Supports concurrent downloads with controlled delays for reliability.

### Modular Design:

- **Configuration (config.py):** Centralizes constants like file paths, download settings, and mirror URLs.
- **DOI Extraction Module (src/doi_extractor.py):** Handles extracting DOIs from your BibTeX data.
- **Downloader Module (src/downloader.py):** Handles fetching PDFs from Sci‑Hub.
- **Entry Point (main.py):** Provides a CLI interface with subcommands for extraction and downloading.

### Logging:

- Application logging uses a rotating file handler, storing logs in the logs/ directory.

## Project Structure

```
get-papers/
├── config.py              # Centralized configuration settings
├── main.py                # Main entry point with CLI subcommands
├── requirements.txt       # List of required Python packages
├── README.md              # Project documentation
├── data/                  # Data directory
│   ├── meta-data-sample.bib  # Sample BibTeX file for input
│   ├── extracted_dois.txt    # File that will store the extracted DOIs
│   ├── failed_dois.txt       # Log file for DOIs that failed to download
│   └── library.txt           # Record of successfully downloaded DOIs
├── logs/                  # Log file directory
│   └── downloader.log     # Rotating log file for application logs
└── src/                   # Source code modules
    ├── __init__.py        # Package initialization and exports
    ├── doi_extractor.py   # Module for extracting DOIs from BibTeX
    └── downloader.py      # Module for downloading PDFs from Sci-Hub
```

## Installation

### Clone the Repository:

```bash
git clone https://github.com/matiasrodlo/get-papers.git
cd get-papers
```

### Optional: Create and Activate a Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

## How to Run the App

The project uses main.py as its entry‑point and supports two main subcommands: extract and download.

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

## Troubleshooting

### Module Not Found Error:

If you see an error like `ModuleNotFoundError: No module named 'src'`, ensure you are executing the command from the project's root directory (where main.py is located). If necessary, modify main.py to add the project root to sys.path.

### Sci-Hub Mirror Issues:

The program automatically selects a working Sci‑Hub mirror from the list defined in config.py. If the application fails to find a working mirror, verify your internet connection or update the mirror list in config.py.

## Contributing

Feel free to fork this repository and submit pull requests. For significant changes, please open an issue first to discuss your ideas.

## License

This project is distributed under the MIT License.

## Acknowledgments

- **Sci‑Hub:** For providing access to academic papers.
- **Open Source Tools:** This project uses popular libraries such as requests, beautifulsoup4, and tqdm.
