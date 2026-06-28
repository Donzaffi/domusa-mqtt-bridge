import aiohttp


class DomusaAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://ic-api-app.azurewebsites.net"
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {token}"}
        )

    async def get_device(self):
        async with self.session.get(f"{self.base_url}/api/v1/devices") as r:
            data = await r.json()
            return data[0]

    async def get_state(self, device_id):
        async with self.session.get(f"{self.base_url}/api/v1/device/{device_id}/state") as r:
            return await r.json()

    async def set_value(self, device_id, key, value):
        payload = {key: value}
        async with self.session.post(
            f"{self.base_url}/api/v1/device/{device_id}/set",
            json=payload
        ) as r:
            return await r.json()
