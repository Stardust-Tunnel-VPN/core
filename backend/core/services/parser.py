from requests import request


# TODO: make it async ?
class Parser:
    """
    Simple python class that parses data from a given URL.
    Originally created to parse vpngate.net data but can be used for any website.

    Attributes:
        url: str
            The URL to parse
    Methods:
        parseURL() -> str
            Parses the data from the given URL.
    """

    def __init__(self, url: str):
        self.url = url

    def parseURL(self) -> str:
        """
        Parses the data from the given URL.

        Returns:
            str: The parsed data
        """
        try:
            response = request("GET", self.url)
            return response.text
        except Exception as exc:
            print(f"An error occurred: {exc}")
