import json


class Discovery:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish_all(self):
        device_id = self.device["id"]

        sensors = [
            {
                "name": "Temperature",
                "key": "temperature",
                "unit": "°C"
            },
            {
                "name": "Power",
                "key": "power"
            }
        ]

        for s in sensors:
            topic = f"homeassistant/sensor/{device_id}_{s['key']}/config"

            payload = {
                "name": f"Domusa {s['name']}",
                "state_topic": f"domusa/{device_id}/{s['key']}",
                "unique_id": f"domusa_{device_id}_{s['key']}",
                "device": {
                    "identifiers": [device_id],
                    "name": "Domusa Boiler"
                }
            }

            if "unit" in s:
                payload["unit_of_measurement"] = s["unit"]

            await self.mqtt.publish(topic, json.dumps(payload))
