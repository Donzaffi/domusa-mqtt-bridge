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

        try:
            return data["content"]["token"]
        except KeyError:
            raise Exception(f"Unexpected login response: {data}")
