"""Constants for the Aqara Camera G3 integration."""
from __future__ import annotations

DOMAIN = "aqara_g3"

# Configuration keys
CONF_AQARA_URL = "aqara_url"
CONF_TOKEN = "token"
CONF_APPID = "appid"
CONF_USERID = "userid"
CONF_SUBJECT_ID = "subject_id"

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

