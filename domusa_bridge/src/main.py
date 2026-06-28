import asyncio

from auth import Auth
from api import DomusaAPI
from mqtt import MQTT
from discovery import Discovery
from state import StateManager
from router import Router
from storage import Storage
import json
import sys
import os


async def poll_loop(api, state, device, cfg):
    while True:
        try:
            data = await api.get_estado(device["id"])
            await state.publish(data)
        except Exception as e:
            print("Polling error:", e)

        await asyncio.sleep(cfg["poll_interval"])


async def main():

    # 1. STORAGE (device persistent)
    storage = Storage()

    # 2. AUTH
    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()

    # 3. API
    api = DomusaAPI(token)

    # 4. DEVICE (ONLY ONCE)
    device = await storage.get_device()
    if not device:
        device = await api.get_caldera()
        await storage.save_device(device)

    # 5. MQTT
    mqtt = MQTT()
    await mqtt.connect()

    # 6. DISCOVERY (idempotent)
    discovery = Discovery(mqtt, device)
    await discovery.publish()

    # 7. STATE HANDLER
    state = StateManager(mqtt, device)

    # 8. ROUTER (commands)
    router = Router(api, mqtt, device)
    asyncio.create_task(router.listen())

    # 9. POLLING LOOP
    await poll_loop(api, state, device, {"poll_interval": 60})


if __name__ == "__main__":
    asyncio.run(main())
