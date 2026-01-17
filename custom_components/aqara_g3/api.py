"""API client for Aqara Camera G3."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import (
    API_BASE_URL,
    API_FACE_INFO,
    API_HISTORY_LOG,
    API_RESOURCE_QUERY,
    API_RESOURCE_WRITE,
)

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
                timeout=aiohttp.ClientTimeout(total=10),
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

    async def set_video(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable video."""
        if not self._subject_id:
            raise ValueError("subject_id is required to set video state")

        payload = {
            "data": {"set_video": 1 if enabled else 0},
            "subjectId": self._subject_id,
        }

        response = await self._request("POST", API_RESOURCE_WRITE, data=payload)
        return response

    async def get_face_info(self) -> dict[str, Any]:
        """Get face info list."""
        if not self._subject_id:
            raise ValueError("subject_id is required to get face info")

        endpoint = f"{API_FACE_INFO}?did={self._subject_id}"
        response = await self._request("GET", endpoint)
        return response

    async def get_last_face_event(self) -> dict[str, Any]:
        """Get the latest face detection event."""
        if not self._subject_id:
            raise ValueError("subject_id is required to get history log")

        payload = {
            "resourceIds": ["13.95.85"],
            "scanId": "",
            "size": "1",
            "startTime": 1514736000000,
            "subjectId": self._subject_id,
        }
        response = await self._request("POST", API_HISTORY_LOG, data=payload)
        return response
