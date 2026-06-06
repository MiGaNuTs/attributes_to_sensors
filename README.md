# Attribute to Sensor

A Home Assistant custom component that exposes every attribute of any entity as individual sensor entities.

## Why?

HA entities often carry useful data in their attributes — weather entities have temperature, humidity, pressure; smart plugs have power, energy, voltage; and so on. These attributes are hard to use in dashboards, automations, or history graphs because they're not first-class entities.

This integration solves that: point it at any entity, and it creates one sensor per attribute automatically.

## Features

- Works with **any entity type** — weather, switches, sensors, media players, etc.
- **Automatic unit detection** — reads `*_unit` sibling attributes (e.g. `temperature_unit`) and falls back to a built-in dictionary of known units
- **Automatic device_class** — maps known attribute names to the right device class
- `*_unit` attributes are consumed silently — they set the unit of their sibling sensor and are not exposed as sensors themselves
- Unavailable source → all derived sensors go unavailable cleanly
- Disable individual sensors via the HA UI — no need to configure which attributes to expose

## Installation

### Via HACS (recommended)

1. In HACS, go to **Integrations → Custom repositories**
2. Add this repository URL, category: **Integration**
3. Install **Attribute to Sensor**
4. Restart Home Assistant

### Manual

1. Copy `custom_components/attribute_to_sensor/` into your HA `/config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration → Attribute to Sensor**
2. Select the source entity
3. One sensor is created per attribute — disable the ones you don't need via the HA UI

You can add multiple instances to expose attributes from multiple entities.

## Requirements

- Home Assistant 2024.1 or newer

## License

MIT
