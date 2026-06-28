import json
from mapper import map_state


class StateManager:
    def __init__(self, api, mqtt, device):
        self.api = api
        self.mqtt = mqtt
        self.device = device

    async def publish(self, data):
        mapped = map_state(data)
        device_id = self.device["id"]

        for k, v in mapped.items():
            topic = f"domusa/{device_id}/{k}"
            await self.mqtt.publish(topic, str(v))
