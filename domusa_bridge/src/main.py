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
    """
    Pollt Daten von /estado und /configuracion, mergt sie zu einem 
    einzigen Payload und veröffentlicht sie über MQTT.
    """
    while True:
        try:
            # 1. Daten von beiden Endpunkten abrufen
            estado = await api.get_estado(device["id"])
            config = await api.get_config(device["id"])
            
            # 2. Sicherheit: Falls API Fehler (None) zurückgibt, leeres Dict verwenden
            estado_data = estado if estado is not None else {}
            config_data = config if config is not None else {}
            
            # 3. Daten zu einem einzigen JSON-Objekt zusammenführen
            # 'config_data' überschreibt ggf. Werte in 'estado_data' bei identischen Keys
            full_data = {**estado_data, **config_data}
            
            # 4. Nur publishen, wenn wir Daten erhalten haben
            if full_data:
                await state.publish(full_data)
            else:
                print("Polling-Warnung: Keine Daten von der API erhalten.")
            
        except Exception as e:
            print(f"Polling error: {e}")
            
        # Intervall aus Konfiguration oder Default 60s
        await asyncio.sleep(cfg.get("poll_interval", 60))

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

    # 3. API INITIALISIEREN
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
            return

    # 5. MQTT
    mqtt = MQTT(
        host=config.get("mqtt_host", "core-mosquitto"),
        port=config.get("mqtt_port", 1883),
        user=config.get("mqtt_user"),
        password=config.get("mqtt_password")
    )
    await mqtt.connect()

    # 6. DISCOVERY (Einmalig beim Start senden)
    discovery = Discovery(mqtt, device)
    await discovery.publish()

    # 7. STATE HANDLER
    state = StateManager(mqtt, device)

    # 8. ROUTER (Commands wie setACS/setTemp)
    router = Router(api, mqtt, device)
    asyncio.create_task(router.listen())

    # 9. POLLING LOOP
    # Wir übergeben das gesamte config-Objekt für den Zugriff auf poll_interval
    await poll_loop(api, state, device, config)

if __name__ == "__main__":
    asyncio.run(main())
