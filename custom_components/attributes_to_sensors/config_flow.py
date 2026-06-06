"""Config flow for Attribute to Sensor."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.selector as selector

from . import DOMAIN


class AttributeToSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow — just pick a source entity."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Single step: select the source entity."""
        if user_input is not None:
            entity_id = user_input["entity_id"]
            # Use entity_id as unique_id to prevent duplicates
            await self.async_set_unique_id(entity_id)
            self._abort_if_unique_id_configured()
            # Use entity_id as title for clarity
            return self.async_create_entry(
                title=entity_id,
                data={"entity_id": entity_id},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("entity_id"): selector.selector(
                        {"entity": {}}
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        """Return the options flow handler."""
        return AttributeToSensorOptionsFlow(entry)


class AttributeToSensorOptionsFlow(config_entries.OptionsFlow):
    """Allow changing the source entity after setup."""

    def __init__(self, entry):
        self._entry = entry

    async def async_step_init(self, user_input=None):
        """Change the source entity."""
        current = self._entry.data.get("entity_id", "")

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("entity_id", default=current): selector.selector(
                        {"entity": {}}
                    ),
                }
            ),
        )
