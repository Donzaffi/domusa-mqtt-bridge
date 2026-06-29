import sys
import os
import json
import asyncio

# --- DEBUG: Import-Test ---
print("DEBUG 1: Skript gestartet")
try:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    from auth import Auth
    from api import DomusaAPI
    from mqtt import MQTT
    from discovery import Discovery
    from state import StateManager
    from router import Router
    from storage import Storage
    print("DEBUG 2: Alle Module erfolgreich geladen")
except Exception as e:
    print(f"DEBUG FEHLER: Modul-Import fehlgeschlagen: {e}")
    sys.exit(1)

async def poll_loop(api, state, device, cfg):
    print("DEBUG 5: Polling-Loop gestartet")
    while True:
        try:
            print("DEBUG 6: Rufe Daten ab...")
            
            estado = await api.get_estado(device["id"])
            print(f"DEBUG 7: /estado Antwort: {json.dumps(estado)}")
            
            config = await api.get_config(device["id"])
            print(f"DEBUG 8: /configuracion Antwort: {json.dumps(config)}")
            
            data_e = estado if estado is not None else {}
            data_c = config if config is not None else {}
            
            full_data = {**data_e, **data_c}
            
            if full_data:
                print(f"DEBUG 9: Daten gesendet: {len(full_data)} Keys")
                await state.publish(full_data)
            else:
                print("DEBUG 9: Warnung - API lieferte keine Daten.")
                
        except Exception as e:
            print(f"CRITICAL ERROR in poll_loop: {e}")
            
        await asyncio.sleep(cfg.get("poll_interval", 60))

async def main():
    print("DEBUG 3: Main-Funktion erreicht")
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"DEBUG FEHLER: Konfiguration konnte nicht geladen werden: {e}")
        return

    print("DEBUG 4: Initialisiere API...")
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
    asyncio.run(main())
