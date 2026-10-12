import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Allows lightweight tests before optional dependencies are installed.
    def load_dotenv():
        return False


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data")).resolve()
DATABASE_PATH = DATA_DIR / "notebooklm.db"
VECTOR_DATABASE_PATH = DATA_DIR / "vectors.sqlite"
ARTIFACTS_PATH = DATA_DIR / "artifacts"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
PORT = int(os.getenv("PORT", "7860"))

for directory in (DATA_DIR, ARTIFACTS_PATH):
    directory.mkdir(parents=True, exist_ok=True)

