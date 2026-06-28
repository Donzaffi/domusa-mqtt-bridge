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
        # Angepasst auf v1 und den Alias-Endpunkt
        r = await self.session.get(f"{self.base}/v1/usuario/calderas/aliases")
        data = await r.json()
        
        print(f"DEBUG: API Alias Antwort: {data}")
        
        # Logik für Struktur: {id: { idcaldera: "wert" }}
        try:
            # Wir nehmen den ersten Key im Dictionary (die Alias-ID)
            first_key = list(data.keys())[0]
            id_wert = data[first_key]["idcaldera"]
            return {"id": id_wert}
        except (IndexError, KeyError, Exception) as e:
            print(f"Fehler beim Extrahieren der idcaldera: {e}")
            return None

    async def get_estado(self, cid):
        # Falls dieser Endpunkt auch v1 benötigt, passe 'v2' hier ebenfalls an
        r = await self.session.get(f"{self.base}/v2/calderas/{cid}/estado")
        return await r.json()

    async def set_temp(self, cid, value, zone="cd"):
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
