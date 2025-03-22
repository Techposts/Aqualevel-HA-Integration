# AquaLevel Home Assistant Integration

This custom component integrates your AquaLevel water tank monitoring system with Home Assistant, allowing you to monitor water levels, configure tank parameters, and receive alerts.

## Features

- **Automatic Discovery**: Finds your AquaLevel devices on your network using mDNS
- **Water Level Monitoring**: View real-time water level, percentage, and volume
- **Tank Configuration**: Set up tank dimensions, calibration, and alert thresholds
- **Alerts**: Get notifications for low and high water levels
- **Device Registry**: All entities are properly grouped under a single device in Home Assistant

## Prerequisites

- Home Assistant installed and running (version 2023.3.0 or later)
- AquaLevel device connected to your network
- The device should have an IP address that is reachable from your Home Assistant instance

## Installation

### HACS (Home Assistant Community Store) - Recommended

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations > ⋮ > Custom repositories
3. Add this repository URL with category "Integration"
4. Click "Install" on the AquaLevel integration
5. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Extract the `custom_components/aqualevel` directory into your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Automatic Discovery (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click the "+ Add Integration" button in the bottom-right corner
3. Search for "AquaLevel" and select it
4. If your AquaLevel device is on the network, it should be discovered automatically
5. Follow the prompts to complete the setup

### Manual Configuration

If automatic discovery doesn't find your device:

1. Go to **Settings** → **Devices & Services**
2. Click the "+ Add Integration" button
3. Search for "AquaLevel" and select it
4. Enter the IP address of your AquaLevel device
5. Enter a name for your device (optional)
6. Click "Submit"

## Entities

After setting up the integration, you'll have access to the following entities:

### Sensors
- **Distance**: Shows the current distance detected by the ultrasonic sensor (cm)
- **Water Level**: Shows the current water level height in the tank (cm)
- **Water Percentage**: Shows the water level as a percentage of the tank capacity (%)
- **Water Volume**: Shows the current water volume in the tank (liters)
- **Tank Capacity**: Shows the maximum tank capacity (liters)
- **Measurement Interval**: Shows how often measurements are taken (seconds)

### Binary Sensors
- **Low Water Alert**: Indicates when water level falls below the low alert threshold
- **High Water Alert**: Indicates when water level rises above the high alert threshold

### Numbers
- **Tank Height**: Set the height of your water tank (cm)
- **Tank Diameter**: Set the diameter of your cylindrical tank (cm)
- **Tank Volume**: Set the maximum volume of your tank (liters)
- **Sensor Offset**: Set the distance from sensor to maximum water level (cm)
- **Empty Distance**: Set the distance reading when tank is empty (cm)
- **Full Distance**: Set the distance reading when tank is full (cm)
- **Measurement Interval**: Set how often measurements are taken (seconds)
- **Reading Smoothing**: Set the number of readings to average for smoother results
- **Low Alert Level**: Set the percentage threshold for low water alerts (%)
- **High Alert Level**: Set the percentage threshold for high water alerts (%)

### Switches
- **Alerts Enabled**: Toggle to enable/disable low and high water alerts

### Buttons
- **Calibrate Empty Tank**: Calibrate the sensor when the tank is empty
- **Calibrate Full Tank**: Calibrate the sensor when the tank is full

## Services

The integration provides the following services:

### `aqualevel.calibrate`
Calibrate the tank sensor for empty or full level.

Parameters:
- `entity_id`: Entity ID of any AquaLevel entity
- `calibration_type`: Type of calibration to perform (`empty` or `full`)

### `aqualevel.update_settings`
Update multiple settings at once.

Parameters:
- `entity_id`: Entity ID of any AquaLevel entity
- `tank_height`: Height of the water tank (cm)
- `tank_diameter`: Diameter of the water tank (cm)
- `tank_volume`: Total volume of the water tank (liters)
- `sensor_offset`: Distance from sensor to maximum water level (cm)
- `empty_distance`: Distance reading when tank is empty (cm)
- `full_distance`: Distance reading when tank is full (cm)
- `measurement_interval`: Time between measurements (seconds)
- `reading_smoothing`: Number of readings to average
- `alert_level_low`: Percentage for low water alert (%)
- `alert_level_high`: Percentage for high water alert (%)
- `alerts_enabled`: Enable or disable alerts (boolean)

## Automation Examples

Here are some examples of how you can use this integration in your Home Assistant automations:

### Send a notification when water level is low

```yaml
automation:
  - alias: "Low water level notification"
    trigger:
      platform: state
      entity_id: binary_sensor.aqualevel_low_water_alert
      to: "on"
    action:
      service: notify.mobile_app
      data:
        title: "Low Water Level Alert"
        message: "Water tank is running low! Current level: {{ states('sensor.aqualevel_water_percentage') }}%"
```

### Log water levels to a database

```yaml
automation:
  - alias: "Log water level daily"
    trigger:
      platform: time_pattern
      hours: "0"
      minutes: "0"
    action:
      service: logbook.log
      data:
        name: "Water Tank Stats"
        message: >
          Water level: {{ states('sensor.aqualevel_water_percentage') }}%, 
          Volume: {{ states('sensor.aqualevel_water_volume') }} liters
```

### Remind to check water level weekly

```yaml
automation:
  - alias: "Weekly water check reminder"
    trigger:
      platform: time
      at: "10:00:00"
      weekday: "mon"
    action:
      service: persistent_notification.create
      data:
        title: "Water Tank Check"
        message: >
          Time for your weekly water tank check!
          Current level is {{ states('sensor.aqualevel_water_percentage') }}%.
```

## Troubleshooting

### Device Not Discovered

- Ensure your AquaLevel device is powered on and connected to your network
- Check that mDNS (Bonjour/Avahi) is working on your network
- Try manual configuration with the IP address instead

### Cannot Connect to Device

- Verify you can access the web interface directly at `http://<IP_ADDRESS>/`
- Check if your firewall is blocking connections to the device
- Ensure the ESP32 is connected to your network and has a stable connection
- Try restarting both the AquaLevel device and Home Assistant

### Calibration Issues

- Make sure the tank is actually empty when calibrating "empty"
- Make sure the water level is stable during calibration
- Check if there are any obstructions or debris affecting the ultrasonic sensor
- Try a manual calibration via the device's web interface

## Advanced Configuration

### Using mDNS Hostname

If your network supports mDNS (most do), you can use the hostname instead of IP:

1. The device hostname format is `aqualevel-<location>.local`
2. For example: `aqualevel-garden.local`

### Setting Up Static IP

For more reliable connectivity, set up a static IP for your AquaLevel device:

1. Access your router's DHCP settings
2. Find the MAC address of your AquaLevel device 
3. Assign a static IP to that MAC address

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Created by Ravi Singh (TechPosts Media)
- Home Assistant component developed by the AquaLevel community
