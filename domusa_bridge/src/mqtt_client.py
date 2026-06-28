from aiomqtt import Client


class MQTT:
    def __init__(self):
        self.client = Client("core-mosquitto")

    async def connect(self):
        await self.client.__aenter__()

    async def publish(self, topic, payload):
        await self.client.publish(topic, payload)
