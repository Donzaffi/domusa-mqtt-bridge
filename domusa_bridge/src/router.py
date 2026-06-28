import asyncio

class Router:
    def __init__(self, api, mqtt, device):
        self.api = api
        self.mqtt = mqtt
        self.device = device

    async def listen(self):
        cid = self.device["id"]
        topic_pattern = f"domusa/{cid}/set/#"

        # 1. Abonnement des Topics
        await self.mqtt.client.subscribe(topic_pattern)
        print(f"Router: Abonniert auf {topic_pattern}")

        # 2. Zugriff auf messages (OHNE Klammern, da es eine Property ist)
        async with self.mqtt.client.messages as messages:
            async for msg in messages:
                try:
                    # Topic prüfen, um sicherzugehen, dass wir die richtige Nachricht verarbeiten
                    topic_str = str(msg.topic)
                    key = topic_str.split("/")[-1]
                    value = msg.payload.decode()
                    
                    print(f"Router: Nachricht empfangen auf {topic_str}: {value}")

                    if key == "tempConsigna":
                        # Umwandlung und API-Aufruf
                        await self.api.set_temp(cid, float(value))
                        print(f"Router: Temperatur erfolgreich auf {value} gesetzt.")

                except Exception as e:
                    print(f"Router error beim Verarbeiten von {msg.topic}: {e}")
