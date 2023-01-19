from wazirx.rest.client import Client


class Base:
    def __init__(self, api_key=None, api_secret=None):
        self.client = Client(api_key=api_key, secret_key=api_secret)

    def ping(self):
        return self.client.send("ping")

    def server_time(self):
        return self.client.send("time")

    def system_status(self):
        return self.client.send("system_status")

    def exchange_info(self):
        return self.client.send("exchange_info")
