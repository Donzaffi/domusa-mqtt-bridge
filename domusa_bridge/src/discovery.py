import json

class Discovery:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish(self):
        cid = self.device["id"]
        dev_info = {"identifiers": [cid], "name": "Domusa HTEC", "manufacturer": "Domusa", "model": "HTEC Pro 12"}

        sensors = [
            {"name": "Verdampfertemperatur", "uid": "s_evap", "key": "s_evap_c00", "unit": "°C", "class": "temperature", "icon": "mdi:snowflake-thermometer"},
            {"name": "Verdichter Druckgastemperatur", "uid": "s_discharge", "key": "s_discharge_c01", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer-chevron-up"},
            {"name": "Sauggastemperatur", "uid": "s_suction", "key": "s_suction_c03", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer-chevron-down"},
            {"name": "Kondensatortemperatur", "uid": "s_condens", "key": "s_condens_c06", "unit": "°C", "class": "temperature", "icon": "mdi:radiator"},
            {"name": "Heizung Solltemperatur", "uid": "st_heat", "key": "st_c_p02", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer-plus"},
            {"name": "Kühlung Solltemperatur", "uid": "st_cool", "key": "st_f_p03", "unit": "°C", "class": "temperature", "icon": "mdi:snowflake"},
            {"name": "Aktiver Heizsollwert", "uid": "st_active_heat", "key": "st_activa_c_f", "unit": "°C", "class": "temperature", "icon": "mdi:thermostat"},
            {"name": "Aktiver Warmwasser Sollwert", "uid": "st_active_acs", "key": "st_activa_acs", "unit": "°C", "class": "temperature", "icon": "mdi:water-thermometer"},
            {"name": "Kompressor IPM Temperatur", "uid": "ipm_temp", "key": "s_ipm_c22", "unit": "°C", "class": "temperature", "icon": "mdi:chip"},
            {"name": "T6 Temperatur", "uid": "t6_temp", "key": "s_t6_c25", "unit": "°C", "class": "temperature", "icon": "mdi:thermometer"},
            {"name": "Externer Zonenfühler", "uid": "zone_ext_temp", "key": "s_zonaext_c75", "unit": "°C", "class": "temperature", "icon": "mdi:home-thermometer-outline"},
            {"name": "Kompressor Phasenstrom", "uid": "phase_current", "key": "curr_ph_comp", "unit": "A", "class": "current", "icon": "mdi:current-ac"},
            {"name": "Zwischenkreisspannung", "uid": "volt_dc", "key": "volt_dc_c24", "unit": "V", "class": "voltage", "icon": "mdi:lightning-bolt"},
            {"name": "Lüfter 1 Drehzahl", "uid": "fan1_rpm", "key": "rpm_vent1_c16", "unit": "rpm", "class": None, "icon": "mdi:fan"},
            {"name": "Lüfter 2 Drehzahl", "uid": "fan2_rpm", "key": "rpm_vent2_c17", "unit": "rpm", "class": None, "icon": "mdi:fan"},
            {"name": "EEV Position", "uid": "eev_position", "key": "eev_c18", "unit": "steps", "class": None, "icon": "mdi:valve"},
            {"name": "PWM Ventil", "uid": "pwm", "key": "pwm_c1_c51", "unit": "%", "class": None, "icon": "mdi:pulse"},
            {"name": "Temperaturdifferenz", "uid": "delta_t", "key": "dt_hp_c11", "unit": "°C", "class": "temperature", "icon": "mdi:delta"},
            {"name": "Wärmeleistung", "uid": "thermal_power", "key": "s_q_c10", "unit": "kW", "class": "power", "icon": "mdi:heat-wave"},
            {"name": "Betriebszustand", "uid": "operation_state", "key": "estado_func_c52", "unit": None, "class": None, "icon": "mdi:cog"},
            {"name": "Wärmepumpenmodus", "uid": "hp_mode", "key": "m_hp_p01", "unit": None, "class": None, "icon": "mdi:heat-pump"},
            {"name": "Netzfrequenz", "uid": "grid_frequency", "key": "e_freq", "unit": "Hz", "class": "frequency", "icon": "mdi:sine-wave"},
            {"name": "Heizkreis Zone 1 Soll", "uid": "zone1_heat_setpoint", "key": "st_zona1_c_p158", "unit": "°C", "class": "temperature", "icon": "mdi:home-thermometer"}
        ]

        for s in sensors:
            payload = {
                "name": f"Domusa {s['name']}",
                "unique_id": f"domusa_{cid}_{s['uid']}",
                "device": dev_info,
                "state_topic": f"domusa/{cid}/status",
                "value_template": f"{{{{ value_json.{s['key']} }}}}",
                "unit_of_measurement": s['unit'],
                "device_class": s['class'],
                "state_class": "measurement" if s['unit'] else None,
                "icon": s['icon']
            }
            await self.mqtt.client.publish(f"homeassistant/sensor/domusa_{cid}_{s['uid']}/config", json.dumps(payload), retain=True)

        climate = {
            "name": "Domusa Warmwasser",
            "unique_id": f"domusa_{cid}_acs_thermostat",
            "device": dev_info,
            "temperature_command_topic": f"domusa/{cid}/set/setACS",
            "current_temperature_topic": f"domusa/{cid}/status",
            "current_temperature_template": "{{ value_json.s_acs_c09 }}",
            "temperature_state_topic": f"domusa/{cid}/status",
            "temperature_state_template": "{{ value_json.st_acs_p04 }}",
            "min_temp": 30, "max_temp": 70, "temp_step": 1,
            "icon": "mdi:water-boiler-marker"
        }
        await self.mqtt.client.publish(f"homeassistant/climate/domusa_{cid}_acs_thermostat/config", json.dumps(climate), retain=True)
