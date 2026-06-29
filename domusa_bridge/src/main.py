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

async def run_addon():
    print("DEBUG: Lade Konfiguration...")
    with open("/data/options.json", "r") as f:
        config = json.load(f)

    print("DEBUG: Initialisiere API...")
    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()
    api = DomusaAPI(token)
    
    storage = Storage()
    device = await storage.get_device()
    if not device:
        device = await api.get_caldera()
        await storage.save_device(device)

    print("DEBUG: Verbinde MQTT...")
    mqtt = MQTT(host=config.get("mqtt_host", "core-mosquitto"), port=1883, user=config.get("mqtt_user"), password=config.get("mqtt_password"))
    await mqtt.connect()

    print("DEBUG: Sende Discovery...")
    discovery = Discovery(mqtt, device)
    await discovery.publish()

    print("DEBUG: Starte Router und State-Manager...")
    state = StateManager(mqtt, device)
    router = Router(api, mqtt, device)
    
    # Aufgaben in den Hintergrund schieben
    asyncio.create_task(router.listen())
    
    print("DEBUG: Start der Haupt-Polling-Schleife...")
    # Polling direkt hier ausführen
    while True:
        try:
            # Deine API-Aufrufe hier
            estado = await api.get_estado(device["id"])
            config = await api.get_config(device["id"])
            full_data = {**(estado or {}), **(config or {})}
            if full_data:
                await state.publish(full_data)
        except Exception as e:
            print(f"DEBUG: Fehler im Loop: {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(run_addon())
    except Exception as e:
        print(f"FATALER FEHLER: {e}")
        # Wir beenden nicht, wir warten, damit das Add-on nicht neu startet
        asyncio.run(asyncio.sleep(3600))
