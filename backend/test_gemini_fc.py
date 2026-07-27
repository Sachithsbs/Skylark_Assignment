import asyncio
import httpx
import json

API_KEY = "AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg"
MODEL = "gemini-flash-latest"  # or gemini-flash-latest

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
            }
        ]
    }
]

async def test_gemini():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "How is our renewables pipeline looking?"}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": "You are a helpful business intelligence assistant."}]
        },
        "tools": GEMINI_TOOLS
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, headers=headers)
        print("Status code:", r.status_code)
        resp_json = r.json()
        print("Response JSON:")
        print(json.dumps(resp_json, indent=2))
        
        # Check if functionCall is returned
        try:
            candidates = resp_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts and "functionCall" in parts[0]:
                    fc = parts[0]["functionCall"]
                    print("\n--- Detected Function Call ---")
                    print("Function Name:", fc.get("name"))
                    print("Args:", fc.get("args"))
        except Exception as e:
            print("Error parsing response:", e)

asyncio.run(test_gemini())
