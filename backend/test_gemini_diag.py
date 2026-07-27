import asyncio
import httpx
import json

API_KEY = "AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg"
MODEL = "gemini-flash-latest"

GEMINI_TOOLS = [
    {
        "functionDeclarations": [
            {
                "name": "get_pipeline_summary",
                "description": "Get deals pipeline summary",
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

async def test():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "How is our renewables pipeline looking?"}]}],
        "tools": GEMINI_TOOLS
    }
    
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        resp_json = r.json()
        print("LEG 1 RESPONSE:")
        print(json.dumps(resp_json, indent=2))
        
        parts = resp_json['candidates'][0]['content']['parts']
        fc = parts[0]['functionCall']
        
        # mock data
        mock_data = {'output': {'total_deals': 111}}
        
        payload2 = {
            "contents": [
                {"role": "user", "parts": [{"text": "How is our renewables pipeline looking?"}]},
                {"role": "model", "parts": parts},
                {"role": "user", "parts": [{"functionResponse": {"name": fc['name'], "response": mock_data}}]}
            ],
            "tools": GEMINI_TOOLS
        }
        
        r2 = await client.post(url, json=payload2, headers=headers)
        print("\nLEG 2 RESPONSE:")
        print(json.dumps(r2.json(), indent=2))

asyncio.run(test())
