import asyncio
from httpx import AsyncClient

async def run():
    async with AsyncClient(timeout=120.0) as client:
        r = await client.post("http://localhost:8001/auth/login", json={"email": "demo-boyahane@usedima.com", "password": "dima-demo-1234"})
        token = r.json().get("access_token")
        
        r2 = await client.post(
            "http://localhost:8001/ask",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "toplam satışlar aylık olarak nedir?"}
        )
        print(r2.status_code)
        print(r2.text)

asyncio.run(run())
