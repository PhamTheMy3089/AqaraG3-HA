"""Data update coordinator for Aqara Camera G3."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AqaraG3API
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class AqaraG3DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Aqara API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = AqaraG3API(
            aqara_url=config_entry.data["aqara_url"],
            token=config_entry.data["token"],
            appid=config_entry.data["appid"],
            userid=config_entry.data.get("userid"),
            subject_id=config_entry.data["subject_id"],
        )
        self.config_entry = config_entry

    async def _async_update_data(self) -> dict:
        """Fetch data from Aqara API."""
        try:
            data = await self.api.get_device_status()
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

