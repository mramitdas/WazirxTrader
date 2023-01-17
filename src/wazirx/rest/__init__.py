from .client import Client
import sys

version = sys.version_info
if version[0] < 3 and version[1] < 7:
    raise BaseException("Python>=3.7 required")
