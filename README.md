# Askoheat+ Integration for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![HA Version](https://img.shields.io/badge/HA-2026.4.0+-blue.svg)](https://www.home-assistant.io/)

A Home Assistant custom integration for [Askoma Askoheat+](https://www.askoma.com/) screw-in and flange heaters. Communicates via the device's local HTTP JSON API — no cloud required.

## Features

- **Water heater** entity with operation modes: Off, Auto (setpoint), Heat (manual step), Feed-in (PV surplus)
- **Temperature sensors** for up to 6 PT1000 probes (auto-detected)
- **Power monitoring** — current heater load, setpoint, feed-in value
- **Full configuration** — all device settings exposed as HA entities (temperature limits, timers, legionella protection, analog thresholds, etc.)
- **Binary sensors** — relay states, emergency mode, heat pump request, error status
- **Device controls** — identify (flash LEDs), clear sensor errors, reboot
- **Operating statistics** — hours per heater, per mode, per step; relay cycle counts
- **Diagnostics** — downloadable device dump for troubleshooting
- **Auto-discovery** via mDNS (askoheat.local / askoheat-eth)

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/Hobby-Student/ha-askoma` as type **Integration**
4. Search for "Askoheat" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/askoheat` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Integrations → Add Integration**
2. Search for **Askoheat**
3. Enter the IP address or hostname of your device (or accept the auto-discovered device)
4. The integration auto-detects connected temperature sensors

### Prerequisites

**Important:** The "Load Setpoint" input must be enabled in the device's web interface under Input Settings for external power control to work. The integration will warn you during setup if this is not configured.

## Configuration

### Options

After setup, go to the integration's options to adjust:

- **Update interval** — how often to poll the device (default: 5 seconds, range: 1–300)

### Entity overview

| Platform | Count | Examples |
|----------|-------|---------|
| Water heater | 1 | Primary control entity with operation modes |
| Sensors | ~41 | Temperatures, power, operating hours, counters |
| Binary sensors | 7 | Relay states, emergency mode, errors |
| Switches | 10 | Input settings, auto-off settings, DST |
| Buttons | 3 | Identify, clear errors, reboot |
| Numbers | 36 | Power setpoint, temperature limits, timers |
| Selects | 18 | Heater step, buffer type, legionella schedule |

## How it works

The integration communicates with the Askoheat+ device over your local network using its HTTP JSON API:

- **Fast polling** (default 5s) — reads real-time data: temperatures, power, status, relay states
- **Slow polling** (60s) — reads configuration, operating hours, counters, extended values
- **Heartbeat** (30s) — re-sends the active power setpoint to prevent the device's 60-second timeout

No data leaves your network. The device's web interface remains fully functional.

## API Reference

- [Askoheat+ JSON API](https://www.download.askoma.com/askofamily_plus/modbus/askoheat-json.html)
- [Askoheat+ Modbus Register Map](https://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html)

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

This project is licensed under the MIT License.
