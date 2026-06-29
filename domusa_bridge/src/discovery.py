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

        # 1. ZUERST: Die alte 'number' Entität (Slider) explizit im MQTT-Broker löschen
        # Dies ist notwendig, damit Home Assistant sie aus der Liste entfernt
        await self.mqtt.client.publish(f"homeassistant/number/domusa_{cid}_acs_regler/config", None, retain=True)

        # 2. Alle Sensoren definieren
        sensors = [
            {"name": "System Status", "uid": "status", "key": "alarma", "unit": None, "class": None, "icon": "mdi:heat-pump"},
            {"name": "Sub-Alarm", "uid": "sub_alarma", "key": "sub_alarma", "unit": None, "class": None, "icon": "mdi:alert-circle-outline"},
            {"name": "Außentemperatur", "uid": "s_ext", "key": "s_ext_c02", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer"},
            {"name": "Vorlauftemperatur", "uid": "s_ida", "key": "s_ida_hp_c08", "unit": "°C", "class": "temperature", "icon": "mdi:water-boiler"},
            {"name": "Rücklauftemperatur", "uid": "s_ret", "key": "s_ret_hp_c07", "unit": "°C", "class": "temperature", "icon": "mdi:water-boiler-alert"},
            {"name": "Warmwassertemperatur Ist", "uid": "s_acs", "key": "s_acs_c09", "unit": "°C", "class": "temperature", "icon": "mdi:water-thermometer"},
            {"name": "Warmwassertemperatur Soll", "uid": "st_acs_soll", "key": "st_acs_p04", "unit": "°C", "class": "temperature", "icon": "mdi:water-boiler-marker"},
            {"name": "Puffer-Heizung", "uid": "s_buffer", "key": "st_buffer_c_p123", "unit": "°C", "class": "temperature", "icon": "mdi:heating-coil"},
            {"name": "Umgebungstemperatur", "uid": "s_amb", "key": "st_amb_p05", "unit": "°C", "class": "temperature", "icon": "mdi:home-thermometer"},
            {"name": "Kompressor Frequenz", "uid": "freq", "key": "freq_c15", "unit": "Hz", "class": None, "icon": "mdi:frequency-converter"},
            {"name": "Kompressor Strom", "uid": "curr", "key": "curr_comp_c21", "unit": "A", "class": "current", "icon": "mdi:current-ac"},
            {"name": "Hochdruck", "uid": "pr_alta", "key": "s_pralta_c13", "unit": "bar", "class": "pressure", "icon": "mdi:gauge"},
            {"name": "Niederdruck", "uid": "pr_baja", "key": "s_prbaja_c14", "unit": "bar", "class": "pressure", "icon": "mdi:gauge"},
            {"name": "Netzspannung AC", "uid": "volt_ac", "key": "volt_ac_c23", "unit": "V", "class": "voltage", "icon": "mdi:lightning-bolt"}
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

        # 3. Das Climate-Widget anlegen
        climate_payload = {
            "name": "Domusa Warmwasser",
            "unique_id": f"domusa_{cid}_acs_thermostat",
            "device": device_info,
            "temperature_command_topic": f"domusa/{cid}/set/setACS",
            "current_temperature_topic": f"domusa/{cid}/status",
            "current_temperature_template": "{{ value_json.s_acs_c09 }}",
            "temperature_state_topic": f"domusa/{cid}/status",
            "temperature_state_template": "{{ value_json.st_acs_p04 }}",
            "min_temp": 30,
            "max_temp": 70,
            "temp_step": 1,
            "icon": "mdi:water-boiler-marker"
        }
        await self.mqtt.client.publish(f"homeassistant/climate/domusa_{cid}_acs_thermostat/config", json.dumps(climate_payload), retain=True)
