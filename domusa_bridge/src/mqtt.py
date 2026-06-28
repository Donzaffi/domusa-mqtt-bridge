class MQTT:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = Client(
            hostname="core-mosquitto",
            keepalive=60
        )
        await self.client.__aenter__()

    async def publish(self, topic, payload):
        await self.client.publish(topic, payload)
