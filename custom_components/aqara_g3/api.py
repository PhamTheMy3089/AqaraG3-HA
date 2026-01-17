"""API client for Aqara Camera G3."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_RESOURCE_QUERY

_LOGGER = logging.getLogger(__name__)


class AqaraG3API:
    """API client for Aqara Camera G3."""

    def __init__(
        self,
        aqara_url: str,
        token: str,
        appid: str,
        userid: str | None = None,
        subject_id: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._aqara_url = aqara_url
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
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        url = f"{self._base_url}{endpoint}"
        
        default_headers = {
            "Token": self._token,
            "Appid": self._appid,
            "Content-Type": "application/json; charset=utf-8",
            "Sys-Type": "1",
        }
        
        if self._userid:
            default_headers["Userid"] = self._userid
        
        if headers:
            default_headers.update(headers)

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, json=data, headers=default_headers
            ) as response:
                response.raise_for_status()
                return await response.json()

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

