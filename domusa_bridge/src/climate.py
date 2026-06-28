class Climate:
    def __init__(self, api, mqtt, device, cfg):
        self.api = api
        self.mqtt = mqtt
        self.device = device

    async def publish(self, state):
        cid = self.device["id"]

        await self.mqtt.publish(
            f"domusa/{cid}/estado/tempActual",
            str(state.get("tempActual"))
        )

        await self.mqtt.publish(
            f"domusa/{cid}/estado/modo",
            str(state.get("modo"))
        )
