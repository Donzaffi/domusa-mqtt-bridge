#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Domusa MQTT Bridge..."

export USERNAME=$(bashio::config 'username')
export PASSWORD=$(bashio::config 'password')

python3 /app/main.py
