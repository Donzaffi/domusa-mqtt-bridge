import asyncio

class Router:
    def __init__(self, api, mqtt, device):
        self.api = api
        self.mqtt = mqtt
        self.device = device

    async def listen(self):
        cid = self.device["id"]
        topic_pattern = f"domusa/{cid}/set/#"

        await self.mqtt.client.subscribe(topic_pattern)
        print(f"Router: Abonniert auf {topic_pattern}")

        # Direktes Iterieren über das messages-Objekt ohne 'async with'
        async for msg in self.mqtt.client.messages:
            try:
            topic_str = str(msg.topic)
            key = topic_str.split("/")[-1]
            value = msg.payload.decode()
        
                # Heizung (bestehend)
                if key == "tempConsigna":
                    await self.api.set_temp(cid, float(value))
            
                # NEU: Warmwasser (ACS)
                elif key == "setACS":
                    # Endpunkt PUT /v2/calderas/{id}/perfiles
                    url = f"{self.api.base}/v2/calderas/{cid}/perfiles"
                    await self.api.session.put(url, json={"acs": int(value)})
                    print(f"Router: Warmwasser auf {value} gesetzt.")

            except Exception as e:
                print(f"Router error: {e}")
