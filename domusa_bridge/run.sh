#!/usr/bin/with-contenv bashio

bashio::log.info "Domusa MQTT Bridge starting..."

export USERNAME=$(bashio::config 'username')
export PASSWORD=$(bashio::config 'password')
export POLL_INTERVAL=$(bashio::config 'poll_interval')
export ZONE=$(bashio::config 'zone')

python3 /app/main.py
