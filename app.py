import threading
import os
import datetime
import json
import re
import sys
from flask import Flask, request, render_template, url_for, jsonify

# Add src/ to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from config import (
    BIBTEX_FILE,
    EXTRACTED_DOIS_FILE,
    DEBUG_MODE,
    LOG_FILE,
    EXTRACTION_SUMMARY_FILE,
    get_logger
)
from core import extract, download

app = Flask(__name__, template_folder="templates")
app.secret_key = "your-secret-key"
logger = get_logger("flask")

def get_unique_log_file(prefix):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = os.path.dirname(LOG_FILE)
    new_log = os.path.join(log_dir, f"downloader_{prefix}_{timestamp}.log")
    open(new_log, "w").close()
    return new_log

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract", methods=["GET"])
def extract_view():
    return render_template("extract.html", default_bibtex=BIBTEX_FILE, default_output=EXTRACTED_DOIS_FILE)

@app.route("/download", methods=["GET"])
def download_view():
    return render_template("download.html", default_doi=EXTRACTED_DOIS_FILE)

@app.route("/start_extraction", methods=["POST"])
def start_extraction():
    bibtex = request.form.get("bibtex") or BIBTEX_FILE
    output = request.form.get("output") or EXTRACTED_DOIS_FILE
    new_log_file = get_unique_log_file("extract")

    def run_extraction():
        try:
            extract(bibtex, output)
        except Exception as e:
            logger.error(f"Extraction error: {e}")

    threading.Thread(target=run_extraction).start()
    return jsonify({
        "status": "Extraction started",
        "log_file": os.path.basename(new_log_file)
    })

@app.route("/start_download", methods=["POST"])
def start_download():
    doi_file = request.form.get("doi_file") or EXTRACTED_DOIS_FILE
    new_log_file = get_unique_log_file("download")

    def run_download():
        try:
            download(doi_file, new_log_file)
        except Exception as e:
            logger.error(f"Download error: {e}")

    threading.Thread(target=run_download).start()
    return jsonify({
        "status": "Download started",
        "log_file": os.path.basename(new_log_file)
    })

@app.route("/get_logs")
def get_logs():
    log_filename = request.args.get("log")
    log_path = os.path.join(os.path.dirname(LOG_FILE), log_filename) if log_filename else LOG_FILE

    try:
        with open(log_path, "r") as f:
            log_lines = f.read().strip().split("\n")

        count, total, skipped, errors = 0, 0, 0, 0

        for line in log_lines:
            if "DOWNLOADED:" in line:
                match = re.search(r"DOWNLOADED:\s*(\d+)", line)
                if match:
                    count = max(count, int(match.group(1)))
            elif "📦 TOTAL:" in line and total == 0:
                match = re.search(r"TOTAL:\s*(\d+)", line)
                if match:
                    total = int(match.group(1))
            elif "⚠️ SKIPPED COUNT:" in line:
                match = re.search(r"SKIPPED COUNT:\s*(\d+)", line)
                if match:
                    skipped = int(match.group(1))

        errors = sum(1 for line in log_lines if "FINAL FAILURE:" in line)
        progress = int(((count + skipped) / total) * 100) if total else 0

        return jsonify({
            "logs": log_lines[-100:],
            "count": count,
            "skipped": skipped,
            "total": total,
            "errors": errors,
            "progress": progress
        })

    except Exception as e:
        return jsonify({
            "logs": [f"Error reading log file: {e}"],
            "count": 0,
            "skipped": 0,
            "total": 0,
            "errors": 0,
            "progress": 0
        })

@app.route("/logs", endpoint="logs_view")
def logs():
    log_filename = request.args.get("log")
    log_path = os.path.join(os.path.dirname(LOG_FILE), log_filename) if log_filename else LOG_FILE
    try:
        with open(log_path, "r") as f:
            log_content = f.read().strip().split("\n")
        displayed_logs = "\n".join(log_content[-100:])
    except Exception as e:
        displayed_logs = f"Error reading log file: {e}"
    return render_template("logs.html", logs=displayed_logs)

@app.route("/extraction_summary")
def extraction_summary():
    try:
        with open(EXTRACTION_SUMMARY_FILE, "r") as f:
            summary = json.load(f)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": f"Could not retrieve summary: {e}"})

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
