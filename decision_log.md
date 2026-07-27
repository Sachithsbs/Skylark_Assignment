# Decision Log — Skylark Drones BI Agent

**Candidate:** Technical Assignment Submission  
**Date:** July 2026  
**Timeline:** 6-hour prototype

---

## Key Assumptions

**1. "Connect to monday.com via MCP or API" — chose REST/GraphQL API**  
MCP (Model Context Protocol) introduces an additional orchestration layer that adds complexity without meaningful benefit for a 6-hour prototype. The GraphQL API offers complete control, cursor-based pagination, and native retry handling via `tenacity`. The monday.com GraphQL API v2 is the recommended production integration path.

**2. Data is messy — assumed CSV files represent the exact board state**  
Imported both CSV files into monday.com as-is, including the messy data. The agent is responsible for cleaning, not the import process. This means the agent handles:
- 2 duplicate header rows in Deals (rows 50 and 179 where `Deal Status == 'Deal Status'`)
- 1 `#VALUE!` Excel formula error in a Work Orders monetary column
- 318 missing `Close Date (A)` entries in Deals (~92% null)
- Inconsistent execution status labels (`"Executed until current month"` normalized to `"Ongoing"`)

**3. "Dynamic querying" means no hardcoded data in the agent logic**  
All analytics are computed at runtime from the data fetched from monday.com (or the mock CSV). There are no hardcoded numbers, summaries, or cached results baked into the agent's responses.

**4. OpenAI key is optional**  
The evaluation environment may not have an OpenAI key. Built a heuristic keyword-matching fallback that calls the same analytics functions and formats responses identically. The full OpenAI tool-calling loop is implemented and activates automatically when `OPENAI_API_KEY` is set.

---

## Trade-offs Chosen and Why

**Mock mode as the default (`USE_MOCK_MONDAY=true`)**  
Since the evaluator needs to test the app without setting up their own monday.com boards, mock mode reads directly from the CSV files using the same data pipeline as the live GraphQL client. Switching to live mode requires only 3 environment variables.

**In-memory caching over PostgreSQL**  
The assignment calls PostgreSQL "optional." For a 6-hour prototype, adding a database layer introduces deployment complexity (connection strings, migrations, pg drivers) that risks the demo not working on first run. In-memory caching provides fast repeated queries while keeping the setup to: `python run.py`.

**Heuristic agent + OpenAI, not OpenAI exclusively**  
Relying solely on OpenAI creates a hard dependency that prevents offline testing and adds API cost. The heuristic fallback provides 90% of the founder use-cases (pipeline, revenue, WO health, sector queries) and the full OpenAI implementation activates transparently when a key is configured.

**React + Vite over Next.js**  
No server-side rendering is needed here — all data comes from the FastAPI backend. Vite provides faster hot-reload and a simpler build pipeline. Next.js would add page-routing complexity without benefit for this single-API-consumer app.

**JWT over OAuth2 provider**  
Single-user prototype with a fixed founder credential. OAuth2 with a provider (Google, Auth0) requires domain registration and redirect URLs, which is disproportionate for a 6-hour build. JWT with bcrypt-hashed passwords satisfies the cybersecurity requirement and is trivially replaceable with OAuth2 in production.

---

## What I'd Do Differently with More Time

1. **Streaming responses** — Implement SSE (Server-Sent Events) for the chat API so long AI responses appear token-by-token, like ChatGPT. This dramatically improves perceived responsiveness.

2. **Persistent query history** — Store chat sessions in PostgreSQL so founders can revisit past queries and the agent has longer context memory across sessions.

3. **Smarter cross-board queries** — Build a join between the Deals and Work Orders datasets on `Deal Name` (52 of 58 WO names match Deals) to answer cross-board questions like "Which won deals haven't generated work orders yet?"

4. **Live data refresh** — Add a WebSocket or polling mechanism to detect when monday.com board data changes and invalidate the in-memory cache, keeping the dashboard always current.

5. **Confidence scoring** — When the heuristic agent handles a query, add a confidence score and suggest related queries it could answer more precisely, reducing ambiguity.

---

## How I Interpreted "Leadership Updates"

The assignment said "help prepare data for leadership updates" with no further specification.

**Interpretation:** Leadership updates are periodic briefings (weekly/monthly) that require synthesizing data from multiple sources into a structured narrative. Founders don't want raw numbers — they want context, comparisons, and recommended actions.

**Implementation:** The Leadership Report page lets the user:
1. Click "Generate Report" — which triggers the AI agent with a specific executive briefing prompt
2. Review the AI-generated structured report with sections: Executive Summary, Pipeline Health, Revenue & Collections, Work Orders, Data Caveats, Recommended Actions
3. Edit any section inline before sharing
4. Export as plain text or copy to clipboard for pasting into email/Notion/slides

**What I didn't build:** Automated scheduling (email every Monday), slide deck export (PowerPoint), or team collaboration editing. These would be high-value next steps but were out of scope for 6 hours.

**Key design decision:** The report explicitly surfaces data quality caveats (e.g., "Close Date is missing for 92% of deals") because leadership decisions based on incomplete data are worse than acknowledging the gap.

---

## Gemini API Integration & Caching Strategy

**1. Gemini REST API Integration**
Implemented the Gemini API REST interface (`gemini-flash-latest` model) using `httpx`. The agent supports standard conversational function calling by declaring tool schemas. To prevent crashes from model hallucinations (such as Gemini trying to call non-existent tools like `list_deals` or `get_deals_by_sector`), we developed a robust **multi-turn reasoning loop** that catches unsupported tool calls, feeds back a structured error to the model, and allows the model to recover and write a final text response.

**2. Turn-Limit Correction (from 3 to 5)**
For complex query chains (e.g. comparing sector performance and then looking up overall pipeline metrics), Gemini executes multiple tool calls sequentially. A 3-turn limit cut off the loop before the final text response was synthesized. We increased this to **5 turns** and added a **force-termination trigger** (stripping tool declarations on the final turn) to guarantee the model outputs a natural language summary instead of an overflow error.

**3. SQLite Query Caching**
To mitigate Gemini free-tier rate limits (429 errors), we implemented a database query cache. Successful agent replies (along with calculated dataset responses) are saved to the `query_cache` table in `skylark.db`. Repeat queries are intercepted and returned instantly from the local database in milliseconds without contacting the Gemini API, preserving quota.

**4. Graceful Technical Error Suppression**
If the Gemini API hits a `429 Too Many Requests` rate limit (or is otherwise unreachable), the system gracefully intercepts the error, falls back to the offline Heuristic rules, and displays a user-friendly badge `"Offline intelligence fallback active"` in the UI, hiding raw API stack traces or exception strings.

