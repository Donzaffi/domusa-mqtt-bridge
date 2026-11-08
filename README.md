# Domusa MQTT Bridge

[![GitHub Issues](https://img.shields.io/github/issues/Macrisu/domusa-mqtt-bridge-multiple)](https://github.com/Macrisu/domusa-mqtt-bridge-multiple/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Home Assistant Add-on acts as a bridge between your **Domusa heating system** and your local **MQTT broker**. 
It retrieves data from the Domusa cloud API and makes it available within Home Assistant for visualisation and automation.

This is a fork of [**Donzaffi/domusa-mqtt-bridge**](https://github.com/Donzaffi/domusa-mqtt-bridge).

I modified it to support multiple heat pumps in the iConnect account and automatically create sensors in Home Assistant. 

## How it works

This add-on bridges the gap between the manufacturer's cloud service and your local smart home:

* **Cloud API Integration:** The add-on communicates with the official Domusa cloud API (hosted on Azure) to fetch system status and send commands.
* **Local MQTT:** Once the data is retrieved, it is published to your local MQTT broker. This allows you to integrate your heating data seamlessly into Home Assistant dashboards and automations.

* **Requirements:**
  - A stable internet connection is required for the bridge to communicate with the Domusa cloud services and **Domusa iConnect Module**.
  - An MQTT broker is installed (independent or as an add-on in Home Assistant).

## Disclaimer

This project is an independent, community-driven integration and is **not officially affiliated with or endorsed by Domusa**. 

* **Cloud Dependency:** This is not a local-only (LAN) integration. It relies on the manufacturer's cloud API.
* **Use at your own risk:** As this project relies on an undocumented or official cloud API, changes to the manufacturer's infrastructure or firmware updates may affect the functionality of this add-on. 

## Installation

1.  Navigate to your Home Assistant **Settings** -> **Add-ons**.
2.  Click the **three-dot menu** in the top right corner and select **Repositories**.
3.  Add this repository URL: `https://github.com/Macrisu/domusa-mqtt-bridge-multiple`
4.  Click **Add** and then **Close**.
5.  Search for **Domusa MQTT Bridge** in the Add-on store and click **Install**.

## Configuration

After installation, go to the **Configuration** tab of the add-on to provide your credentials and MQTT settings:

```yaml
username: xxx@xxx.com # your iConnect email address account
password: yyyyyy # # your iConnect account password
mqtt_host: xxx.xxx.xx.xx # IP of the MQTT server
mqtt_port: 1883 # port of the MQTT server
mqtt_user: xxx # MQTTT username
mqtt_password: xxx # MQTT pass
language: en
poll_interval: 60
```

*Note: Your credentials are used locally by the add-on to authenticate with the Domusa API and are not shared with any third party.*

## Home Assistant dashboard example

You can customise your dashboard as you want, but here is an example.

1. Go to _Settings - Dashboards - Add Dashboard (New dashboard from scratch)._

Give it a _Title_ (ex: Domusa HP) and activate _Add to sidebar._

Go to the newly created Dashboard, click on the pencil icon to edit, then click on the 3 dots and select _Raw configuration editor_.

Paste the code from [here](/dashboard_exemple.yaml) and use the search and replace function in order to change **xxxxxx** to your **numeric installation ID**.

2. Add the codes from [this file](/configuration.yaml) to the specific areas of your Home Assistant **configuration.yaml** file and restart Home Assistant. You can use the File Editor Add-on.

You can find the numeric installation ID on the iConnect app or on the Working Status on your LCD.

See [Picture 1](/images/dashboard1.jpg) and [Picture 2](/images/dashboard2.jpg).


## Support

If you encounter any issues or have feature requests, please [open an issue on GitHub](https://github.com/Macrisu/domusa-mqtt-bridge-multiple/issues). 
Contributions are welcome!

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
