import asyncio


class Router:
    def __init__(self, api, mqtt, device, cfg):
        self.api = api
        self.mqtt = mqtt
        self.device = device
        self.cfg = cfg

    async def listen(self):
        cid = self.device["id"]

        async with self.mqtt.client.filtered_messages(f"domusa/{cid}/set/#") as msgs:
            await self.mqtt.client.subscribe(f"domusa/{cid}/set/#")

            async for msg in msgs:
                key = msg.topic.value.split("/")[-1]
                value = msg.payload.decode()

                if key == "tempConsigna":
                    await self.api.set_temp(cid, float(value), self.cfg.zone)
