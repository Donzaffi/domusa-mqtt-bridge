# Domusa MQTT Bridge

[![GitHub Issues](https://img.shields.io/github/issues/Donzaffi/domusa-mqtt-bridge)](https://github.com/Donzaffi/domusa-mqtt-bridge/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Home Assistant Add-on provides a bridge between your **Domusa heating system** and an **MQTT broker**. It allows you to monitor and control your heating system locally within Home Assistant without relying on third-party cloud services.

## Features

*   **Real-time Monitoring:** Get live data from your Domusa unit directly into Home Assistant.
*   **Full Local Control:** Manage your heating settings via MQTT.
*   **Privacy Focused:** Runs locally on your Home Assistant instance; no external cloud dependency.
*   **Easy Integration:** Designed as a Home Assistant Add-on for seamless deployment.

## Prerequisites

*   A running Home Assistant instance.
*   An MQTT Broker (e.g., Mosquitto) installed and configured in Home Assistant.
*   Your Domusa device accessible on your local network.

## Installation

1.  Navigate to your Home Assistant **Settings** -> **Add-ons**.
2.  Click the **three-dot menu** in the top right corner and select **Repositories**.
3.  Add this repository URL: `https://github.com/Donzaffi/domusa-mqtt-bridge`
4.  Click **Add** and then **Close**.
5.  Refresh the Add-on store page. The **Domusa MQTT Bridge** will appear in the list.
6.  Click on the Add-on and select **Install**.

## Configuration

After installation, go to the **Configuration** tab of the add-on and provide your MQTT connection details:

```yaml
mqtt_broker: "core-mosquitto"
mqtt_port: 1883
mqtt_user: "your_username"
mqtt_password: "your_password"
# Add your specific device settings here
