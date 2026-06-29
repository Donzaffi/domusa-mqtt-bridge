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
    while True:
        log("Starte Datenabfrage...")
        estado = await api.get_estado(device["id"])
        config = await api.get_config(device["id"])
        
        full_data = {**(estado or {}), **(config or {})}
        
        if full_data:
            log(f"Sende {len(full_data)} Sensoren an MQTT")
            await state.publish(full_data)
        else:
            log("Warnung: Keine Daten von der API erhalten!")
            
        await asyncio.sleep(cfg.get("poll_interval", 60))

async def main():
    log("Initialisiere...")
    with open("/data/options.json", "r") as f:
        config = json.load(f)

    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()
    api = DomusaAPI(token)
    
    storage = Storage()
    device = await storage.get_device()
    if not device:
        device = await api.get_caldera()
        await storage.save_device(device)

    mqtt = MQTT(host=config.get("mqtt_host", "core-mosquitto"), port=1883, user=config.get("mqtt_user"), password=config.get("mqtt_password"))
    await mqtt.connect()

    discovery = Discovery(mqtt, device)
    await discovery.publish()

    state = StateManager(mqtt, device)
    router = Router(api, mqtt, device)
    asyncio.create_task(router.listen())

    await poll_loop(api, state, device, config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"FATALER FEHLER: {e}")
