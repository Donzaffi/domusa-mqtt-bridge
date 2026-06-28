#!/usr/bin/with-contenv bashio

bashio::log.info "Starting Domusa MQTT Bridge..."

export USERNAME=$(bashio::config 'username')
export PASSWORD=$(bashio::config 'password')
export POLL_INTERVAL=$(bashio::config 'poll_interval')

python3 /app/main.py
