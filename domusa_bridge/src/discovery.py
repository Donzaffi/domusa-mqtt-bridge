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
            "device": {
                "identifiers": [cid],
                "name": "Domusa Boiler"
            },
            "temperature_state_topic": f"domusa/{cid}/estado/tempActual",
            "temperature_command_topic": f"domusa/{cid}/set/tempConsigna"
        }

        # WICHTIG: Hier muss das await genau 8 Leerzeichen eingerückt sein, 
        # damit es zum Block der async-Funktion gehört!
        await self.mqtt.client.publish(
            f"homeassistant/climate/domusa_{cid}/config",
            json.dumps(payload),
            retain=True,
        )
