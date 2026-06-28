class StateManager:
    def __init__(self, mqtt, device):
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
