import json
import re
import httpx
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from app.config import get_settings
from app.models.schemas import ChatMessage, ChatResponse
from app.services.analytics_service import AnalyticsService
from app.services.monday_service import MondayServiceBase
from app.database import QueryCache

# Gemini Tool declarations mapped to REST format
GEMINI_TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "get_pipeline_summary",
                "description": "Get deals pipeline summary, optionally filtered by sector. Use for questions about pipeline, deals, sales, prospects, opportunities, funnel, stages.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "sector": {
                            "type": "STRING",
                            "description": "Optional sector filter: Renewables, Mining, Railways, Powerline, Construction, Others"
                        }
                    }
                }
            },
            {
                "name": "get_revenue_summary",
                "description": "Get revenue, billing, collections, and accounts receivable summary. Use for questions about revenue, money, billing, AR, collections, financials.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            },
            {
                "name": "get_work_orders_health",
                "description": "Get work orders operational health, completion rates, delays, execution status. Use for questions about work orders, projects, operations, execution, delivery.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            },
            {
                "name": "get_data_quality_report",
                "description": "Get a report on data quality issues, missing values, and cleaning steps applied. Use when asked about data quality, missing data, completeness, or data issues.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            },
            {
                "name": "get_sector_performance",
                "description": "Compare performance across all sectors for both deals and work orders.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {}
                }
            }
        ]
    }
]

