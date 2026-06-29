import asyncio
import json
import sys
import os

# Pfad hinzufügen, damit die Module im gleichen Ordner gefunden werden
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from auth import Auth
from api import DomusaAPI
from mqtt import MQTT
from discovery import Discovery
from state import StateManager
from router import Router
from storage import Storage

async def poll_loop(api, state, device, cfg):
    """Hauptschleife zum Abrufen der Daten von /estado und /configuracion."""
    while True:
        try:
            print("Polling: Rufe Daten ab...")
            # Daten von beiden Endpunkten abrufen
            estado = await api.get_estado(device["id"])
            config = await api.get_config(device["id"])
            
            # Fehlerbehandlung: Leere Antworten in leere Dicts umwandeln
            data_e = estado if estado is not None else {}
            data_c = config if config is not None else {}
            
            # Zusammenführen der Daten
            full_data = {**data_e, **data_c}
            
            if full_data:
                print(f"Polling: Sende Daten für {len(full_data)} Sensoren.")
                await state.publish(full_data)
            else:
                print("Polling: Warnung - API lieferte keine Daten.")
                
        except Exception as e:
            print(f"CRITICAL POLLING ERROR: {e}")
            
        # Wartezeit aus der Konfiguration oder Standard 60 Sekunden
        await asyncio.sleep(cfg.get("poll_interval", 60))

async def main():
    # Konfiguration laden
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Fehler: /data/options.json nicht gefunden!")
        return

    # Authentifizierung und API-Setup
    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()
    api = DomusaAPI(token)
    
    storage = Storage()
    device = await storage.get_device()
    if not device:
        device = await api.get_caldera()
        if device:
            await storage.save_device(device)
        else:
            print("Fehler: Gerät konnte nicht gefunden werden.")
            return

    # MQTT-Verbindung herstellen
    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"), 
        port=config.get("mqtt_port", 1883), 
        user=config.get("mqtt_user"), 
        password=config.get("mqtt_password")
    )
    await mqtt.connect()

    # Discovery ausführen
    discovery = Discovery(mqtt, device)
    await discovery.publish()

    # State-Management und Router starten
    state = StateManager(mqtt, device)
    router = Router(api, mqtt, device)
    asyncio.create_task(router.listen())

    # Polling-Loop starten
    await poll_loop(api, state, device, config)

if __name__ == "__main__":
    asyncio.run(main())
