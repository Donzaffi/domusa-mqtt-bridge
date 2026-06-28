import asyncio
import os

from auth import AuthManager
from api import DomusaAPI
from mqtt_client import MQTTClient
from discovery import Discovery
from state import StateManager
from commands import CommandListener


POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))


async def main():
    auth = AuthManager()
    token = await auth.login()

    api = DomusaAPI(token)
    device = await api.get_device()

    mqtt = MQTTClient()
    await mqtt.connect()

    discovery = Discovery(mqtt, device)
    await discovery.publish_all()

    state = StateManager(api, mqtt, device)

    commands = CommandListener(api, mqtt, device)
    await commands.start()

    while True:
        data = await api.get_state(device["id"])
        await state.publish(data)
        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
