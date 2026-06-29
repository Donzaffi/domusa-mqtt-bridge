import json

class Discovery:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish(self):
        cid = self.device["id"]
        device_info = {
            "identifiers": [cid],
            "name": "Domusa HTEC Pro 12",
            "manufacturer": "Domusa Teknik",
            "model": "HTEC Pro 12"
        }

        # Zusammenfassung aller Sensoren (Status + Konfiguration)
        sensors = [
            # Status-Sensoren
            {"name": "System Status", "uid": "status", "key": "alarma", "unit": None, "class": None, "icon": "mdi:heat-pump"},
            {"name": "Warmwassertemperatur Soll", "uid": "st_acs_soll", "key": "st_acs_p04", "unit": "°C", "class": "temperature", "icon": "mdi:water-heater-marker"},
            
            # Konfigurations-Sensoren (Sicherheit & Grenzwerte)
            {"name": "Max Hochdruck", "uid": "max_pralta", "key": "max_pralta_p53", "unit": "bar", "class": "pressure", "icon": "mdi:gauge"},
            {"name": "Min Niederdruck", "uid": "min_prbaja", "key": "min_prbaja_p54", "unit": "bar", "class": "pressure", "icon": "mdi:gauge"},
            {"name": "Legionellen Temp", "uid": "st_legionela", "key": "st_legionela_p13", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer-alert"},
            
            # Konfigurations-Sensoren (Modi & Status)
            {"name": "Warmwasser Modus", "uid": "m_acs", "key": "m_acs_p63", "unit": None, "class": "running", "icon": "mdi:water-boiler"},
            {"name": "Nachtmodus", "uid": "m_noche", "key": "m_noche_p17", "unit": None, "class": "running", "icon": "mdi:weather-night"},
            {"name": "OTC Regelung", "uid": "m_otc", "key": "m_otc_p19", "unit": None, "class": "running", "icon": "mdi:weather-partly-cloudy"}
        ]

        for s in sensors:
            payload = {
                "name": f"Domusa {s['name']}",
                "unique_id": f"domusa_{cid}_{s['uid']}",
                "device": device_info,
                "state_topic": f"domusa/{cid}/status",
                "value_template": f"{{{{ value_json.{s['key']} }}}}",
                "unit_of_measurement": s['unit'],
                "device_class": s['class'],
                "icon": s['icon']
            }
            await self.mqtt.client.publish(
                f"homeassistant/sensor/domusa_{cid}_{s['uid']}/config", 
                json.dumps(payload), 
                retain=True
            )

        # Der Slider (bleibt wie gehabt)
        acs_number_payload = {
            "name": "Domusa Warmwasser Soll",
            "unique_id": f"domusa_{cid}_acs_regler",
            "device": device_info,
            "state_topic": f"domusa/{cid}/status",
            "value_template": "{{ value_json.st_acs_p04 }}",
            "command_topic": f"domusa/{cid}/set/setACS",
            "optimistic": False,
            "min": 30,
            "max": 70,
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "icon": "mdi:water-heater-marker"
        }
        await self.mqtt.client.publish(
            f"homeassistant/number/domusa_{cid}_acs_regler/config", 
            json.dumps(acs_number_payload), 
            retain=True
        )
