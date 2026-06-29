import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from auth import Auth
from api import DomusaAPI
from mqtt import MQTT
from discovery import Discovery
from state import StateManager
from router import Router
from storage import Storage

async def poll_loop(api, state, device, cfg):
    while True:
        try:
            # Nur noch /estado, wie es vorher stabil lief
            data = await api.get_estado(device["id"])
            await state.publish(data)
        except Exception as e:
            print("Polling error:", e)
        await asyncio.sleep(cfg.get("poll_interval", 60))

async def main():
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Fehler: /data/options.json nicht gefunden!")
        return

    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()
    api = DomusaAPI(token)
    storage = Storage()
    device = await storage.get_device()
    
    if not device:
        device = await api.get_caldera()
        if device:
            await storage.save_device(device)

    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"),
        port=config.get("mqtt_port", 1883),
        user=config.get("mqtt_user"),
        password=config.get("mqtt_password")
    )
    await mqtt.connect()

    discovery = Discovery(mqtt, device)
    await discovery.publish()

    state = StateManager(mqtt, device)
    router = Router(api, mqtt, device)
    asyncio.create_task(router.listen())

    await poll_loop(api, state, device, config)

if __name__ == "__main__":
    asyncio.run(main())
