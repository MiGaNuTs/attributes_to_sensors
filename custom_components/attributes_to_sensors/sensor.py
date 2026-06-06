"""Attribute to Sensor — one sensor per attribute of a source entity."""
from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

UNIT_SUFFIX = "_unit"

KNOWN_UNITS: dict[str, str] = {
    "temperature": "°C",
    "humidity": "%",
    "pressure": "hPa",
    "wind_speed": "km/h",
    "wind_gust_speed": "km/h",
    "wind_bearing": "°",
    "visibility": "km",
    "cloud_coverage": "%",
    "dew_point": "°C",
    "apparent_temperature": "°C",
    "power": "W",
    "current_power_w": "W",
    "energy": "kWh",
    "today_energy_kwh": "kWh",
    "voltage": "V",
    "current": "A",
    "battery": "%",
    "battery_level": "%",
    "illuminance": "lx",
    "co2": "ppm",
    "pm25": "µg/m³",
    "pm10": "µg/m³",
    "noise": "dB",
}

KNOWN_DEVICE_CLASSES: dict[str, str] = {
    "temperature": "temperature",
    "dew_point": "temperature",
    "apparent_temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure",
    "wind_speed": "wind_speed",
    "wind_gust_speed": "wind_speed",
    "visibility": "distance",
    "power": "power",
    "current_power_w": "power",
    "energy": "energy",
    "today_energy_kwh": "energy",
    "voltage": "voltage",
    "current": "current",
    "battery": "battery",
    "battery_level": "battery",
    "illuminance": "illuminance",
    "co2": "carbon_dioxide",
    "pm25": "pm25",
    "pm10": "pm10",
}

INTERNAL_ATTRS = {
    "friendly_name", "icon", "entity_picture",
    "supported_features", "attribution",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one sensor per attribute of the source entity, plus one for state."""
    entity_id = entry.options.get("entity_id", entry.data.get("entity_id"))
    state = hass.states.get(entity_id)

    if state is None:
        _LOGGER.warning("Source entity %s not found at setup time.", entity_id)
        return

    attrs = state.attributes

    # Find *_unit attributes to use as unit sources
    unit_map: dict[str, str] = {}
    for key, value in attrs.items():
        if key.endswith(UNIT_SUFFIX):
            base = key[: -len(UNIT_SUFFIX)]
            unit_map[base] = str(value)

    skip = (
        {f"{k}{UNIT_SUFFIX}" for k in unit_map}
        | INTERNAL_ATTRS
    )

    sensors = []

    # Special sensor for the entity state itself
    sensors.append(
        AttributeSensor(
            hass=hass,
            entry=entry,
            source_entity_id=entity_id,
            attr_name="state",
            unit=None,
            device_class=None,
            is_state=True,
        )
    )

    # One sensor per attribute
    for attr_name, attr_value in attrs.items():
        if attr_name in skip:
            continue
        if attr_name.endswith(UNIT_SUFFIX):
            continue

        unit = unit_map.get(attr_name) or KNOWN_UNITS.get(attr_name)
        device_class = KNOWN_DEVICE_CLASSES.get(attr_name)

        sensors.append(
            AttributeSensor(
                hass=hass,
                entry=entry,
                source_entity_id=entity_id,
                attr_name=attr_name,
                unit=unit,
                device_class=device_class,
                is_state=False,
            )
        )

    _LOGGER.debug("Created %d sensors for %s", len(sensors), entity_id)
    async_add_entities(sensors)


class AttributeSensor(SensorEntity):
    """A sensor that mirrors one attribute (or the state) of a source entity."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        source_entity_id: str,
        attr_name: str,
        unit: str | None,
        device_class: str | None,
        is_state: bool = False,
    ):
        self.hass = hass
        self._entry = entry
        self._source_entity_id = source_entity_id
        self._attr_name_key = attr_name
        self._is_state = is_state
        self._attr_unique_id = f"{entry.entry_id}_{attr_name}"
        self._attr_name = (
            f"{source_entity_id.split('.')[1]} {attr_name}".replace("_", " ").title()
        )
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_native_value = None
        self._update()

    async def async_added_to_hass(self) -> None:
        """Listen for state changes on the source entity."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._source_entity_id],
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self, event) -> None:
        """Called when source entity state changes."""
        self._update()
        self.async_write_ha_state()

    def _update(self) -> None:
        """Read value from source entity."""
        state = self.hass.states.get(self._source_entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            self._attr_available = False
            return
        self._attr_available = True
        if self._is_state:
            self._attr_native_value = state.state
        else:
            self._attr_native_value = state.attributes.get(self._attr_name_key)
