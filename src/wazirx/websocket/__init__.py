from .websocket_client import WebsocketClient
import sys

version = sys.version_info
if version[0] < 3 and version[1] < 7:
    raise BaseException("Python>=3.7 required")
