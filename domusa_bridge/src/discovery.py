import json


class Discovery:
    """Publish Home Assistant MQTT Discovery entities with friendly names."""

    def __init__(self, mqtt, device, lang="en"):
        self.mqtt = mqtt
        self.device = device
        self.lang = lang

    async def _publish(self, component, object_id, payload):
        topic = f"homeassistant/{component}/{object_id}/config"
        payload = {k: v for k, v in payload.items() if v is not None}
        await self.mqtt.client.publish(topic, json.dumps(payload), retain=True)

    @staticmethod
    def _value_template(key, invalid_values=None):
        if invalid_values:
            values = ", ".join(str(v) for v in invalid_values)
            return (
                f"{{% set v = value_json.{key} %}}"
                f"{{% if v not in [{values}] %}}{{{{ v }}}}{{% endif %}}"
            )
        return f"{{{{ value_json.{key} }}}}"

    async def publish(self):
        cid = self.device["id"]
        name = self.device.get("name") or f"Domusa {cid}"
        status_topic = f"domusa/{cid}/status"

        dev_info = {
            "identifiers": [f"domusa_htec_{cid}"],
            "name": name,
            "manufacturer": "Domusa",
            "model": "Dual Clima HT / HTEC Pro",
        }

        # Friendly, useful operating sensors. Raw Domusa field names stay hidden.
        sensors = [
            # Water circuit
            ("flow_temperature", "Flow Temperature", "s_ida_hp_c08", "°C", "temperature", "mdi:thermometer-chevron-up", "measurement", None),
            ("return_temperature", "Return Temperature", "s_ret_hp_c07", "°C", "temperature", "mdi:thermometer-chevron-down", "measurement", None),
            ("delta_t", "Flow / Return Delta", "dt_hp_c11", "°C", "temperature", "mdi:delta", "measurement", None),
            ("active_heating_setpoint", "Active Heating Setpoint", "st_activa_c_f", "°C", "temperature", "mdi:radiator", "measurement", None),
            ("otc_requested_temperature", "OTC Requested Temperature", "st_activa_c_f", "°C", "temperature", "mdi:chart-bell-curve", "measurement", None),
            ("heating_setpoint", "Heating Setpoint", "st_c_p02", "°C", "temperature", "mdi:radiator", "measurement", None),
            ("cooling_setpoint", "Cooling Setpoint", "st_f_p03", "°C", "temperature", "mdi:snowflake", "measurement", None),

            # Buffer / DHW
            ("buffer_temperature", "Buffer Temperature", "s_buffer_c57", "°C", "temperature", "mdi:thermometer-water", "measurement", [-255, -3276.8]),
            ("dhw_temperature", "DHW Temperature", "s_acs_c09", "°C", "temperature", "mdi:water-thermometer", "measurement", [-255, -3276.8]),
            ("dhw_setpoint", "DHW Setpoint", "st_activa_acs", "°C", "temperature", "mdi:water-boiler", "measurement", None),

            # Outdoor / refrigeration circuit
            ("outdoor_temperature", "Outdoor Temperature", "s_ext_c02", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("evaporator_temperature", "Evaporator Temperature", "s_evap_c00", "°C", "temperature", "mdi:thermometer-low", "measurement", [-255, -3276.8]),
            ("evaporating_temperature", "Calculated Evaporating Temperature", "s_evap_calc_c27", "°C", "temperature", "mdi:thermometer-low", "measurement", [-255, -3276.8]),
            ("suction_temperature", "Suction Temperature", "s_suction_c03", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("discharge_temperature", "Discharge Temperature", "s_discharge_c01", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("condenser_temperature", "Condenser Temperature", "s_condens_c06", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("condensing_temperature", "Calculated Condensing Temperature", "s_cond_calc_c28", "°C", "temperature", "mdi:thermometer-high", "measurement", [-255, -3276.8]),
            ("ipm_temperature", "IPM Temperature", "s_ipm_c22", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),
            ("t6_temperature", "T6 Temperature", "s_t6_c25", "°C", "temperature", "mdi:thermometer", "measurement", [-255, -3276.8]),

            # Compressor / fans
            ("compressor_frequency", "Compressor Frequency", "freq_c15", "Hz", "frequency", "mdi:sine-wave", "measurement", None),
            ("compressor_frequency_setpoint", "Compressor Frequency Setpoint", "st_freq_c20", "Hz", "frequency", "mdi:sine-wave", "measurement", None),
            ("compressor_current", "Compressor Current", "curr_comp_c21", "A", "current", "mdi:current-ac", "measurement", None),
            ("compressor_phase_current", "Compressor Phase Current", "curr_ph_comp", "A", "current", "mdi:current-ac", "measurement", None),
            ("fan_1_speed", "Fan 1 Speed", "rpm_vent1_c16", "rpm", None, "mdi:fan", "measurement", None),
            ("fan_2_speed", "Fan 2 Speed", "rpm_vent2_c17", "rpm", None, "mdi:fan", "measurement", None),
            ("eev_position", "Electronic Expansion Valve Position", "eev_c18", "steps", None, "mdi:valve", "measurement", None),

            # Electrical
            ("ac_voltage", "AC Voltage", "volt_ac_c23", "V", "voltage", "mdi:flash", "measurement", None),
            ("dc_bus_voltage", "DC Bus Voltage", "volt_dc_c24", "V", "voltage", "mdi:flash", "measurement", None),
            ("grid_frequency", "Grid Frequency", "e_freq", "Hz", "frequency", "mdi:sine-wave", "measurement", None),

            # Pressures
            ("high_pressure", "High Refrigerant Pressure", "s_pralta_c13", "bar", "pressure", "mdi:gauge-high", "measurement", None),
            ("low_pressure", "Low Refrigerant Pressure", "s_prbaja_c14", "bar", "pressure", "mdi:gauge-low", "measurement", None),

            # Other useful values
            ("water_flow", "Water Flow", "s_q_c10", "L/min", None, "mdi:water", "measurement", None),
            ("compressor_demand", "Compressor Demand", "pwm_c1_c51", "%", None, "mdi:engine", "measurement", None),
            ("p06_hysteresis", "P06 Heating/Cooling Hysteresis", "hyst_c_f_p06", "°C", "temperature", "mdi:delta", "measurement", None),
            ("otc_curve", "OTC Curve", "ck_zona1_p154", None, None, "mdi:chart-bell-curve", "measurement", None),
            ("operation_state", "Operation State", "estado_func_c52", None, None, "mdi:state-machine", None, None),
            ("heat_demand", "Heat Demand", "demanda_hp", None, None, "mdi:fire", None, None),
            ("hp_mode", "Heat Pump Mode", "m_hp_p01", None, None, "mdi:hvac", None, None),
            ("alarm_code", "Alarm Code", "alarma", None, None, "mdi:alert", None, None),
            ("sub_alarm_code", "Sub Alarm Code", "sub_alarma", None, None, "mdi:alert-outline", None, None),
        ]

        for uid, friendly_name, key, unit, device_class, icon, state_class, invalid in sensors:
            payload = {
                "name": friendly_name,
                "object_id": f"domusa_{cid}_{uid}",
                "unique_id": f"domusa_{cid}_{uid}",
                "device": dev_info,
                "state_topic": status_topic,
                "value_template": self._value_template(key, invalid),
                "unit_of_measurement": unit,
                "device_class": device_class,
                "state_class": state_class,
                "icon": icon,
            }
            await self._publish("sensor", f"domusa_{cid}_{uid}", payload)

        # Writable Zone 1 OTC curve (P154).
        otc_curve_number = {
            "name": "OTC Curve",
            "object_id": f"domusa_{cid}_otc_curve_control",
            "unique_id": f"domusa_{cid}_otc_curve_control",
            "device": dev_info,
            "state_topic": status_topic,
            "value_template": "{{ value_json.ck_zona1_p154 }}",
            "command_topic": f"domusa/{cid}/set/setOTCCurve",
            "min": 0.1,
            "max": 2.0,
            "step": 0.1,
            "mode": "slider",
            "icon": "mdi:chart-bell-curve",
        }
        await self._publish("number", f"domusa_{cid}_otc_curve_control", otc_curve_number)

        binary_sensors = [
            ("power", "Heat Pump Power", "on_off_p00", "mdi:power", None),
            ("otc_enabled", "OTC Enabled", "m_otc_p19", "mdi:chart-bell-curve", None),
            ("zone_1_demand", "Zone 1 Demand", "demanda_zona1", "mdi:home-thermometer", None),
            ("zone_2_demand", "Zone 2 Demand", "demanda_zona2", "mdi:home-thermometer", None),
            ("zone_3_demand", "Zone 3 Demand", "demanda_zona3", "mdi:home-thermometer", None),
            ("compressor_enabled", "Compressor Enabled", "m_comp_p40", "mdi:engine", None),
            ("dhw_active", "DHW Active", "m_estadoacs", "mdi:water-boiler", None),
            ("sg_ready", "SG Ready Active", "m_sgready_p201", "mdi:transmission-tower", None),
            ("alarm", "Alarm Active", "alarma", "mdi:alert", "problem"),
        ]

        for uid, friendly_name, key, icon, device_class in binary_sensors:
            if key == "alarma":
                template = "{{ value_json.alarma | int > 0 }}"
            else:
                template = f"{{{{ value_json.{key} }}}}"

            payload = {
                "name": friendly_name,
                "object_id": f"domusa_{cid}_{uid}",
                "unique_id": f"domusa_{cid}_{uid}",
                "device": dev_info,
                "state_topic": status_topic,
                "value_template": template,
                "payload_on": True,
                "payload_off": False,
                "icon": icon,
                "device_class": device_class,
            }
            await self._publish("binary_sensor", f"domusa_{cid}_{uid}", payload)

        # DHW climate entity
        climate = {
            "name": "DHW Thermostat",
            "object_id": f"domusa_{cid}_dhw_thermostat",
            "unique_id": f"domusa_{cid}_dhw_thermostat",
            "device": dev_info,
            "temperature_command_topic": f"domusa/{cid}/set/setACS",
            "current_temperature_topic": status_topic,
            "current_temperature_template": "{{ value_json.s_acs_c09 }}",
            "temperature_state_topic": status_topic,
            "temperature_state_template": "{{ value_json.st_acs_p04 }}",
            "min_temp": 30,
            "max_temp": 70,
            "temp_step": 1,
            "icon": "mdi:water-boiler",
        }
        await self._publish("climate", f"domusa_{cid}_dhw_thermostat", climate)
