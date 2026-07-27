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

async def test_gemini_second_step():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Mock data result from analytics service
    mock_data_result = {
        "total_deals": 111,
        "won": 45,
        "dead": 30,
        "open": 36,
        "on_hold": 0,
        "win_rate": 0.6,
        "total_pipeline_value": 45000000.0,
        "avg_deal_value": 1500000.0
    }
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "How is our renewables pipeline looking?"}]
            },
            {
                "role": "model",
                "parts": [
                    {
                        "functionCall": {
                            "name": "get_pipeline_summary",
                            "args": {"sector": "Renewables"},
                            "id": "nWIxEk0O"
                        },
                        "thoughtSignature": "EuMCCuACARFNMg82I0PslDV65TVpsQlwWwGJ2wSUilN3iXDwu7oPGQjcN3yQE9vV+cE5Jk86Vkjl8feq1np4iWla7xKYn3Yc8Z0ZF20cRvrtaqmq4+x53jGZEBrVUbatQxsOpxk7ZarL/cFqMFWVoMrhXgxkxbiEfIOC3aBPL8oDWl2BAeo48/BL+d6NIsCx+MyPnLSGpSX1otxdAt+OEJO7xK9SVZuBDlPSeik7kEOoFhE79mAXwoDzqcN3/t5rWqSIveDNSFlYkcIDcG6k8QebZXscdDIAt3ygpvXslnsa7zeq7GxxBExg1m/mB8SENhId4yheiyuvhL7Z01dOon22FhrfZAOw2Vrh+ytn/bzWSMoA8xWHDR1c5PRUTKzqnm3s2FP0puUN0UAWjtBC7u2n1Xzs7k2SkoBL7RlLIBd0lNZ1D+7+cINK5/QHCI9uz7qe0e2Yiy4Qai4fHq/M+ykgCCp/3g=="
                    }
                ]
            },
            {
                "role": "user",
                "parts": [
                    {
                        "functionResponse": {
                            "name": "get_pipeline_summary",
                            "response": {
                                "output": mock_data_result
                            }
                        }
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": "You are a helpful business intelligence assistant. Format numbers as ₹X Cr/L."}]
        },
        "tools": GEMINI_TOOLS
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, headers=headers)
        print("Status code:", r.status_code)
        resp_json = r.json()
        print("Response JSON:")
        print(json.dumps(resp_json, indent=2))
        
        try:
            text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
            print("\n--- Final Text Response ---")
            print(text)
        except Exception as e:
            print("Error parsing text:", e)

asyncio.run(test_gemini_second_step())
