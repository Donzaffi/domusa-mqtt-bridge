import json

class Discovery:
    def __init__(self, mqtt, device):
        self.mqtt = mqtt
        self.device = device

    async def publish(self):
        cid = self.device["id"]
        dev_info = {"identifiers": [cid], "name": "Domusa HTEC", "manufacturer": "Domusa", "model": "HTEC Pro 12"}

        sensors = [
            # Temperaturen (div 10)
            {"name": "Verdampfertemperatur", "uid": "s_evap", "key": "s_evap_c00", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Verdichter Druckgastemperatur", "uid": "s_discharge", "key": "s_discharge_c01", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Sauggastemperatur", "uid": "s_suction", "key": "s_suction_c03", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Kondensatortemperatur", "uid": "s_condens", "key": "s_condens_c06", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Heizung Solltemperatur", "uid": "st_heat", "key": "st_c_p02", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Kühlung Solltemperatur", "uid": "st_cool", "key": "st_f_p03", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Aktiver Heizsollwert", "uid": "st_active_heat", "key": "st_activa_c_f", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Aktiver Warmwasser Sollwert", "uid": "st_active_acs", "key": "st_activa_acs", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Kompressor IPM Temperatur", "uid": "ipm_temp", "key": "s_ipm_c22", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "T6 Temperatur", "uid": "t6_temp", "key": "s_t6_c25", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Externer Zonenfühler", "uid": "zone_ext_temp", "key": "s_zonaext_c75", "unit": "°C", "class": "temperature", "div": 1},
            {"name": "Temperaturdifferenz", "uid": "delta_t", "key": "dt_hp_c11", "unit": "°C", "class": "temperature", "div": 1},
            
            # Elektrische Werte & Sonstige (Skalierung je nach Einheit)
            {"name": "Kompressor Phasenstrom", "uid": "phase_current", "key": "curr_ph_comp", "unit": "A", "class": "current", "div": 1},
            {"name": "Zwischenkreisspannung", "uid": "volt_dc", "key": "volt_dc_c24", "unit": "V", "class": "voltage", "div": 1},
            {"name": "Lüfter 1 Drehzahl", "uid": "fan1_rpm", "key": "rpm_vent1_c16", "unit": "rpm", "class": None, "div": 1},
            {"name": "Lüfter 2 Drehzahl", "uid": "fan2_rpm", "key": "rpm_vent2_c17", "unit": "rpm", "class": None, "div": 1},
            {"name": "EEV Position", "uid": "eev_position", "key": "eev_c18", "unit": "steps", "class": None, "div": 1},
            {"name": "PWM Ventil", "uid": "pwm", "key": "pwm_c1_c51", "unit": "%", "class": None, "div": 1},
            {"name": "Wärmeleistung", "uid": "thermal_power", "key": "s_q_c10", "unit": "kW", "class": "power", "div": 1},
            {"name": "Betriebszustand", "uid": "operation_state", "key": "estado_func_c52", "unit": None, "class": None, "div": 1},
            {"name": "Wärmepumpenmodus", "uid": "hp_mode", "key": "m_hp_p01", "unit": None, "class": None, "div": 1},
            {"name": "Netzfrequenz", "uid": "grid_frequency", "key": "e_freq", "unit": "Hz", "class": "frequency", "div": 1},
            {"name": "Heizkreis Zone 1 Soll", "uid": "zone1_heat_setpoint", "key": "st_zona1_c_p158", "unit": "°C", "class": "temperature", "div": 1}
        ]

        for s in sensors:
            template = f"{{{{ (value_json.{s['key']} | float) / {s['div']} }}}}" if s['div'] > 1 else f"{{{{ value_json.{s['key']} }}}}"
            payload = {
                "name": f"Domusa {s['name']}",
                "unique_id": f"domusa_{cid}_{s['uid']}",
                "device": dev_info,
                "state_topic": f"domusa/{cid}/status",
                "value_template": template,
                "unit_of_measurement": s['unit'],
                "device_class": s['class'],
                "state_class": "measurement" if s['unit'] else None
            }
            await self.mqtt.client.publish(f"homeassistant/sensor/domusa_{cid}_{s['uid']}/config", json.dumps(payload), retain=True)

        # Zusätzlich das Climate-Gerät für Warmwasser (ACS)
        climate = {
            "name": "Domusa Warmwasser",
            "unique_id": f"domusa_{cid}_acs_thermostat",
            "device": dev_info,
            "temperature_command_topic": f"domusa/{cid}/set/setACS",
            "current_temperature_topic": f"domusa/{cid}/status",
            "current_temperature_template": "{{ (value_json.s_acs_c09 | float) / 10 }}",
            "temperature_state_topic": f"domusa/{cid}/status",
            "temperature_state_template": "{{ (value_json.st_acs_p04 | float) / 10 }}",
            "min_temp": 30, "max_temp": 70, "temp_step": 1,
            "icon": "mdi:water-boiler-marker"
        }
        await self.mqtt.client.publish(f"homeassistant/climate/domusa_{cid}_acs_thermostat/config", json.dumps(climate), retain=True)
