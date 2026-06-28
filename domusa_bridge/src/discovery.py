import json


class Discovery:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish(self):
        cid = self.device["id"]

        payload = {
            "name": "Domusa Heating",
            "unique_id": f"domusa_{cid}",

            "temperature_state_topic": f"domusa/{cid}/estado/tempActual",
            "temperature_command_topic": f"domusa/{cid}/set/tempConsigna",

            "mode_state_topic": f"domusa/{cid}/estado/modo",
            "mode_command_topic": f"domusa/{cid}/set/mode",

            "device": {
                "identifiers": [cid],
                "name": "Domusa Boiler"
            }
        }

        await self.mqtt.publish(
            f"homeassistant/climate/domusa_{cid}/config",
            json.dumps(payload)
        )
