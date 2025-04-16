import threading
import os
import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from src import doi_extractor, downloader
from config import BIBTEX_FILE, EXTRACTED_DOIS_FILE, DEBUG_MODE, LOG_FILE

app = Flask(__name__, template_folder="templates")
app.secret_key = "your-secret-key"  # Replace with a secure key

def get_unique_log_file(prefix):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_dir = os.path.dirname(LOG_FILE)
    new_log = os.path.join(log_dir, f"downloader_{prefix}_{timestamp}.log")
    # Create an empty log file
    open(new_log, "w").close()
    return new_log

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract", methods=["GET"])
def extract():
    return render_template("extract.html", default_bibtex=BIBTEX_FILE, default_output=EXTRACTED_DOIS_FILE)

@app.route("/download", methods=["GET"])
def download():
    return render_template("download.html", default_doi=EXTRACTED_DOIS_FILE)

@app.route("/start_extraction", methods=["POST"])
def start_extraction():
    bibtex = request.form.get("bibtex") or BIBTEX_FILE
    output = request.form.get("output") or EXTRACTED_DOIS_FILE
    new_log_file = get_unique_log_file("extract")
    
    def run_extraction():
        try:
            doi_extractor.extract_dois_from_bibtex(bibtex, output)
        except Exception as e:
            with open(new_log_file, "a") as logf:
                logf.write(f"Extraction error: {e}\n")
    
    threading.Thread(target=run_extraction).start()
    # Return only the basename for easier client-side handling.
    return jsonify({"status": "Extraction started", "log_file": os.path.basename(new_log_file)})

@app.route("/start_download", methods=["POST"])
def start_download():
    doi_file = request.form.get("doi_file") or EXTRACTED_DOIS_FILE
    new_log_file = get_unique_log_file("download")
    
    def run_download():
        try:
            downloader.download_all_papers(doi_file)
        except Exception as e:
            with open(new_log_file, "a") as logf:
                logf.write(f"Download error: {e}\n")
    
    threading.Thread(target=run_download).start()
    return jsonify({"status": "Download started", "log_file": os.path.basename(new_log_file)})

@app.route("/get_logs")
def get_logs():
    # Expect a query parameter "log" with the log file's basename.
    log_filename = request.args.get("log")
    log_path = os.path.join(os.path.dirname(LOG_FILE), log_filename) if log_filename else LOG_FILE
    try:
        with open(log_path, "r") as f:
            log_content = f.read().strip().split("\n")
        # Return only the last 100 lines as JSON
        return jsonify({"logs": log_content[-100:]})
    except Exception as e:
        return jsonify({"logs": [f"Error reading log file: {e}"]})

@app.route("/logs", endpoint="logs_view")
def logs():
    # Use the "log" query parameter to display logs
    log_filename = request.args.get("log")
    log_path = os.path.join(os.path.dirname(LOG_FILE), log_filename) if log_filename else LOG_FILE
    try:
        with open(log_path, "r") as f:
            log_content = f.read().strip().split("\n")
        displayed_logs = "\n".join(log_content[-100:])
    except Exception as e:
        displayed_logs = f"Error reading log file: {e}"
    return render_template("logs.html", logs=displayed_logs)

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
