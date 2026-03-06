<<<<<<< HEAD
# 📊 Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India. It uses **DuckDuckGo** for real-time data collection and **Google Gemini AI** for intelligent analysis.

---

## 🏗️ Project Structure

```
Assignment_Python_Appscrip/
│
├── main.py                          # FastAPI application entry point
├── config.py                        # Configuration & settings
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── auth/
│   └── authentication.py            # JWT authentication logic
│
├── middleware/
│   └── rate_limiter.py              # Rate limiting (sliding window)
│
├── models/
│   └── schemas.py                   # Pydantic request/response schemas
│
├── services/
│   ├── data_collector.py            # DuckDuckGo search integration
│   ├── ai_analyzer.py               # Google Gemini API integration
│   └── report_generator.py          # Markdown report saving & history
│
├── utils/
│   └── logger.py                    # Logging configuration
│
├── webapp/
│   └── templates/
│       └── index.html               # Interactive web dashboard
│
└── reports/                         # Auto-generated markdown reports
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### 2. Install Dependencies

```bash
cd Assignment_Python_Appscrip
pip install -r requirements.txt
```

### 3. Set API Key (Optional — already configured in config.py)

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

### 4. Run the Server

```bash
python main.py
```

The server starts at `http://localhost:8000`

### 5. Open the App

