import asyncio
import httpx
import json
import sys

sys.path.insert(0, '.')
from app.services.monday_service import get_monday_service
from app.services.analytics_service import AnalyticsService
from app.config import get_settings

API_KEY = "AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg"
MODEL = "gemini-flash-latest"

GEMINI_TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "get_pipeline_summary",
                "description": "Get deals pipeline summary, optionally filtered by sector.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "sector": {
                            "type": "STRING",
                            "description": "Optional sector filter"
                        }
                    }
                }
            }
        ]
    }
]

async def test_live_agent():
    settings = get_settings()
    # Ensure live mode
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
        {"role": "user", "parts": [{"text": "How is our renewables pipeline looking?"}]}
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Turn 1
        r = await client.post(url, json={"contents": contents, "tools": GEMINI_TOOLS}, headers=headers)
        resp1 = r.json()
        print("LEG 1:")
        print(json.dumps(resp1, indent=2))
        
        parts = resp1['candidates'][0]['content']['parts']
        fc = parts[0]['functionCall']
        
        # Calculate real data
        sector = fc.get("args", {}).get("sector", "Renewables")
        data_result = analytics.query_pipeline_by_sector(deals_df, sector)
        print("\nReal Analytics Result for renewables:", data_result)
        
        # Turn 2
        contents.append({"role": "model", "parts": parts})
        contents.append({
            "role": "user",
            "parts": [{"functionResponse": {"name": fc["name"], "response": {"output": data_result}}}]
        })
        
        r2 = await client.post(url, json={"contents": contents, "tools": GEMINI_TOOLS}, headers=headers)
        resp2 = r2.json()
        print("\nLEG 2 RESPONSE:")
        print(json.dumps(resp2, indent=2))

asyncio.run(test_live_agent())
