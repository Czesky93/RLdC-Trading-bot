
import requests

class BinanceService:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.binance.com/api/v3/"

    def test_connection(self):
        response = requests.get(f"{self.base_url}ping")
        return response.status_code == 200
