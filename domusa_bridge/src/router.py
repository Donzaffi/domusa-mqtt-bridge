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

        async for msg in self.mqtt.client.messages:
            try:
                topic_str = str(msg.topic)
                key = topic_str.split("/")[-1]
                value = msg.payload.decode()
                
                print(f"Router: Nachricht empfangen auf {topic_str}: {value}")

                if key == "tempConsigna":
                    await self.api.set_temp(cid, float(value))
                    print(f"Router: Temperatur erfolgreich auf {value} gesetzt.")
                
                elif key == "setACS":
                    # Nutzung des korrekten Endpunkts /estado und Keys st_acs_p04
                    url = f"{self.api.base}/v2/calderas/{cid}/estado"
                    payload = {"st_acs_p04": int(value)}
                    
                    async with self.api.session.put(url, json=payload) as response:
                        if response.status == 200:
                            print(f"Router: Warmwasser-Soll erfolgreich auf {value} gesetzt.")
                        else:
                            print(f"Router: Fehler bei ACS-Änderung: {response.status}")

            except Exception as e:
                print(f"Router error beim Verarbeiten von {msg.topic}: {e}")
