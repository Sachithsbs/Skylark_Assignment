# 🚀 EVALUATOR: START IN THE [EVALUATOR_START_HERE](file:///d:/Skylark/EVALUATOR_START_HERE/) FOLDER!

All assignment deliverables, specifications, and setups are compiled inside the **[EVALUATOR_START_HERE](file:///d:/Skylark/EVALUATOR_START_HERE/)** directory for immediate access:
- **[2-Page Decision Log](file:///d:/Skylark/EVALUATOR_START_HERE/decision_log.md)**
- **[System Limitations & Caching](file:///d:/Skylark/EVALUATOR_START_HERE/limitations_and_resilience.md)**
- **[Future Roadmap](file:///d:/Skylark/EVALUATOR_START_HERE/future_roadmap.md)**
- **[Setup & Imports Guide](file:///d:/Skylark/EVALUATOR_START_HERE/monday_setup_instructions.md)**

---

# Skylark BI — Business Intelligence Agent

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  React + TypeScript + Tailwind CSS + Recharts           │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Chat   │ │ Dashboard │ │Leadership│ │ Quality  │  │
│  │Interface │ │  Charts  │ │  Report  │ │  Audit   │  │
│  └──────────┘ └───────────┘ └──────────┘ └──────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / Axios (JWT Bearer)
┌────────────────────────▼────────────────────────────────┐
│                      BACKEND                            │
│  FastAPI + Python + Uvicorn                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │              AgentService                       │    │
│  │  ┌──────────────────┐  ┌──────────────────────┐ │    │
│  │  │  OpenAI Tool     │  │  Heuristic Fallback  │ │    │
│  │  │  Calling Loop    │  │  (no key needed)     │ │    │
│  │  └────────┬─────────┘  └──────────────────────┘ │    │
│  └───────────┼─────────────────────────────────────┘    │
│              │                                          │
│  ┌───────────▼──────────────────────────────────────┐   │
│  │           AnalyticsService (Pandas)              │   │
│  │  • Data cleaning  • Missing value handling        │   │
│  │  • #VALUE! fixes  • Date normalization            │   │
│  │  • Pipeline KPIs  • Revenue metrics               │   │
│  └───────────┬──────────────────────────────────────┘   │
│              │                                          │
│  ┌───────────▼──────────────────────────────────────┐   │
│  │           MondayService (Dual Mode)              │   │
│  │  • Mock: CSV files    • Live: GraphQL API        │   │
│  │  • Tenacity retries   • Cursor pagination        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    monday.com       │
              │  GraphQL API v2     │
              │  Deals Board        │
              │  Work Orders Board  │
              └─────────────────────┘
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- CSV data files at `data/deals.csv` and `data/work_orders.csv` *(already included)*

### Backend

```bash
cd backend

# Install dependencies
python -m pip install -r requirements.txt

# Copy environment file and configure
copy .env.example .env
# Edit .env as needed (defaults work out-of-the-box with mock data)

# Start the API server
python run.py
```

Backend runs at: **http://localhost:8000**  
API docs (Swagger): **http://localhost:8000/docs**

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Login Credentials
| Username | Password     |
|----------|-------------|
| `founder` | `skylark2026` |

---

## Configuration

### Backend `.env` file

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `skylark-secret-key-for-dev-only-32chars` | JWT signing secret |
| `FOUNDER_USERNAME` | `founder` | Login username |
| `FOUNDER_PASSWORD` | `skylark2026` | Login password |
| `USE_MOCK_MONDAY` | `true` | Use CSV files instead of live API |
| `MONDAY_API_KEY` | *(empty)* | monday.com API v2 key |
| `DEALS_BOARD_ID` | *(empty)* | Board ID for Deals |
| `WORK_ORDERS_BOARD_ID` | *(empty)* | Board ID for Work Orders |
| `OPENAI_API_KEY` | *(empty)* | OpenAI key (optional — uses heuristic fallback if absent) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `DATA_DIR` | `../data` | Path to CSV data directory |
| `FRONTEND_URL` | `http://localhost:5173` | CORS allowed origin |

---

## monday.com Integration

### Step 1 — Import CSVs into monday.com

1. Go to your monday.com workspace
2. Create a new board: **"Deals"**  
   - Import `data/deals.csv`
   - Set column types: Text, Status, Date, Number, Dropdown
3. Create a new board: **"Work Orders"**  
   - Import `data/work_orders.csv` (skip the first empty row)
   - Set column types appropriately

### Step 2 — Get API Credentials

1. Go to monday.com → Profile → **Developers** → **My Access Tokens**
2. Generate a Personal API Token
3. Find your board IDs from the URL: `monday.com/boards/<BOARD_ID>`

### Step 3 — Switch to Live Mode

Update `.env`:
```env
USE_MOCK_MONDAY=false
MONDAY_API_KEY=your_api_token_here
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
```

The GraphQL client maps column values dynamically by their **title** — so it works with any column layout that matches the imported CSV column names.

---

## Data Cleaning Applied

The analytics service automatically handles the following real-world data quality issues found in the CSV files:

| Issue | Resolution |
|---|---|
| 2 duplicate header rows in Deals | Dropped automatically |
| `#VALUE!` Excel formula error in Work Orders amount column | Replaced with `NaN` |
| `Close Date (A)` missing for ~92% of deals | Flagged, reported in Data Quality view |
| Monetary columns as strings with commas | Stripped and converted to float |
| Mixed execution status labels | Normalized: `"Executed until current month"` → `"Ongoing"` |
| `Sector/service` casing inconsistencies | Standardized with `.str.title()` |
| Empty first row in work_orders.csv | Skipped with `skiprows=1` |

---

## Features

### 💬 Conversational BI Agent
- Ask founder-level questions in natural language
- Powered by OpenAI function-calling (GPT-4o-mini) OR heuristic fallback
- Suggested query pills for quick start
- Data quality warnings shown inline

### 📊 BI Dashboard
- KPI cards: Pipeline Value, Win Rate, Active WOs, AR Outstanding
- Revenue trend (monthly billed vs collected)
- Pipeline funnel by deal stage
- Sector performance donut charts (Deals + Work Orders)
- Work order operational health

### 📝 Leadership Report
- Auto-generate executive briefings from live data
- Edit inline, copy to clipboard, download as `.txt`

### 🛡️ Data Quality Audit
- Per-column completeness scores with color coding
- Cleaning steps audit log
- Overall data completeness score

---

## Project Structure

```
Skylark/
├── data/
│   ├── deals.csv              # Deals pipeline data
│   └── work_orders.csv        # Work orders tracker
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings (pydantic-settings)
│   │   ├── main.py            # FastAPI app, CORS, routers
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── auth.py        # /api/auth/login, /api/auth/me
│   │   │   ├── analytics.py   # /api/analytics/* endpoints
│   │   │   └── agent.py       # /api/agent/chat
│   │   ├── services/
│   │   │   ├── monday_service.py    # Mock + GraphQL clients
│   │   │   ├── analytics_service.py # Data cleaning + metrics
│   │   │   └── agent_service.py     # OpenAI + heuristic agent
│   │   └── utils/
│   │       └── security.py    # JWT + bcrypt auth
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DashboardCharts.tsx
│   │   │   ├── LeadershipReport.tsx
│   │   │   └── DataQualityDashboard.tsx
│   │   ├── services/api.ts
│   │   ├── context/AuthContext.tsx
│   │   ├── types/index.ts
│   │   └── App.tsx
│   └── package.json
├── decision_log.md
└── README.md
```
