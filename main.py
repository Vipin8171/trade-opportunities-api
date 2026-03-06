<<<<<<< HEAD
"""
Trade Opportunities API — Main Application.

A FastAPI service that analyzes market data and provides trade opportunity
insights for specific sectors in India.

Author  : Vipin
Version : 1.0.0
"""
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse

from auth.authentication import (
    create_access_token,
    get_current_user,
    verify_user,
)
from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    HOST,
    PORT,
    SUPPORTED_SECTORS,
)
from middleware.rate_limiter import rate_limiter
from models.schemas import (
    AnalysisResponse,
    ErrorResponse,
    HealthResponse,
    Token,
    UserLogin,
    TokenData,
)
from services.ai_analyzer import ai_analyzer
from services.data_collector import data_collector
from services.report_generator import report_generator
from utils.logger import logger

# ─── In-Memory Session Store ────────────────────────────────────────────────────
sessions: dict = {}           # { username: { requests: int, last_active: str } }

# ─── Tag Ordering (this controls Swagger UI section order) ──────────────────────
tags_metadata = [
    {
        "name": "🔑 Authentication",
        "description": "Login to get your JWT token. Use the token for all protected endpoints.",
    },
    {
        "name": "🔍 Analysis",
        "description": "Main endpoint — analyze trade opportunities for any sector.",
    },
    {
        "name": "📋 Reports",
        "description": "View previously generated reports.",
    },
    {
        "name": "⚙️ General",
        "description": "Health check, sector list, and session info.",
    },
]

# ─── App Initialization ─────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_tags=tags_metadata, # ← controls tag order in Swagger
)

# ─── Template path for custom UI ────────────────────────────────────────────────
TEMPLATE_DIR = Path(__file__).parent / "webapp" / "templates"


# ─── Exception Handlers ─────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later.", "status": "error"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


# ─── Health Check ────────────────────────────────────────────────────────────────
@app.get(
    "/",
    response_model=HealthResponse,
    tags=["⚙️ General"],
    summary="Health Check",
)
async def health_check():
    """Root endpoint — returns API health status."""
    return HealthResponse(
        status="healthy",
        version=APP_VERSION,
        timestamp=datetime.now().isoformat(),
    )


# ─── Login ───────────────────────────────────────────────────────────────────────
@app.post(
    "/login",
    response_model=Token,
    tags=["🔑 Authentication"],
    summary="Login & get JWT token",
    responses={401: {"model": ErrorResponse}},
)
async def login(user: UserLogin):
    """
    Authenticate with username & password to receive a JWT token.

    **Demo Credentials:**
    - `admin` / `admin123`
    - `analyst` / `analyst123`
    - `guest` / `guest123`
    """
    verified = verify_user(user.username, user.password)
    if not verified:
        logger.warning(f"Failed login attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(data={"sub": verified["username"]})

    # Track session
    sessions[verified["username"]] = {
        "requests": 0,
        "last_active": datetime.now().isoformat(),
    }

    return Token(access_token=access_token)


# ─── List Supported Sectors ─────────────────────────────────────────────────────
@app.get(
    "/sectors",
    tags=["⚙️ General"],
    summary="List all supported sectors",
)
async def list_sectors():
    """Returns the list of supported sector names."""
    return {
        "supported_sectors": SUPPORTED_SECTORS,
        "total": len(SUPPORTED_SECTORS),
        "note": "You can also try other sector names — the API will attempt analysis for any sector.",
    }


# ─── Main Analysis Endpoint ─────────────────────────────────────────────────────
@app.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    tags=["🔍 Analysis"],
    summary="Analyze trade opportunities for a sector",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Invalid sector"},
        429: {"description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
)
async def analyze_sector(
    sector: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """
    **Main Endpoint** — Analyzes market data for the given sector and returns
    a structured markdown report with current trade opportunities in India.

    **Workflow:**
    1. Validates the sector input
    2. Checks rate limit for the user
    3. Searches for current market data & news (DuckDuckGo)
    4. Sends collected data to Google Gemini for analysis
    5. Returns a structured markdown report

    **Example:** `GET /analyze/pharmaceuticals`
    """
    username = current_user.username
    logger.info(f"[{username}] Analysis requested for sector: '{sector}'")

    # ── Input Validation ──
    sector_clean = sector.strip().lower()
    if len(sector_clean) < 2 or len(sector_clean) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sector name must be between 2 and 50 characters.",
        )

    if not sector_clean.replace(" ", "").isalpha():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sector name must contain only alphabetic characters.",
        )

    # ── Rate Limiting ──
    rate_limiter.check_rate_limit(request, username=username)

    # ── Update Session ──
    if username in sessions:
        sessions[username]["requests"] += 1
        sessions[username]["last_active"] = datetime.now().isoformat()

    # ── Step 1: Data Collection ──
    logger.info(f"[{username}] Step 1/3 — Collecting market data for '{sector_clean}'")
    try:
        collected_data = data_collector.collect_sector_data(sector_clean)
        formatted_data = data_collector.format_for_analysis(collected_data)
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to collect market data: {str(e)}",
        )

    # ── Step 2: AI Analysis ──
    logger.info(f"[{username}] Step 2/3 — Running Gemini AI analysis")
    try:
        report_md = ai_analyzer.analyze_sector(sector_clean, formatted_data)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis service error: {str(e)}",
        )

    # ── Step 3: Save Report ──
    logger.info(f"[{username}] Step 3/3 — Saving report")
    filename = report_generator.save_report(sector_clean, report_md)

    logger.info(f"[{username}] ✅ Analysis complete → {filename}")

    return AnalysisResponse(
        sector=sector_clean,
        report=report_md,
        generated_at=datetime.now().isoformat(),
        sources_count=collected_data["total_sources"],
        status="success",
    )


