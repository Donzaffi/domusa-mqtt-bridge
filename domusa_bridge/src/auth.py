import aiohttp


class Auth:
    BASE = "https://ic-api-app.azurewebsites.net"

    async def get_token(self):
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                f"{self.BASE}/v1/auth/login",
                json={
                    "username": "",
                    "password": "",
                    "langDevice": "es"
                }
            )
            data = await r.json()
            return data["token"]
