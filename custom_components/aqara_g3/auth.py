"""Account auth helper for Aqara Cloud."""
from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
import urllib.parse
from typing import Any

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .const import AQARA_AREA_MAP

_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCG46slB57013JJs4Vvj5cVyMpR
9b+B2F+YJU6qhBEYbiEmIdWpFPpOuBikDs2FcPS19MiWq1IrmxJtkICGurqImRUt
4lP688IWlEmqHfSxSRf2+aH0cH8VWZ2OaZn5DWSIHIPBF2kxM71q8stmoYiV0oZs
rZzBHsMuBwA4LQdxBwIDAQAB
-----END PUBLIC KEY-----"""


class AqaraAccountClient:
    """Client to authenticate with Aqara account and fetch devices."""

    def __init__(self, session: aiohttp.ClientSession, area: str) -> None:
        """Initialize client."""
        area_key = (area or "").upper()
        if area_key not in AQARA_AREA_MAP:
            area_key = "OTHER"
        area_cfg = AQARA_AREA_MAP[area_key]

        self._session = session
        self._area = area_key
        self._server = area_cfg["server"]
        self._appid = area_cfg["appid"]
        self._appkey = area_cfg["appkey"]
        self._token: str | None = None
        self._userid: str | None = None

    @property
    def appid(self) -> str:
        """Return appid."""
        return self._appid

    @property
    def aqara_url(self) -> str:
        """Return aqara domain without scheme."""
        return (
            self._server.replace("https://", "").replace("http://", "").strip("/")
        )

    async def async_login(self, username: str, password: str) -> dict[str, str]:
        """Login using account credentials."""
        payload = {
            "account": username,
            "encryptType": 2,
            "password": self._encrypt_password(password),
        }
        payload_str = json.dumps(payload or {}, separators=(",", ":"), ensure_ascii=False)
        headers = self._build_headers(payload_str)
        headers.setdefault("Content-Type", "application/json")
        url = f"{self._server}/app/v1.0/lumi/user/login"

        try:
            async with self._session.request(
                "POST",
                url,
                data=payload_str,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                response_text = await response.text()

                if response.status in (401, 403):
                    error_data = {}
                    try:
                        error_data = json.loads(response_text)
                    except:
                        pass
                    error_msg = error_data.get("message", "Invalid authentication credentials")
                    raise PermissionError(
                        f"Authentication failed: {error_msg} (code: {error_data.get('code', 'N/A')})"
                    )

                if response.status >= 400:
                    error_data = {}
                    try:
                        error_data = json.loads(response_text)
                        error_msg = error_data.get("message", f"HTTP {response.status}")
                        error_code = error_data.get("code", "N/A")
                        raise ConnectionError(
                            f"API error: {error_msg} (code: {error_code}, HTTP: {response.status})"
                        )
                    except:
                        raise ConnectionError(f"HTTP {response.status} error: {response_text}")

                response.raise_for_status()
                data = await response.json()

                if not isinstance(data, dict):
                    raise PermissionError(f"Invalid response format: {response_text}")

                if data.get("code") != 0:
                    error_msg = data.get("message", "Unknown error")
                    error_code = data.get("code", "N/A")
                    raise PermissionError(f"Login failed: {error_msg} (code: {error_code})")

                result = data.get("result") or {}
                token = result.get("token")
                userid = result.get("userId")
                if not token or not userid:
                    raise PermissionError("Invalid response: missing token or userId")

                self._token = str(token)
                self._userid = str(userid)

                return {
                    "token": self._token,
                    "userid": self._userid,
                    "appid": self._appid,
                    "aqara_url": self.aqara_url,
                }
        except PermissionError:
            raise
        except ConnectionError:
            raise
        except aiohttp.ClientConnectorError as err:
            raise ConnectionError(f"Network error: {err}") from err
        except aiohttp.ClientError as err:
            raise ConnectionError(f"Network error: {err}") from err
        except Exception as err:
            raise ConnectionError(f"Unexpected error during login: {err}") from err

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Fetch device list for the account."""
        response = await self._request(
            "GET", "/lumi/app/position/device/query", params={}
        )
        return self._extract_device_list(response)

    def _encrypt_password(self, password: str) -> str:
        """Encrypt password using Aqara public key."""
        md5_hex = hashlib.md5(password.encode()).hexdigest().encode()
        public_key = serialization.load_pem_public_key(_PUBLIC_KEY.encode())
        encrypted = public_key.encrypt(md5_hex, padding.PKCS1v15())
        return base64.b64encode(encrypted).decode()

    def _build_headers(self, payload_str: str) -> dict[str, str]:
        """Build Aqara headers including sign."""
        headers = {
            "Area": self._area,
            "Appid": self._appid,
            "Appkey": self._appkey,
            "Nonce": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            "Time": str(round(time.time() * 1000)),
            "RequestBody": payload_str,
            "Sys-Type": "1",
            "Lang": "en",
            "Phone-Model": "pyAqara",
            "PhoneId": str(uuid.uuid4()).upper(),
            "App-Version": "3.0.0",
            "User-Agent": "pyAqara/1.0.0",
        }
        if self._token:
            headers["Token"] = self._token

        sign = self._sign_header(headers)
        del headers["Appkey"]
        del headers["RequestBody"]
        headers["Sign"] = sign
        return headers

    def _sign_header(self, headers: dict[str, str]) -> str:
        """Sign header using Aqara algorithm."""
        if headers.get("Token"):
            sign_source = (
                "Appid={Appid}&Nonce={Nonce}&Time={Time}&Token={Token}&"
                "{RequestBody}&{Appkey}"
            ).format(**headers)
        else:
            sign_source = (
                "Appid={Appid}&Nonce={Nonce}&Time={Time}&{RequestBody}&{Appkey}"
            ).format(**headers)
        return hashlib.md5(sign_source.encode()).hexdigest()

    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an Aqara request using account auth."""
        if method.upper() == "GET":
            payload_str = urllib.parse.urlencode(params or {})
        else:
            payload_str = json.dumps(payload or {}, separators=(",", ":"), ensure_ascii=False)

        headers = self._build_headers(payload_str)
        if method.upper() != "GET":
            headers.setdefault("Content-Type", "application/json")
        url = f"{self._server}/app/v1.0{endpoint}"

        try:
            async with self._session.request(
                method,
                url,
                params=params if method.upper() == "GET" else None,
                data=None if method.upper() == "GET" else payload_str,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status in (401, 403):
                    raise PermissionError("Invalid authentication credentials")
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientConnectorError as err:
            raise ConnectionError(f"Cannot connect to Aqara API: {err}") from err
        except aiohttp.ClientError as err:
            raise ConnectionError(f"Error communicating with Aqara API: {err}") from err

    @staticmethod
    def _extract_device_list(data: dict | None) -> list[dict[str, Any]]:
        """Extract device list from response."""
        if not isinstance(data, dict):
            return []
        result = data.get("result")
        if isinstance(result, dict):
            for key in ("data", "list", "deviceList", "devices"):
                value = result.get(key)
                if isinstance(value, list):
                    return value
        if isinstance(result, list):
            return result
        for key in ("data", "list", "deviceList", "devices"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return []
