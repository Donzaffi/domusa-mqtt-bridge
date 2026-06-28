# FILE: domusa_bridge/src/main.py

import asyncio

from config import Config
from auth import Auth
from api import DomusaAPI
from mqtt import MQTT
from discovery import Discovery
from climate import Climate
from router import Router


async def main():

    # 1. CONFIG
    cfg = Config()

    # 2. AUTH
    auth = Auth(cfg)
    token = await auth.get_valid_token()

    # 3. API
    api = DomusaAPI(token)
    device = await api.get_caldera()

    # 4. MQTT
    mqtt = MQTT()
    await mqtt.connect()

    # 5. DISCOVERY
    discovery = Discovery(mqtt, device)
    await discovery.publish()

    # 6. ROUTER (commands in background)
    router = Router(api, mqtt, device, cfg)
    asyncio.create_task(router.listen())

    # 7. CLIMATE HANDLER
    climate = Climate(api, mqtt, device, cfg)

    # 8. MAIN LOOP (polling)
    while True:
        state = await api.get_estado(device["id"])
        await climate.publish(state)
        await asyncio.sleep(cfg.poll_interval)


if __name__ == "__main__":
    asyncio.run(main())
