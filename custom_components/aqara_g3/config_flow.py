"""Config flow for Aqara Camera G3 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .auth import AqaraAccountClient
from .const import (
    AQARA_AREA_MAP,
    CONF_AQARA_URL,
    CONF_APPID,
    CONF_AREA,
    CONF_FACE_NAME_MAP,
    CONF_PASSWORD,
    CONF_SUBJECT_ID,
    CONF_TOKEN,
    CONF_USERID,
    CONF_USERNAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

AREA_OPTIONS = [
    {"value": key, "label": key} for key in AQARA_AREA_MAP.keys()
]

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_AREA, default="CN"): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=AREA_OPTIONS,
                multiple=False,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    client = AqaraAccountClient(session=session, area=data[CONF_AREA])

    try:
        credentials = await client.async_login(
            data[CONF_USERNAME], data[CONF_PASSWORD]
        )
        devices = await client.async_get_devices()
    except PermissionError as err:
        _LOGGER.error("Invalid authentication: %s", err)
        raise InvalidAuth from err
    except ConnectionError as err:
        _LOGGER.error("Cannot connect to Aqara API: %s", err)
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.error("Unexpected error: %s", err)
        raise CannotConnect from err

    return {"credentials": credentials, "devices": devices}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aqara Camera G3."""

    VERSION = 1
    _login_data: dict[str, Any] | None = None
    _devices: list[dict[str, Any]] | None = None

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
            self._login_data = info["credentials"]
            self._devices = info["devices"]
            return await self.async_step_device()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection step."""
        if not self._login_data:
            return await self.async_step_user()

        errors: dict[str, str] = {}
        if user_input is not None:
            subject_id = user_input[CONF_SUBJECT_ID]
            entry_data = {
                CONF_AQARA_URL: self._login_data[CONF_AQARA_URL],
                CONF_TOKEN: self._login_data[CONF_TOKEN],
                CONF_APPID: self._login_data[CONF_APPID],
                CONF_USERID: self._login_data[CONF_USERID],
                CONF_SUBJECT_ID: subject_id,
            }
            await self.async_set_unique_id(subject_id)
            self._abort_if_unique_id_configured()
            title = f"Aqara Camera G3 ({subject_id})"
            return self.async_create_entry(title=title, data=entry_data)

        schema = self._build_device_schema(errors)
        return self.async_show_form(
            step_id="device",
            data_schema=schema,
            errors=errors,
        )

    def _build_device_schema(self, errors: dict[str, str]) -> vol.Schema:
        """Build device selection schema from fetched list."""
        devices = self._devices or []
        options: list[dict[str, str]] = []
        for item in devices:
            if not isinstance(item, dict):
                continue
            device_id = (
                item.get("subjectId")
                or item.get("deviceId")
                or item.get("did")
                or item.get("devId")
                or item.get("id")
            )
            if not device_id:
                continue
            name = (
                item.get("name")
                or item.get("deviceName")
                or item.get("positionName")
                or item.get("model")
            )
            label = f"{name} ({device_id})" if name else str(device_id)
            options.append({"value": str(device_id), "label": label})

        if not options:
            errors["base"] = "no_devices"
            return vol.Schema({vol.Required(CONF_SUBJECT_ID): str})

        return vol.Schema(
            {
                vol.Required(CONF_SUBJECT_ID): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        multiple=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
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
        self._config_entry = config_entry

    async def _get_face_list(self) -> dict[str, str]:
        """Fetch current face list from coordinator."""
        face_list: dict[str, str] = {}
        data = self.hass.data.get(DOMAIN, {}).get(self._config_entry.entry_id)
        if data and isinstance(data, dict):
            coordinator = data.get("coordinator")
            if coordinator:
                face_list = await coordinator.async_get_face_map()
        return face_list

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
        face_list = await self._get_face_list()

        # Collect person entities
        persons = list(self.hass.states.async_all("person"))
        person_options = [
            {"value": state.entity_id, "label": state.name} for state in persons
        ]
        # Allow clearing mapping
        person_options.insert(0, {"value": "", "label": "None"})

        existing = self._config_entry.options.get(CONF_FACE_NAME_MAP, {})
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
