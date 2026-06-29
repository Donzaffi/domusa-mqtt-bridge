import aiohttp

class DomusaAPI:
    def __init__(self, token):
        self.base = "https://ic-api-app.azurewebsites.net/api"
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

    async def get_caldera(self):
        url = f"{self.base}/v1/usuario/calderas/aliases"
        try:
            async with self.session.get(url) as r:
                if r.status != 200:
                    print(f"API Fehler: Status {r.status}")
                    return None
                data = await r.json()
                print(f"DEBUG: API Alias Antwort: {data}")
                
                if isinstance(data, dict) and data:
                    first_key = list(data.keys())[0]
                    # Versuche ID zu extrahieren
                    id_wert = data[first_key].get("idcaldera", first_key)
                    return {"id": id_wert}
                return None
        except Exception as e:
            print(f"Fehler in get_caldera: {e}")
            return None

    async def get_estado(self, cid):
        url = f"{self.base}/v2/calderas/{cid}/estado"
        async with self.session.get(url) as r:
            return await r.json()

    async def set_temp(self, cid, value, zone="cd"):
        url = f"{self.base}/v2/calderas/{cid}/setTempManual"
        async with self.session.post(url, json={
            "zona": zone,
            "newModo": {
                "modoSeleccion": "temp",
                "tempConsigna": float(value)
            }
        }) as r:
            return await r.json()
