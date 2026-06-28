import asyncio
import json
import os
import aiohttp
from aiomqtt import Client

# Lade die Konfiguration aus den Home Assistant Optionen
with open("/data/options.json") as f:
    config = json.load(f)

USERNAME = config.get("username")
PASSWORD = config.get("password")
MQTT_HOST = "core-mosquitto" # Standard Host in HA Add-ons

class DomusaBridge:
    def __init__(self):
        self.session = None
        self.token = None

    async def login(self):
        url = "https://ic-api-app.azurewebsites.net/api/v1/auth/login" # Prüfe die URL deiner API!
        payload = {"username": USERNAME, "password": PASSWORD, "langDevice": "es"}
        async with self.session.post(url, json=payload) as resp:
            data = await resp.json()
            self.token = data.get("token")
            # Hier auch die Geräte-ID abrufen und speichern!

    async def run(self):
        async with aiohttp.ClientSession() as self.session:
            await self.login()
            async with Client(MQTT_HOST) as mqtt:
                while True:
                    # 1. API Daten abrufen
                    # 2. MQTT Discovery senden
                    # 3. Status veröffentlichen
                    await asyncio.sleep(60) # Interval

if __name__ == "__main__":
    bridge = DomusaBridge()
    asyncio.run(bridge.run())
