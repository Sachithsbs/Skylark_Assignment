# Evaluator Guide: Skylark Drones BI Agent

Welcome! This directory contains the complete set of deliverables, logs, and architectural specifications compiled for the reviewer. 

Please review the documents inside this folder first to understand the design system, technical choices, and setup steps.

---

## 📂 Folder Structure (Inside this directory)

| File | Purpose | Recommended Reading Order |
|---|---|---|
| **[README.md](file:///d:/Skylark/EVALUATOR_START_HERE/README.md)** | This document. Overview of the architecture, tech stack, and quickstart commands. | 1st |
| **[decision_log.md](file:///d:/Skylark/EVALUATOR_START_HERE/decision_log.md)** | **2-Page Max** Decision Log covering core design assumptions, trade-offs, and how "leadership reports" were implemented. | 2nd |
| **[limitations_and_resilience.md](file:///d:/Skylark/EVALUATOR_START_HERE/limitations_and_resilience.md)** | Complete breakdown of system limitations (Gemini free tier RPM limits), caching mitigations, and data resilience strategies. | 3rd |
| **[future_roadmap.md](file:///d:/Skylark/EVALUATOR_START_HERE/future_roadmap.md)** | Roadmap detailing advanced enhancements (streaming, persistent history, cross-board joins) if given more than 6 hours. | 4th |
| **[monday_setup_instructions.md](file:///d:/Skylark/EVALUATOR_START_HERE/monday_setup_instructions.md)** | Step-by-step guide to import sample CSVs into monday.com, extract board IDs, and configure credentials. | 5th |

---

## 🛠️ Tech Stack & Architecture Overview

The system is built as a highly decoupled Client-Server architecture designed to run on a local machine for development and scale to free hosting platforms (Vercel + Render + Supabase Postgres) for production:

```
                  ┌─────────────────────────────────┐
                  │       Vite + React Client       │
                  │   (Supabase Dark Theme UI)      │
                  └────────────────┬────────────────┘
                                   │ HTTP API Requests
                  ┌────────────────▼────────────────┐
                  │      FastAPI Backend Server     │
                  │     (AI Agent Orchestration)    │
                  └───────┬─────────────────┬───────┘
                          │                 │
    SQL Queries (ORM)     │                 │ GraphQL Queries
┌─────────────────────────▼─────┐     ┌─────▼─────────────────────────┐
│        Database Layer         │     │     monday.com Boards         │
│ • SQLite (Local Dev)          │     │ • Deals (Sales Pipeline)      │
│ • Supabase Postgres (Prod)    │     │ • Work Orders (Operations)    │
│ • Stores Users & Chat Cache   │     │ • Fetched dynamically via REST│
└───────────────────────────────┘     └───────────────────────────────┘
```

### 1. Frontend: React, TypeScript & Tailwind CSS
*   **Vite**: Selected for fast building and instant hot-module reloading.
*   **Tailwind CSS**: Custom themed using the **Supabase Dashboard Color System** (charcoal `#1e1e1e` cards, pitch-black `#121212` backgrounds, and `#3ecf8e` emerald green accents).
*   **Recharts**: Renders the 6 charts (KPI cards, Monthly Revenue Trend, Pipeline stages, Deals and Work Orders sector breakdowns, and Work Order status metrics) dynamically.
*   **Axios**: Configured with request/response interceptors to attach JWT headers and handle auto-logout on session expiration.

### 2. Backend: FastAPI & Pandas
*   **FastAPI**: Async Python framework with automatic Swagger docs.
*   **Uvicorn**: High-performance ASGI server.
*   **Pandas & NumPy**: Cleans messy data on the fly (replaces Excel formula errors like `#VALUE!`, standardizes sector strings, normalizes execution statuses, and removes duplicate header rows).

### 3. AI Agent: Gemini REST Integration
*   **Model**: `gemini-flash-latest` (queried via REST for zero package version conflicts).
*   **Multi-Turn Loop**: Implements up to 5 turns to execute analytical tool calling, with **unsupported tool-hallucination protection** (capturing calls like `list_deals` and returning error payloads to let Gemini recover).
*   **Fallback Heuristics**: Automatic switch to offline rules if Gemini is rate-limited (429), formatting response data exactly like Gemini.

### 4. Database & Caching: SQLAlchemy (SQLite / Supabase Postgres)
*   **Dynamic Adapters**: Connects to `sqlite:///./skylark.db` locally and switches to cloud PostgreSQL in production dynamically.
*   **Query Cache**: Saves successful LLM answers in the database. Identical subsequent requests load in milliseconds, bypassing the API to save free-tier tokens.
