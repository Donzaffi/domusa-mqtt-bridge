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


def log(msg):
    print(f"DEBUG: {msg}")
    sys.stdout.flush()


async def poll_loop(api, state, device, cfg):
    cid = device["id"]
    name = device.get("name") or cid
    while True:
        log(f"Polling {name} ({cid})...")
        estado = await api.get_estado(cid)
        config = await api.get_config(cid)
        full_data = {**(estado or {}), **(config or {})}

        if full_data:
            log(f"{name}: publishing {len(full_data)} values")
            await state.publish(full_data)
        else:
            log(f"Warning: no data received for {name} ({cid})")

        await asyncio.sleep(cfg.get("poll_interval", 60))


async def main():
    log("Initializing Domusa MQTT Bridge...")

    with open("/data/options.json", "r") as f:
        config = json.load(f)

    auth = Auth(config["username"], config["password"])
    api = DomusaAPI(auth)

    # Always query the cloud so newly added installations are picked up.
    cloud_devices = await api.get_calderas()
    if not cloud_devices:
        raise RuntimeError("No Domusa installations found in this account")

    storage = Storage()
    await storage.save_devices(cloud_devices)
    devices = cloud_devices

    log(f"Found {len(devices)} Domusa installation(s): " + ", ".join(
        f"{d.get('name', d['id'])} [{d['id']}]" for d in devices
    ))

    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"),
        port=config.get("mqtt_port", 1883),
        user=config.get("mqtt_user"),
        password=config.get("mqtt_password"),
    )
    await mqtt.connect()

    # Create one state publisher and one polling task per installation.
    tasks = []
    for device in devices:
        state = StateManager(mqtt, device)
        discovery = Discovery(mqtt, device, config.get("language", "de"))
        await discovery.publish()
        tasks.append(poll_loop(api, state, device, config))

    # One router handles commands for all device IDs.
    router = Router(api, mqtt, devices)
    tasks.append(router.listen())

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
