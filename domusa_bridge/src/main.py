import asyncio
import json
import sys
import os

# Pfad-Fix für Importe
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
            data = await api.get_estado(device["id"])
            await state.publish(data)
        except Exception as e:
            print("Polling error:", e)
        await asyncio.sleep(cfg["poll_interval"])

async def main():
    # 1. KONFIGURATION LADEN
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Fehler: /data/options.json nicht gefunden!")
        return

    # 2. AUTH
    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()

    # 3. API INITIALISIEREN (Hier wird 'api' definiert!)
    api = DomusaAPI(token)

    # 4. STORAGE & DEVICE
storage = Storage()
    device = await storage.get_device()
    
    if not device:
        print("Kein Gerät im Storage gefunden, frage API ab...")
        device = await api.get_caldera()
        if device:
            await storage.save_device(device)
        else:
            print("KRITISCHER FEHLER: API konnte keine Caldera finden.")
            return # Programm beenden, nicht weiterlaufen!

    # 5. MQTT
    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"),
        port=config.get("mqtt_port", 1883),
        user=config.get("mqtt_user"),
        password=config.get("mqtt_password")
    )
    await mqtt.connect()

    # 6. DISCOVERY
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
