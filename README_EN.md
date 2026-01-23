# Aqara Camera G3 Integration for Home Assistant

[Tiếng Việt](README.md) | [English](README_EN.md)

Integration for Aqara Camera G3 in Home Assistant, installable via HACS.

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to the "Integrations" tab
3. Click the 3-dot menu in the top right
4. Choose "Custom repositories"
5. Add this repository URL and choose category "Integration"
6. Find "Aqara Camera G3" and click "Install"
7. Restart Home Assistant

### Manual installation

1. Copy `custom_components/aqara_g3` into your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings > Devices & Services > Add Integration
4. Search "Aqara Camera G3" and follow the steps

## Configuration

After installation, just sign in with your Aqara account:

- **Username**: Aqara account (email/phone)
- **Password**: Aqara password
- **Area**: CN/EU/US/HMT/OTHER...

The integration will automatically fetch **Token**, **App ID**, **User ID** and device list, then you select **Subject ID**.

## Credentials

No manual steps needed. The integration logs in and fetches everything automatically.

## Features

- Sensors for detection states (Motion, Face, Pets, Human)
- WiFi RSSI sensor
- Alarm status sensor

## Support

If you run into issues, please open an issue on GitHub.

## Credits

This project is based on: https://github.com/sdavides/AqaraPOST-Homeassistant
