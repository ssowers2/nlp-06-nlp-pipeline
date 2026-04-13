from pathlib import Path

# ============================================================
# API CONFIGURATION
# ============================================================

# TODO: In your custom app, change the URL to work with a different page.
PAGE_URL: str = (
    "https://s7customguitars.com/services/"  # Apply Skills to Complete the Project
)

# Let them know who we are (and that we're doing educational web mining).
HTTP_REQUEST_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (educational-use; web-mining-course)"
}

# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT_PATH: Path = Path.cwd()
DATA_PATH: Path = ROOT_PATH / "data"
RAW_PATH: Path = DATA_PATH / "raw"
PROCESSED_PATH: Path = DATA_PATH / "processed"

# TODO: In your custom app, change the output file names from case_
# to something that represents YOUR custom project.
RAW_HTML_PATH: Path = (
    RAW_PATH / "sowers_raw_project.html"
)  # Apply Skills to Complete the Project
PROCESSED_CSV_PATH: Path = (
    PROCESSED_PATH / "sowers_processed_project.csv"
)  # Apply Skills to Complete the Project