- **Web UI (recommended):** [http://localhost:8000/ui](http://localhost:8000/ui)
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Endpoints

| Method | Endpoint             | Auth Required | Description                            |
|--------|----------------------|---------------|----------------------------------------|
| GET    | `/`                  | ❌            | Health check                           |
| POST   | `/login`             | ❌            | Get JWT token                          |
| GET    | `/sectors`           | ❌            | List supported sectors                 |
| GET    | `/analyze/{sector}`  | ✅ Bearer     | **Main endpoint** — Sector analysis    |
| GET    | `/history`           | ✅ Bearer     | View report generation history         |
| GET    | `/session`           | ✅ Bearer     | View current session info              |
| GET    | `/ui`                | ❌            | Interactive web dashboard              |

---

## 🚀 Usage Guide

### Step 1: Login to get a token

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### Step 2: Analyze a sector

```bash
curl -X GET http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "sector": "pharmaceuticals",
  "report": "# Trade Opportunities Report: Pharmaceuticals...",
  "generated_at": "2026-03-05T10:30:00",
  "sources_count": 42,
  "status": "success"
}
```

The `report` field contains a full markdown analysis that can be saved as a `.md` file.

### Step 3: Check history

```bash
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer <your_token>"
```

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication.

| Username  | Password      | Role   |
|-----------|---------------|--------|
| admin     | admin123      | admin  |
| analyst   | analyst123    | user   |
| guest     | guest123      | guest  |

Tokens expire after **60 minutes**.

---

## 🛡️ Rate Limiting

- **10 requests** per **60-second** sliding window per user
- Rate limit is tracked per authenticated username (or IP for unauthenticated)
- Returns `429 Too Many Requests` when exceeded with `retry_after_seconds`

---

## 🧰 Technical Details

| Component           | Technology                       |
|---------------------|----------------------------------|
| **Framework**       | FastAPI (async)                  |
| **Authentication**  | JWT via python-jose              |
| **AI/LLM**         | Google Gemini 2.0 Flash          |
| **Web Search**      | DuckDuckGo (duckduckgo-search)   |
| **Validation**      | Pydantic v2                      |
| **Storage**         | In-memory (dict-based)           |
| **Rate Limiting**   | Custom sliding window            |
| **Logging**         | Python logging (structured)      |

### Core Workflow
1. User authenticates via `/login` → receives JWT
2. User hits `/analyze/{sector}` with the token
3. System searches DuckDuckGo for market data & news (7 targeted queries)
4. Collected data is sent to Gemini AI with a structured prompt
5. Gemini generates a comprehensive markdown report
6. Report is saved to `reports/` folder and returned to user

---

## 📂 Generated Reports

Reports are automatically saved in the `reports/` directory:
```
reports/
├── pharmaceuticals_report_20260305_103000.md
├── technology_report_20260305_104500.md
└── agriculture_report_20260305_110000.md
```

---

## ⚠️ Error Handling

| Status Code | Meaning                    |
|-------------|----------------------------|
| 200         | Success                    |
| 401         | Invalid/expired token      |
| 422         | Invalid sector input       |
| 429         | Rate limit exceeded        |
| 502         | External API failure       |
| 500         | Internal server error      |

---

## 📝 Notes

- Reports contain real-time data — results will vary based on current news
- DuckDuckGo search doesn't require an API key (free & unlimited)
- The Gemini API free tier supports sufficient requests for testing
- All data is stored in-memory (resets on server restart)

---

## 👤 Author

**Vipin** — Python Developer

---

*Built as part of Appscrip Python Developer Assignment*
=======
# 📊 Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India. It uses **DuckDuckGo** for real-time data collection and **Google Gemini AI** for intelligent analysis.

---

## 🏗️ Project Structure

```
Assignment_Python_Appscrip/
│
├── main.py                          # FastAPI application entry point
├── config.py                        # Configuration & settings
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── auth/
│   └── authentication.py            # JWT authentication logic
│
├── middleware/
│   └── rate_limiter.py              # Rate limiting (sliding window)
│
├── models/
│   └── schemas.py                   # Pydantic request/response schemas
│
├── services/
│   ├── data_collector.py            # DuckDuckGo search integration
│   ├── ai_analyzer.py               # Google Gemini API integration
│   └── report_generator.py          # Markdown report saving & history
│
├── utils/
│   └── logger.py                    # Logging configuration
│
├── webapp/
│   └── templates/
│       └── index.html               # Interactive web dashboard
│
└── reports/                         # Auto-generated markdown reports
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### 2. Install Dependencies

```bash
cd Assignment_Python_Appscrip
pip install -r requirements.txt
```

### 3. Set API Key (Optional — already configured in config.py)

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

### 4. Run the Server

```bash
python main.py
```

The server starts at `http://localhost:8000`

### 5. Open the App

- **Web UI (recommended):** [http://localhost:8000/ui](http://localhost:8000/ui)
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Endpoints

| Method | Endpoint             | Auth Required | Description                            |
|--------|----------------------|---------------|----------------------------------------|
| GET    | `/`                  | ❌            | Health check                           |
| POST   | `/login`             | ❌            | Get JWT token                          |
| GET    | `/sectors`           | ❌            | List supported sectors                 |
| GET    | `/analyze/{sector}`  | ✅ Bearer     | **Main endpoint** — Sector analysis    |
| GET    | `/history`           | ✅ Bearer     | View report generation history         |
| GET    | `/session`           | ✅ Bearer     | View current session info              |
| GET    | `/ui`                | ❌            | Interactive web dashboard              |

---

## 🚀 Usage Guide

### Step 1: Login to get a token

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### Step 2: Analyze a sector

```bash
curl -X GET http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "sector": "pharmaceuticals",
  "report": "# Trade Opportunities Report: Pharmaceuticals...",
  "generated_at": "2026-03-05T10:30:00",
  "sources_count": 42,
  "status": "success"
}
```

The `report` field contains a full markdown analysis that can be saved as a `.md` file.

### Step 3: Check history

```bash
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer <your_token>"
```

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication.

| Username  | Password      | Role   |
|-----------|---------------|--------|
| admin     | admin123      | admin  |
| analyst   | analyst123    | user   |
| guest     | guest123      | guest  |

Tokens expire after **60 minutes**.

---

## 🛡️ Rate Limiting

- **10 requests** per **60-second** sliding window per user
- Rate limit is tracked per authenticated username (or IP for unauthenticated)
- Returns `429 Too Many Requests` when exceeded with `retry_after_seconds`

---

## 🧰 Technical Details

| Component           | Technology                       |
|---------------------|----------------------------------|
| **Framework**       | FastAPI (async)                  |
| **Authentication**  | JWT via python-jose              |
| **AI/LLM**         | Google Gemini 2.0 Flash          |
| **Web Search**      | DuckDuckGo (duckduckgo-search)   |
| **Validation**      | Pydantic v2                      |
| **Storage**         | In-memory (dict-based)           |
| **Rate Limiting**   | Custom sliding window            |
| **Logging**         | Python logging (structured)      |

### Core Workflow
1. User authenticates via `/login` → receives JWT
2. User hits `/analyze/{sector}` with the token
3. System searches DuckDuckGo for market data & news (7 targeted queries)
4. Collected data is sent to Gemini AI with a structured prompt
5. Gemini generates a comprehensive markdown report
6. Report is saved to `reports/` folder and returned to user

---

## 📂 Generated Reports

Reports are automatically saved in the `reports/` directory:
```
reports/
├── pharmaceuticals_report_20260305_103000.md
├── technology_report_20260305_104500.md
└── agriculture_report_20260305_110000.md
```

---

## ⚠️ Error Handling

| Status Code | Meaning                    |
|-------------|----------------------------|
| 200         | Success                    |
| 401         | Invalid/expired token      |
| 422         | Invalid sector input       |
| 429         | Rate limit exceeded        |
| 502         | External API failure       |
| 500         | Internal server error      |

---

## 📝 Notes

- Reports contain real-time data — results will vary based on current news
- DuckDuckGo search doesn't require an API key (free & unlimited)
- The Gemini API free tier supports sufficient requests for testing
- All data is stored in-memory (resets on server restart)

---

## 👤 Author

**Vipin** — Python Developer

---

*Built as part of Appscrip Python Developer Assignment*
>>>>>>> e3bdfa0dc1e232c7a1a90430320437a724ae975b
