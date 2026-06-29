# Domusa MQTT Bridge

[![GitHub Issues](https://img.shields.io/github/issues/Donzaffi/domusa-mqtt-bridge)](https://github.com/Donzaffi/domusa-mqtt-bridge/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Home Assistant Add-on acts as a bridge between your **Domusa heating system** and your local **MQTT broker**. It retrieves data from the Domusa cloud API and makes it available within Home Assistant for visualization and automation.

## How it works

This add-on bridges the gap between the manufacturer's cloud service and your local smart home:

* **Cloud API Integration:** The add-on communicates with the official Domusa cloud API (hosted on Azure) to fetch system status and send commands.
* **Local MQTT:** Once the data is retrieved, it is published to your local MQTT broker. This allows you to integrate your heating data seamlessly into Home Assistant dashboards and automations.
* **Requirements:** A stable internet connection is required for the bridge to communicate with the Domusa cloud services.

## Disclaimer

This project is an independent, community-driven integration and is **not officially affiliated with or endorsed by Domusa**. 

* **Cloud Dependency:** This is not a local-only (LAN) integration. It relies on the manufacturer's cloud API.
* **Use at your own risk:** As this project relies on an undocumented or official cloud API, changes to the manufacturer's infrastructure or firmware updates may affect the functionality of this add-on. 

## Installation

1.  Navigate to your Home Assistant **Settings** -> **Add-ons**.
2.  Click the **three-dot menu** in the top right corner and select **Repositories**.
3.  Add this repository URL: `https://github.com/Donzaffi/domusa-mqtt-bridge`
4.  Click **Add** and then **Close**.
5.  Search for **Domusa MQTT Bridge** in the Add-on store and click **Install**.

## Configuration

After installation, go to the **Configuration** tab of the add-on to provide your credentials and MQTT settings:

```yaml
mqtt_broker: "core-mosquitto"
mqtt_port: 1883
mqtt_user: "your_mqtt_username"
mqtt_password: "your_mqtt_password"
domusa_user: "your_domusa_app_email"
domusa_password: "your_domusa_app_password" ```

*Note: Your credentials are used locally by the add-on to authenticate with the Domusa API and are not shared with any third party.*

## Sensor Naming

The sensors provided by this add-on are currently named in German. If you prefer a different language, you can easily rename the entities directly within Home Assistant:

1. Go to **Settings** -> **Devices & Services** -> **Entities**.
2. Find the sensor you want to rename.
3. Click on the sensor name and change it to your preferred language.

Home Assistant will remember these custom names even after updates.

## Support

If you encounter any issues or have feature requests, please [open an issue on GitHub](https://github.com/Donzaffi/domusa-mqtt-bridge/issues). Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
