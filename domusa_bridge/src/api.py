import aiohttp
import asyncio

class DomusaAPI:
    def __init__(self, token):
        self.base = "https://ic-api-app.azurewebsites.net/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def _get(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url, timeout=10) as r:
                    if r.status == 200:
                        return await r.json()
                    return {}
            except Exception as e:
                print(f"API Error at {url}: {e}")
                return {}

    async def get_caldera(self):
        url = f"{self.base}/v1/usuario/calderas/aliases"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as r:
                if r.status != 200: return None
                data = await r.json()
                if isinstance(data, dict) and data:
                    first_key = list(data.keys())[0]
                    return {"id": data[first_key].get("idcaldera", first_key)}
        return None

    async def get_estado(self, cid):
        return await self._get(f"{self.base}/v2/calderas/{cid}/estado")

    async def get_config(self, cid):
        return await self._get(f"{self.base}/v2/calderas/{cid}/configuracion")
