"""
Application configuration, loaded from environment variables (via .env in
local development). Nothing sensitive lives here directly -- copy
.env.example to .env and adjust values there.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_DIR = BASE_DIR / "database"
DEVICES_FILE = DATABASE_DIR / "devices.json"
REPAIRS_FILE = DATABASE_DIR / "repairs.json"
PRICING_FILE = DATABASE_DIR / "pricing.json"

# Comma-separated list of allowed origins for CORS, e.g.
# "http://localhost:5173,https://your-production-domain.com"
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
CORS_ORIGINS = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

APP_NAME = "Mobile Repair Cost Estimator API"
APP_VERSION = "0.1.0"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
