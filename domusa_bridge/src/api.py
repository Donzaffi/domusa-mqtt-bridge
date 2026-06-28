import aiohttp


class DomusaAPI:
    def __init__(self, token):
        self.base = "https://ic-api-app.azurewebsites.net"
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {token}"}
        )

    async def get_caldera(self):
        r = await self.session.get(f"{self.base}/v2/calderas")
        return (await r.json())[0]

    async def get_estado(self, cid):
        r = await self.session.get(f"{self.base}/v2/calderas/{cid}/estado")
        return await r.json()

    async def set_temp(self, cid, value, zone):
        return await self.session.put(
            f"{self.base}/v2/calderas/{cid}/setTempManual",
            json={
                "zona": zone,
                "newModo": {
                    "modoSeleccion": "temp",
                    "tempConsigna": value
                }
            }
        )
