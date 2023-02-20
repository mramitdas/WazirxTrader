from datetime import datetime

from wazirx.rest.client import Client

from .exception import MissingAttributeError


class User:
    def __init__(self, api_key=None, api_secret=None):
        """_summary_

        Args:
            api_key (str): wazirx api key
            api_secret (str): wazirx secret key
        Returns:
            self.client: obj instance
        """
        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)

    def user_info(self):
        """_summary_

        Get current account information.

        Rate limit: 1 per second
        Query Parameters: None
        Returns:
            dict: {}
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("account_info",
                                {"timestamp": ts,
                                 "recvWindow": 5000})

    def user_funds(self):
        """_summary_

        Get fund details for current account.

        Rate limit: 1 per second
        Query Parameters: None
        Returns:
            list: [{}, {}]
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("funds_info",
                                {"timestamp": ts,
                                 "recvWindow": 5000})
