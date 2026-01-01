<!-- prettier-ignore -->
# Ecoflow PowerOcean

[Home Assistant](https://home-assistant.io/) custom component to get access to PowerOcean system from EcoFlow.

This component is a fork of [jdammers/powerocean](https://github.com/jdammers/powerocean) and was updated to use the new API.

Temporary quick solution.
The official API documentation can be found at [https://developer-eu.ecoflow.com/us/document/powerocean](https://developer-eu.ecoflow.com/us/document/powerocean).

## Prerequisites

- You need the serial number of your inverter
- Go to [https://developer-eu.ecoflow.com/us/security](https://developer-eu.ecoflow.com/us/security), login and create an AccessKey with a SecretKey
- Instead of username and password you will need the AccessKey and the SecretKey for login

## Disclaimer

The following parts of the document are copy-pasted from [jdammers/powerocean](https://github.com/jdammers/powerocean)

## Installation

- Install as a custom repository via HACS
- Manually download and extract to the custom_components directory

Once installed, use Add Integration -> Ecoflow PowerOcean.

## Configuration

Follow the flow.

![step 1](documentation/setup_step_1.PNG)
![step 2](documentation/setup_step_2.PNG)



### Sensors
Sensors are registered to each device as `sensor.{name}_{serial}_{sensor_name}` with an friendly name of `sensor_name`. Additional attributes are presented on each sensor:
- Product Description, Destination Name, Source Name: internal names
- Internal Unique ID: `{serial}_{sensor_name}`
- Device Name: as
- Vendor Product Serial: serial number of the PowerOcean inverter
- Vendor Firmware Version: 5.1.8
- Vendor Product Build: 13
  
![sensor](documentation/sensor.PNG)


## Troubleshooting
Please set your logging for the this custom component to debug during initial setup phase. If everything works well, you are safe to remove the debug logging:

```yaml
logger:
  default: warn
  logs:
    custom_components.powerocean: info
```

## Credits

Thanks to my kollege David for giving me a start point.

And also thanks for the great work of the team from homeassistant and the great community.