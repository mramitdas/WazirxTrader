from wazirx.rest.client import Client


class Base:
    def __init__(self, api_key=None, api_secret=None):
        """_summary_

        Args:
            api_key (str): wazirx api key
            api_secret (str): wazirx secret key
        Returns:
            self.client: obj instance
        """
        self.client = Client(api_key=api_key, secret_key=api_secret)

    def ping(self):
        """_summary_
        Test connectivity to the Rest API.

        Rate limit: 1 per second
        Args: NONE
        Returns:
            dict: {}
        """
        return self.client.send("ping")

    def server_time(self):
        """_summary_
        Fetch system status.

        Rate limit: 1 per second
        Args: NONE
        Returns:
            serverTime: long
        """
        return self.client.send("time")

    def system_status(self):
        """_summary_
        Test connectivity to the Rest API and get the current server time.

        Rate limit: 1 per second
        Args: NONE
        Returns:
            status: str
            message: str
        """
        return self.client.send("system_status")

    def exchange_info(self):
        """_summary_
        Fetch all exchange information

        Rate limit: 1 per second
        Args: NONE
        Returns:
            timezone: str
            serverTime: long
            symbols: list
        """
        return self.client.send("exchange_info")
