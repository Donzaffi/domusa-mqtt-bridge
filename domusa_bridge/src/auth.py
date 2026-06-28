import aiohttp


class AuthManager:
    def __init__(self):
        self.base_url = "https://ic-api-app.azurewebsites.net"

    async def login(self):
        async with aiohttp.ClientSession() as session:
            payload = {
                "username": __import__("os").getenv("USERNAME"),
                "password": __import__("os").getenv("PASSWORD"),
                "langDevice": "es"
            }

            async with session.post(f"{self.base_url}/api/v1/auth/login", json=payload) as r:
                data = await r.json()
                return data["token"]
