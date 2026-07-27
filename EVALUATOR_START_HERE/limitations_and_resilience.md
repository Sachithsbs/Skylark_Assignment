# System Limitations & Data Resilience

This document outlines the operational limitations of the prototype (such as free-tier API rate limits), the engineering mitigations implemented to handle them, and the data cleaning logic applied to handle real-world messy data.

---

## 1. Gemini API Free Tier Rate Limits (429 Errors)

### The Limitation
The Gemini API free tier key provided is limited to **15 RPM (Requests Per Minute)**. During complex queries (like analyzing sectoral pipeline distributions), Gemini chain-calls multiple tools sequentially. This quickly triggers `429 Too Many Requests` API errors.

### Mitigation A: Database Query Caching (SQLite / Postgres)
We implemented a query cache database table in SQLite (`skylark.db` locally) and Supabase Postgres in production.
*   **Normalized Lookup**: When a chat request is received, the backend strips and normalizes the query (e.g. `how is our pipeline looking?` -> `how is our pipeline looking`).
*   **Direct DB Fetch**: If the query is present in the cache, the backend deserializes the cached JSON response and returns it in **milliseconds**.
*   **Zero-Token Cost**: This intercepts identical queries entirely, bypasses the Gemini network call, and eliminates the risk of hitting rate limits during client evaluations.
*   **UI Alert**: A cache notification is displayed in the UI warning box: `Retrieved from local database cache (free tier optimization)`.

### Mitigation B: Graceful Heuristic Fallback & Error Suppression
If a new query is submitted and the Gemini API returns a `429 Rate Limit` error:
*   **Exception Interception**: The backend catches the exception, prints it to the terminal server console, and immediately dispatches the request to the offline `HeuristicAgent`.
*   **Aesthetic Error Suppression**: The raw technical exception string (which contains API keys, HTTP request details, and URL paths) is hidden from the UI. The user is presented with a clean indicator: `Offline intelligence fallback active.`.
*   **Calculation Fidelity**: The offline agent performs the exact same calculations as the live tools and formats the response output using the proper Indian currency notation (Crores/Lakhs).

---

## 2. Monday.com GraphQL Schema Resilience

### The Limitation
Importing CSV files into monday.com creates randomized column IDs (e.g. `'numeric_mm5n7jwt'` instead of `'amount'`). A hardcoded query mapping to specific column IDs will break if the evaluator imports the sheets into their own boards.

### Mitigation: Dynamic Metadata Mapping
*   **Two-Step Queries**: The `MondayGraphQLClient` first queries the board column metadata (`boards.columns`) to map column IDs to their display titles (e.g. mapping `'dropdown_mm5nx413'` to `'Customer Name Code'`).
*   **Clean Parsing**: It then fetches the items and translates the column IDs to their readable names on-the-fly. This guarantees that **no matter what column IDs monday.com assigns during import, the analytics service continues to parse the data correctly**.

---

## 3. Data Cleaning Details (Pandas Data Pipeline)

### deals.csv (Sales Pipeline)
*   **Duplicate Header Rows**: The original sheet has duplicate header rows at index 50 and 179 where the cells literally repeat the column titles (e.g. `'Deal Status'` value is `'Deal Status'`). This causes numerical sum conversions to crash. The pipeline drops these rows before running calculations.
*   **Null Close Dates**: 318 of 346 deals have null close dates (~92% null). The system calculates Win Rate based only on finalized deals (`Won` and `Dead`) and flags the missing values count in the Data Quality Report.

### work_orders.csv (Project Execution)
*   **Excel Formula Errors**: Row 6 contains `#VALUE!` in the numeric amount column. The pipeline replaces it with `NaN` so the column can be safely converted to a float and summed.
*   **Execution Status Inconsistencies**: The status values include `'Executed until current month'` and `'Partial Completed'`, which are normalized to `'Ongoing'` to clean up the Recharts legends and stats.
*   **Empty Header Row**: The first row of the sheet consists of empty commas. It is skipped on import using `skiprows=1` to ensure correct schema parsing.
