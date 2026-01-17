"""Data update coordinator for Aqara Camera G3."""
from __future__ import annotations

import logging
from datetime import timedelta
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AqaraG3API
from .const import CONF_FACE_MAP, CONF_FACE_NAME_MAP, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
FACE_INFO_REFRESH_INTERVAL = timedelta(hours=12)


class AqaraG3DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Aqara API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Aqara G3 Data",
            update_interval=SCAN_INTERVAL,
        )
        session = async_get_clientsession(hass)
        self.api = AqaraG3API(
            session=session,
            aqara_url=config_entry.data["aqara_url"],
            token=config_entry.data["token"],
            appid=config_entry.data["appid"],
            userid=config_entry.data.get("userid"),
            subject_id=config_entry.data["subject_id"],
        )
        self.config_entry = config_entry
        self._logged_first_response = False
        self._face_map: dict[str, str] = {}
        self._last_face_info_fetch: float | None = None
        self._logged_face_event_empty = False

    async def _async_update_data(self) -> dict:
        """Fetch data from Aqara API."""
        try:
            data = await self.api.get_device_status()
            attrs = self._extract_attr_map(data)
            last_face_id = None
            last_face_name = None

            # Enrich with face list (refresh every 12h) + last face event
            await self._maybe_refresh_face_map()

            try:
                face_event = await self.api.get_last_face_event()
                last_face_id = self._extract_last_face_id(face_event)
                if last_face_id and self._face_map:
                    last_face_name = self._face_map.get(last_face_id)
                if last_face_id is None and not self._logged_face_event_empty:
                    _LOGGER.warning("Aqara G3 FACE EVENT EMPTY: %s", face_event)
                    self._logged_face_event_empty = True
            except Exception as err:
                _LOGGER.debug("Failed to fetch face history: %s", err)

            if last_face_id:
                attrs["last_face_id"] = last_face_id
            if last_face_name:
                attrs["last_face_name"] = last_face_name
            # Map face id to HA person if configured
            # Prefer mapping by face name, fallback to face id
            face_name_map = self.config_entry.options.get(CONF_FACE_NAME_MAP, {})
            face_id_map = self.config_entry.options.get(CONF_FACE_MAP, {})
            person_entity_id = None
            if last_face_name and face_name_map:
                person_entity_id = face_name_map.get(str(last_face_name))
            if not person_entity_id and last_face_id and face_id_map:
                person_entity_id = face_id_map.get(str(last_face_id))
            if person_entity_id:
                state = self.hass.states.get(person_entity_id)
                attrs["last_face_person"] = (
                    state.name if state and state.name else person_entity_id
                )
            if not self._logged_first_response:
                self._logged_first_response = True
                result = data.get("result") if isinstance(data, dict) else None
                result_list = []
                if isinstance(result, list):
                    result_list = result
                elif isinstance(result, dict):
                    result_list = result.get("resultList", []) or []
                _LOGGER.debug(
                    "Aqara G3 response shape: type=%s, keys=%s, result_type=%s, result_len=%s",
                    type(data).__name__,
                    list(data.keys()) if isinstance(data, dict) else None,
                    type(result).__name__ if result is not None else None,
                    len(result_list) if isinstance(result_list, list) else None,
                )
                _LOGGER.debug(
                    "Aqara G3 normalized attrs: count=%s, keys=%s",
                    len(attrs),
                    list(attrs.keys()) if attrs else None,
                )
            return attrs
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _maybe_refresh_face_map(self) -> None:
        """Refresh face map at startup or every 12 hours."""
        now = time.monotonic()
        if (
            self._last_face_info_fetch is not None
            and now - self._last_face_info_fetch < FACE_INFO_REFRESH_INTERVAL.total_seconds()
        ):
            return

        try:
            face_info = await self.api.get_face_info()
            self._face_map = self._extract_face_map(face_info)
            self._last_face_info_fetch = now
        except Exception as err:
            _LOGGER.debug("Failed to refresh face info: %s", err)

    async def async_get_face_map(self, force_refresh: bool = False) -> dict[str, str]:
        """Return face map, optionally forcing refresh."""
        if force_refresh:
            self._last_face_info_fetch = None
        await self._maybe_refresh_face_map()
        return dict(self._face_map)

    @staticmethod
    def _extract_attr_map(data: dict | None) -> dict:
        """Normalize API response into a flat attr->value dict."""
        if not isinstance(data, dict):
            return {}

        result = data.get("result")
        attrs: dict[str, object] = {}

        # Case 1: result is a list of {attr, value}
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and "attr" in item:
                    attrs[item["attr"]] = item.get("value")
            return attrs

        # Case 2: result is a dict with resultList
        if isinstance(result, dict):
            result_list = result.get("resultList")
            if isinstance(result_list, list) and result_list:
                # If result_list[0] is a dict of keys -> {value}
                first = result_list[0]
                if isinstance(first, dict) and "attr" not in first:
                    for key, value in first.items():
                        if isinstance(value, dict) and "value" in value:
                            attrs[key] = value.get("value")
                        else:
                            attrs[key] = value
                    return attrs

                # Otherwise treat as list of {attr, value}
                for item in result_list:
                    if isinstance(item, dict) and "attr" in item:
                        attrs[item["attr"]] = item.get("value")
                return attrs

            # If result itself is a map of key -> {value}
            for key, value in result.items():
                if isinstance(value, dict) and "value" in value:
                    attrs[key] = value.get("value")
                else:
                    attrs[key] = value
            return attrs

        # Case 3: fallback to top-level resultList
        result_list = data.get("resultList")
        if isinstance(result_list, list):
            for item in result_list:
                if isinstance(item, dict) and "attr" in item:
                    attrs[item["attr"]] = item.get("value")
        return attrs

    @staticmethod
    def _extract_face_map(data: dict | None) -> dict[str, str]:
        """Extract face id -> name map from face info response."""
        if not isinstance(data, dict):
            return {}

        result = data.get("result")
        if isinstance(result, dict):
            face_list = result.get("faceList") or result.get("list") or []
        elif isinstance(result, list):
            face_list = result
        else:
            face_list = data.get("faceList") or data.get("list") or []

        face_map: dict[str, str] = {}
        if isinstance(face_list, list):
            for item in face_list:
                if not isinstance(item, dict):
                    continue
                face_id = item.get("faceId") or item.get("id")
                face_id_str = item.get("faceIdStr")
                name = item.get("name") or item.get("faceName")
                if name:
                    if face_id:
                        face_map[str(face_id)] = str(name)
                    if face_id_str:
                        face_map[str(face_id_str)] = str(name)
        return face_map

    @staticmethod
    def _extract_last_face_id(data: dict | None) -> str | None:
        """Extract the last face id from history log response."""
        if not isinstance(data, dict):
            return None

        result = data.get("result")
        if isinstance(result, dict):
            history_list = (
                result.get("data")
                or result.get("history")
                or result.get("list")
                or result.get("resultList")
                or []
            )
        elif isinstance(result, list):
            history_list = result
        else:
            history_list = data.get("history") or data.get("list") or []

        if isinstance(history_list, list) and history_list:
            item = history_list[0]
            if isinstance(item, dict):
                return (
                    item.get("faceId")
                    or item.get("faceIdStr")
                    or item.get("value")
                    or item.get("data")
                    or item.get("attrValue")
                )
        return None