# ─── Report History ──────────────────────────────────────────────────────────────
@app.get(
    "/history",
    tags=["📋 Reports"],
    summary="View report generation history",
)
async def get_history(current_user: TokenData = Depends(get_current_user)):
    """Returns the history of all generated reports (current session)."""
    history = report_generator.get_history()
    return {
        "total_reports": report_generator.get_report_count(),
        "history": history,
    }


# ─── Session Info ────────────────────────────────────────────────────────────────
@app.get(
    "/session",
    tags=["⚙️ General"],
    summary="View current session info",
)
async def get_session(current_user: TokenData = Depends(get_current_user)):
    """Returns session info for the authenticated user."""
    username = current_user.username
    session = sessions.get(username, {})
    return {
        "username": username,
        "session": session,
        "total_reports_generated": report_generator.get_report_count(),
    }


# ─── Custom Web UI ───────────────────────────────────────────────────────────────
@app.get(
    "/ui",
    response_class=HTMLResponse,
    tags=["⚙️ General"],
    summary="Interactive Web UI",
    include_in_schema=False,
)
async def web_ui():
    """Serves the interactive web dashboard."""
    html_path = TEMPLATE_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting {APP_TITLE} v{APP_VERSION}")
    logger.info(f"🌐 Web UI:  http://localhost:{PORT}/ui")
    logger.info(f"📖 API Docs: http://localhost:{PORT}/docs")
    uvicorn.run("main:app", host=HOST, port=PORT)
=======
"""
Trade Opportunities API — Main Application.

A FastAPI service that analyzes market data and provides trade opportunity
insights for specific sectors in India.

Author  : Vipin
Version : 1.0.0
"""
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse

from auth.authentication import (
    create_access_token,
    get_current_user,
    verify_user,
)
from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    HOST,
    PORT,
    SUPPORTED_SECTORS,
)
from middleware.rate_limiter import rate_limiter
from models.schemas import (
    AnalysisResponse,
    ErrorResponse,
    HealthResponse,
    Token,
    UserLogin,
    TokenData,
)
from services.ai_analyzer import ai_analyzer
from services.data_collector import data_collector
from services.report_generator import report_generator
from utils.logger import logger

# ─── In-Memory Session Store ────────────────────────────────────────────────────
sessions: dict = {}           # { username: { requests: int, last_active: str } }

# ─── Tag Ordering (this controls Swagger UI section order) ──────────────────────
tags_metadata = [
    {
        "name": "🔑 Authentication",
        "description": "Login to get your JWT token. Use the token for all protected endpoints.",
    },
    {
        "name": "🔍 Analysis",
        "description": "Main endpoint — analyze trade opportunities for any sector.",
    },
    {
        "name": "📋 Reports",
        "description": "View previously generated reports.",
    },
    {
        "name": "⚙️ General",
        "description": "Health check, sector list, and session info.",
    },
]

# ─── App Initialization ─────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_tags=tags_metadata, # ← controls tag order in Swagger
)

# ─── Template path for custom UI ────────────────────────────────────────────────
TEMPLATE_DIR = Path(__file__).parent / "webapp" / "templates"


# ─── Exception Handlers ─────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later.", "status": "error"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


# ─── Health Check ────────────────────────────────────────────────────────────────
@app.get(
    "/",
    response_model=HealthResponse,
    tags=["⚙️ General"],
    summary="Health Check",
)
async def health_check():
    """Root endpoint — returns API health status."""
    return HealthResponse(
        status="healthy",
        version=APP_VERSION,
        timestamp=datetime.now().isoformat(),
    )


