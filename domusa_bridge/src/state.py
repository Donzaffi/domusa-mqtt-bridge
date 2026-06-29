import json

class StateManager:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish(self, data):
        # Hier wird das komplette JSON-Objekt aus der API 
        # auf das Status-Topic veröffentlicht.
        topic = f"domusa/{self.device['id']}/status"
        payload = json.dumps(data)
        
        await self.mqtt.client.publish(topic, payload, retain=True)
        print(f"State: Daten auf {topic} veröffentlicht.")
