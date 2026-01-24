"""Constants for the Aqara Camera G3 integration."""
from __future__ import annotations

DOMAIN = "aqara_g3"

# Configuration keys
CONF_AQARA_URL = "aqara_url"
CONF_TOKEN = "token"
CONF_APPID = "appid"
CONF_USERID = "userid"
CONF_SUBJECT_ID = "subject_id"
CONF_FACE_MAP = "face_map"
CONF_FACE_NAME_MAP = "face_name_map"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_AREA = "area"

SERVICE_REFRESH_FACE_LIST = "refresh_face_list"

# API endpoints
API_BASE_URL = "https://{url}/app/v1.0"
API_RESOURCE_QUERY = "/lumi/res/query"
API_RESOURCE_WRITE = "/lumi/res/write"
API_CAMERA_OPERATE = "/lumi/devex/camera/operate"
API_VIEW_DATA_QUERY = "/lumi/app/view/data/query"
API_FACE_INFO = "/lumi/devex/face/info"
API_HISTORY_LOG = "/lumi/res/history/log"

# Default values
DEFAULT_AQARA_URL = "open-cn.aqara.com"

# Aqara account regions (for token auto-fetch)
AQARA_AREA_MAP: dict[str, dict[str, str]] = {
    "CN": {
        "server": "https://aiot-rpc.aqara.cn",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "EU": {
        "server": "https://rpc-ger.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "RU": {
        "server": "https://rpc-ru.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "KR": {
        "server": "https://rpc-kr.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "JP": {
        "server": "https://rpc-kr.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "AF": {
        "server": "https://rpc-ger.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "US": {
        "server": "https://aiot-rpc-usa.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "SG": {
        "server": "https://sgp-aiot-api.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "HMT": {
        "server": "https://aiot-rpc-usa.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "AU": {
        "server": "https://rpc-au.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "ME": {
        "server": "https://rpc-au.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
    "OTHER": {
        "server": "https://aiot-rpc-usa.aqara.com",
        "appid": "444c476ef7135e53330f46e7",
        "appkey": "NULL",
    },
}
