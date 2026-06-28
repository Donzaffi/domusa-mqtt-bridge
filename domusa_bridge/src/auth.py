import aiohttp
import time
import json
import os


class Auth:
    def __init__(self, cfg):
        self.cfg = cfg
        self.base_url = "https://ic-api-app.azurewebsites.net"
        self.token_file = "/data/token.json"

    async def login(self):
        async with aiohttp.ClientSession() as s:
            r = await s.post(
                f"{self.base_url}/v1/auth/login",
                json={
                    "username": self.cfg.username,
                    "password": self.cfg.password,
                    "langDevice": "es"
                }
            )
            return await r.json()

    async def get_valid_token(self):
        data = await self.login()

        token = {
            "access": data["token"],
            "expires": time.time() + 3600
        }

        with open(self.token_file, "w") as f:
            json.dump(token, f)

        return token["access"]