# OpenAI Tools
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pipeline_summary",
            "description": "Get deals pipeline summary, optionally filtered by sector. Use for questions about pipeline, deals, sales, prospects, opportunities, funnel, stages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector": {
                        "type": "string",
                        "description": "Optional sector filter: Renewables, Mining, Railways, Powerline, Construction, Others"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_revenue_summary",
            "description": "Get revenue, billing, collections, and accounts receivable summary. Use for questions about revenue, money, billing, AR, collections, financials.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_work_orders_health",
            "description": "Get work orders operational health, completion rates, delays, execution status. Use for questions about work orders, projects, operations, execution, delivery.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_data_quality_report",
            "description": "Get a report on data quality issues, missing values, and cleaning steps applied. Use when asked about data quality, missing data, completeness, or data issues.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sector_performance",
            "description": "Compare performance across all sectors for both deals and work orders.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

SYSTEM_PROMPT = """
You are Skylark BI — an elite business intelligence agent for Skylark Drones, a drone services company operating across Mining, Renewables, Railways, Powerline, and Construction sectors. You help founders and executives get crisp, actionable insights from their sales pipeline and work orders data.

Strict Rules:
1. Always call the appropriate tool first before answering.
2. Only call functions that are explicitly declared in the tools list (e.g. get_pipeline_summary, get_revenue_summary). Do not hallucinate or try to call other functions like 'list_deals' or 'get_deals_by_sector'.
3. Format numbers in Indian numbering: use Cr (crore) for values above 10 lakh, and L (lakh) for values 1-10 lakh, e.g. ₹2.3Cr, ₹8.5L.
4. Be concise and executive-level — use bullet points, not paragraphs.
5. Always mention data caveats or missing data issues if relevant.
6. If a question is ambiguous about sector or time period, make a reasonable assumption and state it.
7. If asked about something you cannot find in the tools, say so clearly.
"""

def format_inr(value: float) -> str:
    if value >= 10000000:
        return f"₹{value/10000000:.2f}Cr"
    elif value >= 100000:
        return f"₹{value/100000:.2f}L"
    else:
        return f"₹{value:,.0f}"

class HeuristicAgent:
    def __init__(self, analytics: AnalyticsService, deals_df, wo_df):
        self.analytics = analytics
        self.deals_df = deals_df
        self.wo_df = wo_df

    def process(self, message: str) -> ChatResponse:
        msg = message.lower()
        
        # Priority 0: Leadership report / executive briefing queries
        if any(w in msg for w in ['leadership', 'briefing', 'executive update', 'comprehensive report', 'update covering pipeline']):
            pipe = self.analytics.get_deal_summary(self.deals_df)
            rev = self.analytics.query_revenue_summary(self.wo_df, self.deals_df)
            wo = self.analytics.query_work_orders_health(self.wo_df)
            dq = self.analytics.get_data_quality_report(self.deals_df, self.wo_df, [])
            
            reply = f"""### Executive Briefing (Offline Mode)
* **Status**: Compiled from live database metrics.

#### 1. Sales & Pipeline Health
* **Total Sales Deals**: {pipe.get('total_deals')} total deals
  * **Won**: {pipe.get('won')} deals
  * **Open Pipeline**: {pipe.get('open')} active deals
  * **Win Rate**: {pipe.get('win_rate', 0)*100:.1f}%
* **Open Pipeline Value**: {format_inr(pipe.get('total_pipeline_value', 0))}
* **Average Deal Value**: {format_inr(pipe.get('avg_deal_value', 0))}

#### 2. Financials & Collections
* **Total Booked Value**: {format_inr(rev.get('total_contract_value', 0))}
* **Billed Revenue**: {format_inr(rev.get('billed_value', 0))}
* **Collected Amount**: {format_inr(rev.get('collected_value', 0))}
* **AR Outstanding (Accounts Receivable)**: {format_inr(rev.get('ar_outstanding', 0))}

#### 3. Operations & Delivery (Work Orders)
* **Active Work Orders**: {wo.get('total_ongoing')} projects ongoing.
* **Delayed Projects**: {wo.get('delayed_orders')} projects currently delayed past their probable end date.
* **Operational Completion Rate**: {wo.get('completion_rate', 0)*100:.1f}%

#### 4. Data Quality Warnings
* **Deals**: {dq.get('deals_missing_close_date')} deals are missing Close Date (A).
* **Work Orders**: {dq.get('wo_missing_amounts')} work orders are missing contract values.
"""
            return ChatResponse(reply=reply, data=rev, tool_used='get_revenue_summary')

        # Priority 1: Data quality queries
        if any(w in msg for w in ['data quality', 'missing', 'incomplete', 'clean', 'error', 'caveat']):
            data = self.analytics.get_data_quality_report(self.deals_df, self.wo_df, [])
            reply = f"Data Quality Report:\n- Deals Total Rows: {data.get('deals_total')}\n- Deals Missing Sector: {data.get('deals_missing_sector')}\n- Deals Missing Close Date (A): {data.get('deals_missing_close_date')} (approx {data.get('deals_missing_close_date') / data.get('deals_total') * 100:.1f}% of deals)\n- Work Orders Total Rows: {data.get('wo_total')}\n- Work Orders Missing Amount: {data.get('wo_missing_amounts')}\n- Excel Formula Errors Fixed: {data.get('wo_excel_errors_fixed')}\n- Work Orders Missing End Dates: {data.get('wo_missing_dates')}"
            return ChatResponse(reply=reply, data=data, tool_used='get_data_quality_report')
            
        # Priority 2: Revenue and billing queries (check before pipeline to avoid false matches on "won deals revenue")
        elif any(w in msg for w in ['revenue', 'billing', 'billed', 'collected', 'collection', 'ar', 'receivable', 'money', 'income', 'invoice']):
            data = self.analytics.query_revenue_summary(self.wo_df, self.deals_df)
            reply = f"Revenue Summary:\n- Total Contract Value: {format_inr(data.get('total_contract_value', 0))}\n- Billed Value: {format_inr(data.get('billed_value', 0))}\n- Collected Value: {format_inr(data.get('collected_value', 0))}\n- AR Outstanding (Amount Receivable): {format_inr(data.get('ar_outstanding', 0))}\n- Open Pipeline Value: {format_inr(data.get('total_pipeline', 0))}"
            return ChatResponse(reply=reply, data=data, tool_used='get_revenue_summary')
            
        # Priority 3: Work orders and project health queries
        elif any(w in msg for w in ['work order', 'project', 'execution', 'operational', 'delivery', 'delay', 'ongoing', 'completed']):
            data = self.analytics.query_work_orders_health(self.wo_df)
            reply = f"Work Orders Health Summary:\n- Total Ongoing Projects: {data.get('total_ongoing')}\n- Delayed Projects: {data.get('delayed_orders')}\n- Completion Rate: {data.get('completion_rate', 0)*100:.1f}%"
            return ChatResponse(reply=reply, data=data, tool_used='get_work_orders_health')
            
        # Priority 4: Sector performance (comparison)
        elif any(w in msg for w in ['sector breakdown', 'sectors performance', 'compare sectors', 'industry breakdown']):
            data = {"deals": self.analytics.get_sector_breakdown_deals(self.deals_df), "wo": self.analytics.get_sector_breakdown_wo(self.wo_df)}
            reply = "Sector Performance:\n- Renewables, Mining, Railways, Powerline, and Construction performance can be viewed in detail on the BI Dashboard."
            return ChatResponse(reply=reply, data=data, tool_used='get_sector_performance')
            
        # Priority 5: Deals / Sales pipeline queries
        elif any(w in msg for w in ['pipeline', 'deal', 'sales', 'prospect', 'funnel', 'stage', 'won', 'dead']):
            sector = None
            for s in ['renewables', 'mining', 'railways', 'powerline', 'construction', 'energy']:
                if s in msg:
                    # Map energy to renewables if mentioned
                    sector = 'Renewables' if s == 'energy' else s.title()
                    break
                    
            if sector:
                data = self.analytics.query_pipeline_by_sector(self.deals_df, sector)
                reply = f"Pipeline Summary for {sector}:\n- Total Deals: {data.get('total_deals')}\n- Won Deals: {data.get('won')}\n- Win Rate: {data.get('win_rate', 0)*100:.1f}%\n- Pipeline Value (Open Deals): {format_inr(data.get('total_pipeline_value', 0))}"
            else:
                data = self.analytics.get_deal_summary(self.deals_df)
                reply = f"Overall Pipeline Summary:\n- Total Deals: {data.get('total_deals')}\n- Won Deals: {data.get('won')}\n- Open Deals: {data.get('open')}\n- Win Rate: {data.get('win_rate', 0)*100:.1f}%\n- Pipeline Value (Open Deals): {format_inr(data.get('total_pipeline_value', 0))}"
            return ChatResponse(reply=reply, data=data, tool_used='get_pipeline_summary')
            
        else:
            # Smart default: return a brief high level summary instead of a refusal
            data = self.analytics.get_deal_summary(self.deals_df)
            reply = f"Hi! I am Skylark BI. I can answer business questions about sales or projects. Here is our high-level pipeline status:\n- Open Pipeline: {format_inr(data.get('total_pipeline_value', 0))}\n- Win Rate: {data.get('win_rate', 0)*100:.1f}%\nAsk me about 'revenue', 'delayed work orders', or sector-specific details!"
            return ChatResponse(reply=reply, data=None)

class AgentService:
    def __init__(self, analytics: AnalyticsService, monday_svc: MondayServiceBase):
        self.analytics = analytics
        self.monday_svc = monday_svc
        self.settings = get_settings()
        
        # Initialize clients if keys exist
        if self.settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            
        self.gemini_key = self.settings.GEMINI_API_KEY
        self.gemini_model = self.settings.GEMINI_MODEL

    def _dispatch_tool(self, tool_name: str, args: dict, deals_df, wo_df) -> dict:
        """Execute analytical calculations based on tool name and parameters."""
        if tool_name == "get_pipeline_summary":
            sector = args.get("sector")
            if sector:
                return self.analytics.query_pipeline_by_sector(deals_df, sector)
            return self.analytics.get_deal_summary(deals_df)
        elif tool_name == "get_revenue_summary":
            return self.analytics.query_revenue_summary(wo_df, deals_df)
        elif tool_name == "get_work_orders_health":
            return self.analytics.query_work_orders_health(wo_df)
        elif tool_name == "get_data_quality_report":
            return self.analytics.get_data_quality_report(deals_df, wo_df, [])
        elif tool_name == "get_sector_performance":
            return {
                "deals_by_sector": self.analytics.get_sector_breakdown_deals(deals_df),
                "wo_by_sector": self.analytics.get_sector_breakdown_wo(wo_df),
            }
        return {"error": f"Unknown tool: {tool_name}"}

    async def _chat_gemini(self, message: str, history: list[ChatMessage], deals_df, wo_df) -> ChatResponse:
        """Execute chat using Gemini REST interface with multi-turn function calling safety loop."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}

        # Map history turns
        contents = []
        for h in history[-6:]:
            role = "model" if h.role == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": h.content}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "tools": GEMINI_TOOLS
        }

        async with httpx.AsyncClient(timeout=30) as client:
            turns = 0
            last_data = None
            last_tool = None
            
            # Allow up to 5 reasoning turns for multi-tool execution chains
            max_turns = 5
            
            while turns < max_turns:
                # If we are on the very last turn, strip the tools to force Gemini to summarize
                if turns == max_turns - 1:
                    payload.pop("tools", None)

                r = await client.post(url, json=payload, headers=headers)
                r.raise_for_status()
                resp_json = r.json()

                candidates = resp_json.get("candidates", [])
                if not candidates:
                    return ChatResponse(reply="No response generated from Gemini.", data=None)

                first_content = candidates[0].get("content", {})
                parts = first_content.get("parts", [])
                
                if not parts:
                    return ChatResponse(reply="Empty response parts from Gemini.", data=None)

                # Check for functionCall
                if "functionCall" in parts[0]:
                    fc = parts[0]["functionCall"]
                    tool_name = fc.get("name")
                    args = fc.get("args") or {}

                    supported_tools = ["get_pipeline_summary", "get_revenue_summary", "get_work_orders_health", "get_data_quality_report", "get_sector_performance"]
                    if tool_name not in supported_tools:
                        # Feed back error to Gemini so it recovers from tool hallucinations
                        data_result = {"error": f"Tool '{tool_name}' is not supported. Please use only declared tools."}
                        tool_name_dispatch = tool_name
                    else:
                        # Execute real tool
                        data_result = self._dispatch_tool(tool_name, args, deals_df, wo_df)
                        tool_name_dispatch = tool_name
                        last_data = data_result
                        last_tool = tool_name_dispatch

                    # Append model turn and function response turns to payload contents
                    payload["contents"].append({
                        "role": "model",
                        "parts": parts
                    })
                    payload["contents"].append({
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": tool_name_dispatch,
                                    "response": {
                                        "output": data_result
                                    }
                                }
                            }
                        ]
                    })
                    
                    turns += 1
                else:
                    # Text response received
                    text = parts[0].get("text", "No text generated.")
                    
                    # Fetch warning items from data quality report
                    dq_report = self.analytics.get_data_quality_report(deals_df, wo_df, [])
                    dq_notes = [
                        f"Deals: {dq_report.get('deals_missing_close_date')} missing Close Dates.",
                        f"Work Orders: {dq_report.get('wo_missing_amounts')} missing contract values."
                    ]

                    return ChatResponse(
                        reply=text,
                        data=last_data,
                        data_quality_notes=dq_notes,
                        tool_used=last_tool
                    )
            
            # Reached max turns without a text response
            return ChatResponse(reply="Gemini reached maximum reasoning turns without generating a summary.", data=last_data, tool_used=last_tool)

    async def _chat_openai(self, message: str, history: list[ChatMessage], deals_df, wo_df) -> ChatResponse:
        """Execute chat using OpenAI client."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history[-6:]:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": message})

        tool_used = None
        data_result = None

        response = await self.openai_client.chat.completions.create(
            model=self.settings.OPENAI_MODEL,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)

            for tc in choice.message.tool_calls:
                tool_used = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                data_result = self._dispatch_tool(tool_used, args, deals_df, wo_df)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(data_result, default=str),
                })

            final_response = await self.openai_client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=messages,
            )
            reply = final_response.choices[0].message.content or ""
        else:
            reply = choice.message.content or ""

        dq_report = self.analytics.get_data_quality_report(deals_df, wo_df, [])
        dq_notes = [
            f"Deals: {dq_report.get('deals_missing_close_date')} missing Close Dates.",
            f"Work Orders: {dq_report.get('wo_missing_amounts')} missing contract values."
        ]

        return ChatResponse(
            reply=reply,
            data=data_result,
            data_quality_notes=dq_notes,
            tool_used=tool_used,
        )

    async def chat(self, message: str, history: list[ChatMessage], db: Session) -> ChatResponse:
        # 1. Normalize query for database cache lookup
        norm_query = re.sub(r'\s+', ' ', message.strip().lower())
        
        # 2. Check SQLite query cache first
        cached_record = db.query(QueryCache).filter(QueryCache.query == norm_query).first()
        if cached_record:
            try:
                cached_data = json.loads(cached_record.response)
                notes = cached_data.get("data_quality_notes", [])
                
                # Append caching notification so it is visible to the frontend
                if "Retrieved from local database cache (free tier optimization)" not in notes:
                    notes.insert(0, "Retrieved from local database cache (free tier optimization)")
                
                return ChatResponse(
                    reply=cached_data.get("reply"),
                    data=cached_data.get("data"),
                    data_quality_notes=notes,
                    tool_used=cached_data.get("tool_used")
                )
            except Exception as e:
                print(f"[Cache] Error reading cached record: {e}. Re-executing query.")
                
        # 3. Load deals and work orders dataframes
        deals_df, wo_df = await self.analytics._get_data(self.monday_svc)

        # 4. Route query to Gemini, OpenAI, or Heuristic Agent
        is_cached_eligible = True
        try:
            if self.gemini_key:
                # Prefer Gemini
                resp = await self._chat_gemini(message, history, deals_df, wo_df)
            elif self.openai_client:
                # Fallback to OpenAI
                resp = await self._chat_openai(message, history, deals_df, wo_df)
            else:
                # Fallback to Heuristic rules
                agent = HeuristicAgent(self.analytics, deals_df, wo_df)
                resp = agent.process(message)
                is_cached_eligible = False # don't cache static heuristic responses
        except Exception as exc:
            # Graceful error fallback to Heuristic
            print(f"[Agent] API call failed: {exc}. Falling back to Heuristics.")
            agent = HeuristicAgent(self.analytics, deals_df, wo_df)
            resp = agent.process(message)
            resp.data_quality_notes.insert(0, "Offline intelligence fallback active.")
            is_cached_eligible = False

        # 5. Save generated response to cache if eligible
        if is_cached_eligible and resp.data is not None:
            try:
                serialized = json.dumps({
                    "reply": resp.reply,
                    "data": resp.data,
                    "data_quality_notes": resp.data_quality_notes,
                    "tool_used": resp.tool_used
                })
                # SQLite upsert equivalent for cache
                db.query(QueryCache).filter(QueryCache.query == norm_query).delete()
                new_cache = QueryCache(query=norm_query, response=serialized)
                db.add(new_cache)
                db.commit()
                print(f"[Cache] Saved response for query: '{norm_query}'")
            except Exception as e:
                db.rollback()
                print(f"[Cache] Failed to save query response: {e}")

        return resp
