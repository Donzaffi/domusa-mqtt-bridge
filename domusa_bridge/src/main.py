import asyncio
import json
import sys
import os

# Pfad zum src-Verzeichnis hinzufügen, damit die Module gefunden werden
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from auth import Auth
from api import DomusaAPI
from mqtt import MQTT
from discovery import Discovery
from state import StateManager
from router import Router
from storage import Storage
from i18n import I18n

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
    
    # Konfiguration laden
    with open("/data/options.json", "r") as f:
        config = json.load(f)
    
    # Sprachwahl aus Config laden (Standard: 'de')
    lang = config.get("language", "de")
    
    # Authentifizierung und API
    auth = Auth(config["username"], config["password"])
    token = await auth.get_token()
    api = DomusaAPI(token)
    
    # Storage und Device
    storage = Storage()
    device = await storage.get_device()
    if not device:
        device = await api.get_caldera()
        await storage.save_device(device)

    # MQTT Verbindung
    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"), 
        port=1883, 
        user=config.get("mqtt_user"), 
        password=config.get("mqtt_password")
    )
    await mqtt.connect()

    # Discovery mit Sprach-Support initialisieren
    discovery = Discovery(mqtt, device, lang=lang)
    await discovery.publish()

    # State und Router starten
    state = StateManager(mqtt, device)
    router = Router(api, mqtt, device)
    
    # Poll-Loop und Router gleichzeitig laufen lassen
    await asyncio.gather(
        poll_loop(api, state, device, config),
        router.listen()
    )

if __name__ == "__main__":
    asyncio.run(main())
