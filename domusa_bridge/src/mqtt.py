import aiomqtt

class MQTT:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.client = None

    async def connect(self):
        print(f"DEBUG: Verbinde mit MQTT {self.host} als User {self.user}...")
        # Hier müssen user und password zwingend übergeben werden
        self.client = aiomqtt.Client(
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password
        )
        await self.client.__aenter__()
