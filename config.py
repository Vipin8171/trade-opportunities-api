<<<<<<< HEAD
"""
Configuration settings for Trade Opportunities API.
"""
import os

# ─── API Keys ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "api-key-placeholder-2026")

# ─── JWT Settings ───────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "trade-opportunities-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ─── Rate Limiting ──────────────────────────────────────────────────────────────
RATE_LIMIT_REQUESTS = 10          # max requests
RATE_LIMIT_WINDOW_SECONDS = 60    # per window (seconds)

# ─── Supported Sectors ──────────────────────────────────────────────────────────
SUPPORTED_SECTORS = [
    "pharmaceuticals",
    "technology",
    "agriculture",
    "automobile",
    "banking",
    "energy",
    "textiles",
    "infrastructure",
    "fmcg",
    "telecom",
    "chemicals",
    "defence",
    "healthcare",
    "real estate",
    "education",
]

# ─── App Settings ───────────────────────────────────────────────────────────────
APP_TITLE = "Trade Opportunities API"
APP_DESCRIPTION = "Analyzes market data and provides trade opportunity insights for specific sectors in India."
APP_VERSION = "1.0.0"
HOST = "0.0.0.0"
PORT = 8000
=======
"""
Configuration settings for Trade Opportunities API.
"""
import os

# ─── API Keys ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "api-key-placeholder-2026")

# ─── JWT Settings ───────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "trade-opportunities-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ─── Rate Limiting ──────────────────────────────────────────────────────────────
RATE_LIMIT_REQUESTS = 10          # max requests
RATE_LIMIT_WINDOW_SECONDS = 60    # per window (seconds)

# ─── Supported Sectors ──────────────────────────────────────────────────────────
SUPPORTED_SECTORS = [
    "pharmaceuticals",
    "technology",
    "agriculture",
    "automobile",
    "banking",
    "energy",
    "textiles",
    "infrastructure",
    "fmcg",
    "telecom",
    "chemicals",
    "defence",
    "healthcare",
    "real estate",
    "education",
]

# ─── App Settings ───────────────────────────────────────────────────────────────
APP_TITLE = "Trade Opportunities API"
APP_DESCRIPTION = "Analyzes market data and provides trade opportunity insights for specific sectors in India."
APP_VERSION = "1.0.0"
HOST = "0.0.0.0"
PORT = 8000
>>>>>>> e3bdfa0dc1e232c7a1a90430320437a724ae975b
