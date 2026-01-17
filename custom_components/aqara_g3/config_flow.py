"""Config flow for Aqara Camera G3 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import AqaraG3API
from .const import (
    CONF_AQARA_URL,
    CONF_APPID,
    CONF_FACE_MAP,
    CONF_FACE_NAME_MAP,
    CONF_SUBJECT_ID,
    CONF_TOKEN,
    CONF_USERID,
    DEFAULT_AQARA_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AQARA_URL, default=DEFAULT_AQARA_URL): str,
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_APPID): str,
        vol.Required(CONF_USERID): str,
        vol.Required(CONF_SUBJECT_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api = AqaraG3API(
        session=session,
        aqara_url=data[CONF_AQARA_URL],
        token=data[CONF_TOKEN],
        appid=data[CONF_APPID],
        userid=data[CONF_USERID],
        subject_id=data[CONF_SUBJECT_ID],
    )
    
    try:
        # Test API connection by trying to get device status
        await api.get_device_status()
    except PermissionError as err:
        _LOGGER.error("Invalid authentication: %s", err)
        raise InvalidAuth from err
    except ConnectionError as err:
        _LOGGER.error("Cannot connect to Aqara API: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise CannotConnect from err
    
    return {"title": f"Aqara Camera G3 ({data[CONF_SUBJECT_ID]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aqara Camera G3."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Set unique_id to prevent duplicate entries
            await self.async_set_unique_id(user_input[CONF_SUBJECT_ID])
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Aqara Camera G3."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options step for mapping faces to persons."""
        if user_input is not None:
            face_name_map = {k: v for k, v in user_input.items() if v}
            return self.async_create_entry(
                title="", data={CONF_FACE_NAME_MAP: face_name_map}
            )

        # Collect face list from coordinator
        face_list: dict[str, str] = {}
        data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if data and isinstance(data, dict):
            coordinator = data.get("coordinator")
            if coordinator:
                face_list = await coordinator.async_get_face_map()

        # Collect person entities
        persons = list(self.hass.states.async_all("person"))
        person_options = [
            {"value": state.entity_id, "label": state.name} for state in persons
        ]
        # Allow clearing mapping
        person_options.insert(0, {"value": "", "label": "None"})

        existing = self.config_entry.options.get(CONF_FACE_NAME_MAP, {})
        schema_dict: dict[vol.Optional, object] = {}
        # Build unique face names (one person may have multiple face IDs)
        face_names = sorted({name for name in face_list.values() if name})
        for face_name in face_names:
            schema_dict[
                vol.Optional(face_name, default=existing.get(face_name, ""))
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=person_options,
                    multiple=False,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"faces": ", ".join(face_list.values()) or "none"},
        )

