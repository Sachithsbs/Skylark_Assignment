import asyncio
import httpx
import json
import sys

sys.path.insert(0, '.')
from app.services.monday_service import get_monday_service
from app.services.analytics_service import AnalyticsService
from app.config import get_settings
from app.services.agent_service import GEMINI_TOOLS, SYSTEM_PROMPT

API_KEY = "AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg"
MODEL = "gemini-flash-latest"

async def test_turns():
    settings = get_settings()
    settings.USE_MOCK_MONDAY = False
    settings.MONDAY_API_KEY = API_KEY
    settings.DEALS_BOARD_ID = "5030219755"
    settings.WORK_ORDERS_BOARD_ID = "5030220085"
    
    svc = get_monday_service()
    analytics = AnalyticsService()
    deals_df, wo_df = await analytics._get_data(svc)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    contents = [
        {"role": "user", "parts": [{"text": "How is our pipeline looking this quarter?"}]}
    ]
    
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "tools": GEMINI_TOOLS
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        turns = 0
        while turns < 5:
            print(f"\n--- Turn {turns} ---")
            r = await client.post(url, json=payload, headers=headers)
            resp = r.json()
            
            candidates = resp.get("candidates", [])
            if not candidates:
                print("No candidates")
                break
                
            parts = candidates[0]["content"]["parts"]
            if "functionCall" in parts[0]:
                fc = parts[0]["functionCall"]
                tool_name = fc["name"]
                args = fc.get("args") or {}
                print(f"Model requested tool: {tool_name} with args: {args}")
                
                # Execute tool
                if tool_name == "get_pipeline_summary":
                    data = analytics.get_deal_summary(deals_df)
                elif tool_name == "get_sector_performance":
                    data = {
                        "deals_by_sector": analytics.get_sector_breakdown_deals(deals_df),
                        "wo_by_sector": analytics.get_sector_breakdown_wo(wo_df)
                    }
                else:
                    data = {"status": "mock data"}
                
                print("Data result:", list(data.keys())[:3] if isinstance(data, dict) else "list")
                
                payload["contents"].append({"role": "model", "parts": parts})
                payload["contents"].append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": tool_name, "response": {"output": data}}}]
                })
                turns += 1
            else:
                text = parts[0].get("text", "")
                print("Text Response received:")
                print(text)
                break

asyncio.run(test_turns())
