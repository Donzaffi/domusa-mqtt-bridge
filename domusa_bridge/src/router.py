class Router:
    def __init__(self, api, mqtt, devices):
        self.api = api
        self.mqtt = mqtt
        self.devices = {str(device["id"]): device for device in devices}

    async def listen(self):
        for cid in self.devices:
            topic_pattern = f"domusa/{cid}/set/#"
            await self.mqtt.client.subscribe(topic_pattern)
            print(f"Router: Subscribed to {topic_pattern}")

        async for msg in self.mqtt.client.messages:
            try:
                topic_str = str(msg.topic)
                parts = topic_str.split("/")
                # Expected: domusa/<device_id>/set/<command>
                if len(parts) < 4 or parts[0] != "domusa" or parts[2] != "set":
                    continue

                cid = parts[1]
                key = parts[-1]
                if cid not in self.devices:
                    continue

                value = msg.payload.decode()
                print(f"Router: {cid} received {key}={value}")

                if key == "setACS":
                    await self.api.set_acs(cid, int(float(value)))
                    print(f"Router: DHW setpoint for {cid} changed to {value}")
                elif key == "setOTCCurve":
                    curve_text = value.strip().replace("K=", "")
                    curve = float(curve_text)
                    result = await self.api.set_otc_curve(cid, curve)
                    if result is None:
                        print(f"Router: ERROR - OTC curve write failed for {cid}")
                    elif curve == 0:
                        print(f"Router: OTC curve for {cid} set to OFF")
                    else:
                        print(f"Router: OTC curve for {cid} changed to K={curve}")
                else:
                    print(f"Router: Unsupported command '{key}' for {cid}")

            except Exception as e:
                print(f"Router error processing {msg.topic}: {e}")
