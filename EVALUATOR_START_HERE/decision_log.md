# Decision Log — Skylark Drones BI Agent

**Submission Name:** Technical Assignment Prototype  
**Timeline:** 6-hour prototype constraint  
**Target Architecture:** local development with zero-cost production hosting  

---

## 1. Key Assumptions Made

*   **REST/GraphQL API vs. MCP Integration**:  
    While the prompt suggested Model Context Protocol (MCP) or the GraphQL API, we chose the **GraphQL API**. MCP adds an extra layer of server orchestration and package dependencies that can introduce deployment vulnerabilities or errors on the evaluator's machine. GraphQL gives us direct control over headers, query scopes, and pagination via `httpx` and `tenacity`.
*   **Messy Data Normalization (On-The-Fly Cleaning)**:  
    We assumed the CSV files represent the exact raw, messy state of the boards. Instead of cleaning the data *prior* to importing into monday.com, we imported the spreadsheets as-is and shifted all data sanitization to the backend pipeline at runtime:
    *   *Deals duplicate headers*: Identified rows 50 and 179 where the content matches the header strings (`Deal Status == 'Deal Status'`) and dropped them programmatically.
    *   *Work Order formula errors*: Found `#VALUE!` cells in monetary columns and mapped them to `NaN` to prevent parse failures.
    *   *Work Order execution status*: Normalized the labels (e.g. `"Executed until current month"` is standard mapping for `"Ongoing"`).
    *   *Null Close Dates*: 318 of 346 deals are missing close dates (~92% null). The agent surfaces this limitation explicitly to the user via Data Quality Notes rather than guessing close dates.
*   **API Key Availability & Fallbacks**:  
    We assumed that the evaluator might run the code offline or without valid OpenAI/Gemini API keys. To ensure the application is testable instantly, we built a robust, prioritized **Heuristic Agent fallback** that replicates the exact tool-calling outputs and formats them in Indian numbering formats.

---

## 2. Trade-offs Chosen and Why

*   **SQLite locally, PostgreSQL in Production**:  
    For local development, SQLite requires no external service installation or docker containers. To support $0 hosting on Render/Vercel (where Render's free tier deletes local SQLite files on spin-down), we added dynamic SQLAlchemy dialect loading to connect to a **Supabase Postgres Free Tier** database in production with 0 code changes.
*   **Gemini REST API over OpenAI SDK**:  
    To support Gemini API keys natively (per user request) without installing heavy or version-sensitive Google GenAI packages, we implemented the connection using standard HTTPX REST requests. This guarantees the backend starts up on any machine with standard Python packages.
*   **In-Memory Pandas Caching for Dashboard Metrics**:  
    Querying large monday.com boards on every single chart render creates a bottleneck and risks rate limits. We warm up the cache by fetching and cleaning the boards once on server startup. Any subsequent dashboard render requests load from memory instantly.

---

## 3. How I Interpreted "Leadership Updates"

*   **Interpretation**: Leadership updates are high-level briefings presented to founders or board members. They should not consist of raw lists or tables. Instead, they must synthesize sales, revenue, outstanding collections, project execution statuses, and key operational risks into a cohesive, editable briefing.
*   **Implementation**: We built a dedicated **Leadership Briefing Workspace** tab.
    1.  **AI Summary Generation**: Clicking *Generate Report* invokes the agent with an executive briefing prompt.
    2.  **Rich Summarization**: Generates sections covering: Sales Pipeline Health, Financials & Collections, Operations & Delivery, and Data Integrity Caveats.
    3.  **Interactive Editor**: Founders can edit the text inline to add manual notes before exporting.
    4.  **Export Tools**: Supports *Copy to Clipboard* and *Save as .txt File* for sharing.
    5.  **Offline Robustness**: If the Gemini API is offline or rate-limited, the Heuristic Agent compiles a full Markdown report using calculated database values.

---

## 4. What I'd Do Differently with More Time

1.  **Cross-Board Joins on Deal Names**: Join Deals and Work Orders on `Deal Name` (52 names overlap) to flag which won deals haven't had work orders generated yet, or where billed amounts exceed the original deal value.
2.  **Streaming Chat Responses**: Use Server-Sent Events (SSE) to stream Gemini text token-by-token for a smoother chat experience.
3.  **Automated PDF Briefing Exports**: Generate PDF documents for leadership updates, complete with charts embedded, for direct emailing.
