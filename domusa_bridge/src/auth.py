import aiohttp


class Auth:
    BASE = "https://ic-api-app.azurewebsites.net"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def get_token(self):
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                f"{self.BASE}/v1/auth/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "langDevice": "es"
                }
            )

            data = await r.json()
            print("LOGIN RESPONSE:", data)

            return data["content"]["token"]
