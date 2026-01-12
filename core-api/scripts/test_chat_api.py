import httpx
import asyncio

async def test_api():
    url = "http://localhost:8000/api/v1/chat/"
    
    # 1. Headers requiring X-API-KEY and Origin
    headers = {
        "X-API-KEY": "test-key-123",
        "Origin": "http://localhost:3000", # Must match allowed_domains
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Sending request to {url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json={"query": "test"})
            
            print(f"📥 Status Code: {response.status_code}")
            print(f"📄 Response: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Test Passed!")
            else:
                print(f"❌ Test Failed (Check Logic or Auth)")
                print(f"📄 Response Text: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            if 'response' in locals():
                 print(f"📄 Response Text: {response.text}") # type: ignore

if __name__ == "__main__":
    asyncio.run(test_api())
