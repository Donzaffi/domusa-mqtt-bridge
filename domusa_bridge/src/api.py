import aiohttp
import asyncio

class DomusaAPI:
    def __init__(self, auth):
        self.base = "https://ic-api-app.azurewebsites.net/api"
        self.auth = auth
        self.token = None

    async def _get_headers(self):
        if not self.token:
            self.token = await self.auth.get_token()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def _get(self, url):
        headers = await self._get_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(url, timeout=10) as r:
                    # Token-Refresh Logik bei 401
                    if r.status == 401:
                        self.token = await self.auth.get_token()
                        headers["Authorization"] = f"Bearer {self.token}"
                        async with session.get(url, headers=headers, timeout=10) as r2:
                            return await r2.json() if r2.status == 200 else {}
                    
                    return await r.json() if r.status == 200 else {}
            except Exception as e:
                print(f"API Error at {url}: {e}")
                return {}

    async def get_caldera(self):
        url = f"{self.base}/v1/usuario/calderas/aliases"
        headers = await self._get_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as r:
                # Auch hier 401 prüfen, falls das Token abgelaufen ist
                if r.status == 401:
                    self.token = await self.auth.get_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    async with session.get(url, headers=headers) as r2:
                        r = r2
                
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
