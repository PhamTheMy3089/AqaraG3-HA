"""API client for Aqara Camera G3."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.helpers.aiohttp_client import DEFAULT_TIMEOUT

from .const import API_BASE_URL, API_RESOURCE_QUERY

_LOGGER = logging.getLogger(__name__)


class AqaraG3API:
    """API client for Aqara Camera G3."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        aqara_url: str,
        token: str,
        appid: str,
        userid: str | None = None,
        subject_id: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._token = token
        self._appid = appid
        self._userid = userid
        self._subject_id = subject_id
        self._base_url = API_BASE_URL.format(url=aqara_url)

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request using Home Assistant's shared session."""
        url = f"{self._base_url}{endpoint}"
        
        # Build headers - Aqara API uses "Token" header (not Bearer)
        headers = {
            "Token": self._token,
            "Appid": self._appid,
            "Content-Type": "application/json; charset=utf-8",
            "Sys-Type": "1",
        }
        
        if self._userid:
            headers["Userid"] = self._userid

        try:
            async with self._session.request(
                method,
                url,
                json=data,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            ) as response:
                if response.status == 401 or response.status == 403:
                    error_text = await response.text()
                    _LOGGER.error("Authentication failed: %s", error_text)
                    raise PermissionError("Invalid authentication credentials") from None
                response.raise_for_status()
                return await response.json()
        except PermissionError:
            # Re-raise permission errors as-is
            raise
        except aiohttp.ClientConnectorError as err:
            _LOGGER.error("Connection error: %s", err)
            raise ConnectionError(f"Cannot connect to Aqara API: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error: %s", err)
            raise ConnectionError(f"Error communicating with Aqara API: {err}") from err

    async def get_device_status(self) -> dict[str, Any]:
        """Get device status."""
        payload = {
            "data": [
                {
                    "options": [
                        "ptz_cruise_enable",
                        "pets_track_enable",
                        "humans_track_enable",
                        "gesture_detect_enable",
                        "mdtrigger_enable",
                        "soundtrigger_enable",
                        "human_detect_enable",
                        "face_detect_enable",
                        "pets_detect_enable",
                        "set_video",
                        "sdcard_status",
                        "alarm_status",
                        "system_volume",
                        "alarm_bell_index",
                        "device_night_tip_light",
                        "cloud_small_video",
                        "alarm_bell_volume",
                        "device_wifi_rssi",
                        "gateway_deletion_setting",
                    ],
                    "subjectId": self._subject_id,
                }
            ]
        }
        
        response = await self._request("POST", API_RESOURCE_QUERY, data=payload)
        return response

