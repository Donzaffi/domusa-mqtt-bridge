import asyncio


class Router:
    def __init__(self, api, mqtt, device):
        self.api = api
        self.mqtt = mqtt
        self.device = device

    async def listen(self):
        cid = self.device["id"]

        await self.mqtt.client.subscribe(f"domusa/{cid}/set/#")

        async with self.mqtt.client.messages() as messages:
            async for msg in messages:
                try:
                    key = msg.topic.value.split("/")[-1]
                    value = msg.payload.decode()

                    if key == "tempConsigna":
                        await self.api.set_temp(cid, float(value))

                except Exception as e:
                    print("Router error:", e)
