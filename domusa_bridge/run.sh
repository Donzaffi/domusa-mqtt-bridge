#!/usr/bin/with-contenv bashio

# Optional: Logging in HA anzeigen
bashio::log.info "Starting Domusa MQTT Bridge..."

# Starte das Python-Skript
python3 /app/main.py