# ─── Login ───────────────────────────────────────────────────────────────────────
@app.post(
    "/login",
    response_model=Token,
    tags=["🔑 Authentication"],
    summary="Login & get JWT token",
    responses={401: {"model": ErrorResponse}},
)
async def login(user: UserLogin):
    """
    Authenticate with username & password to receive a JWT token.

    **Demo Credentials:**
    - `admin` / `admin123`
    - `analyst` / `analyst123`
    - `guest` / `guest123`
    """
    verified = verify_user(user.username, user.password)
    if not verified:
        logger.warning(f"Failed login attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(data={"sub": verified["username"]})

    # Track session
    sessions[verified["username"]] = {
        "requests": 0,
        "last_active": datetime.now().isoformat(),
    }

    return Token(access_token=access_token)


# ─── List Supported Sectors ─────────────────────────────────────────────────────
@app.get(
    "/sectors",
    tags=["⚙️ General"],
    summary="List all supported sectors",
)
async def list_sectors():
    """Returns the list of supported sector names."""
    return {
        "supported_sectors": SUPPORTED_SECTORS,
        "total": len(SUPPORTED_SECTORS),
        "note": "You can also try other sector names — the API will attempt analysis for any sector.",
    }


# ─── Main Analysis Endpoint ─────────────────────────────────────────────────────
@app.get(
    "/analyze/{sector}",
    response_model=AnalysisResponse,
    tags=["🔍 Analysis"],
    summary="Analyze trade opportunities for a sector",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Invalid sector"},
        429: {"description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
)
async def analyze_sector(
    sector: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """
    **Main Endpoint** — Analyzes market data for the given sector and returns
    a structured markdown report with current trade opportunities in India.

    **Workflow:**
    1. Validates the sector input
    2. Checks rate limit for the user
    3. Searches for current market data & news (DuckDuckGo)
    4. Sends collected data to Google Gemini for analysis
    5. Returns a structured markdown report

    **Example:** `GET /analyze/pharmaceuticals`
    """
    username = current_user.username
    logger.info(f"[{username}] Analysis requested for sector: '{sector}'")

    # ── Input Validation ──
    sector_clean = sector.strip().lower()
    if len(sector_clean) < 2 or len(sector_clean) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sector name must be between 2 and 50 characters.",
        )

    if not sector_clean.replace(" ", "").isalpha():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sector name must contain only alphabetic characters.",
        )

    # ── Rate Limiting ──
    rate_limiter.check_rate_limit(request, username=username)

    # ── Update Session ──
    if username in sessions:
        sessions[username]["requests"] += 1
        sessions[username]["last_active"] = datetime.now().isoformat()

    # ── Step 1: Data Collection ──
    logger.info(f"[{username}] Step 1/3 — Collecting market data for '{sector_clean}'")
    try:
        collected_data = data_collector.collect_sector_data(sector_clean)
        formatted_data = data_collector.format_for_analysis(collected_data)
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to collect market data: {str(e)}",
        )

    # ── Step 2: AI Analysis ──
    logger.info(f"[{username}] Step 2/3 — Running Gemini AI analysis")
    try:
        report_md = ai_analyzer.analyze_sector(sector_clean, formatted_data)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis service error: {str(e)}",
        )

    # ── Step 3: Save Report ──
    logger.info(f"[{username}] Step 3/3 — Saving report")
    filename = report_generator.save_report(sector_clean, report_md)

    logger.info(f"[{username}] ✅ Analysis complete → {filename}")

    return AnalysisResponse(
        sector=sector_clean,
        report=report_md,
        generated_at=datetime.now().isoformat(),
        sources_count=collected_data["total_sources"],
        status="success",
    )


# ─── Report History ──────────────────────────────────────────────────────────────
@app.get(
    "/history",
    tags=["📋 Reports"],
    summary="View report generation history",
)
async def get_history(current_user: TokenData = Depends(get_current_user)):
    """Returns the history of all generated reports (current session)."""
    history = report_generator.get_history()
    return {
        "total_reports": report_generator.get_report_count(),
        "history": history,
    }


# ─── Session Info ────────────────────────────────────────────────────────────────
@app.get(
    "/session",
    tags=["⚙️ General"],
    summary="View current session info",
)
async def get_session(current_user: TokenData = Depends(get_current_user)):
    """Returns session info for the authenticated user."""
    username = current_user.username
    session = sessions.get(username, {})
    return {
        "username": username,
        "session": session,
        "total_reports_generated": report_generator.get_report_count(),
    }


# ─── Custom Web UI ───────────────────────────────────────────────────────────────
@app.get(
    "/ui",
    response_class=HTMLResponse,
    tags=["⚙️ General"],
    summary="Interactive Web UI",
    include_in_schema=False,
)
async def web_ui():
    """Serves the interactive web dashboard."""
    html_path = TEMPLATE_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting {APP_TITLE} v{APP_VERSION}")
    logger.info(f"🌐 Web UI:  http://localhost:{PORT}/ui")
    logger.info(f"📖 API Docs: http://localhost:{PORT}/docs")
    uvicorn.run("main:app", host=HOST, port=PORT)
>>>>>>> e3bdfa0dc1e232c7a1a90430320437a724ae975b
