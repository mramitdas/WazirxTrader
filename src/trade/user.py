from wazirx.rest.client import Client
from datetime import datetime


class User:
    def __init__(self, api_key=None, api_secret=None):
        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.ct = datetime.now().timestamp()
        self.ts = int(self.ct*1000)

    def user_info(self):
        return self.client.send("account_info",
                                {"timestamp": self.ts,
                                 "recvWindow": 5000})

    def user_funds(self):
        return self.client.send("funds_info",
                                {"timestamp": self.ts,
                                 "recvWindow": 5000})
