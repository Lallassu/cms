import requests
import logging
import time
from .const import LOGIN_URL, PROFILE_URL, SPA_URL_TEMPLATE

_LOGGER = logging.getLogger(__name__)

class ControlMySpaClient:
    def __init__(self, email, password):
        self.session = requests.Session()
        self.email = email
        self.password = password
        self.token = None
        self.refresh_token = None
        self.token_expiry = 0
        self.spa_id = None

    def login(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://controlmyspa.com",
            "Referer": "https://controlmyspa.com/",
            "User-Agent": "Mozilla/5.0" # Just to avoid getting banned or something :) 
        }
        payload = {"email": self.email, "password": self.password}
        response = self.session.post(LOGIN_URL, json=payload, headers=headers)

        response.raise_for_status()
        data = response.json().get("data", {})
        self.token = data.get("accessToken")
        self.refresh_token = data.get("refreshToken")
        self.token_expiry = time.time() + 3600  # Assume 1 hour expiry
        if not self.token:
            raise ValueError("Login succeeded but no access_token returned")

    def ensure_authenticated(self):
        if not self.token or time.time() >= self.token_expiry:
            self.login()
            self.get_profile()

    def get_profile(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0"
        }
    
        # Fetch user profile to extract spa ID
        response = self.session.get(PROFILE_URL, headers=headers)
        response.raise_for_status()
        
        # Extract spa ID from user profile
        profile_data = response.json().get("data", {})
        user_data = profile_data.get("user", {})
        self.spa_id = user_data.get("_id")
        
        if not self.spa_id:
            raise ValueError("Spa ID could not be extracted from profile response")
    
    
    def fetch_spa_data(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"https://iot.controlmyspa.com/portal/spas/{self.spa_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        }
        url = SPA_URL_TEMPLATE.format(self.spa_id)
        response = self.session.get(url, headers=headers)

        # If we get an empty response, try to get the correct spa ID from spa list
        if response.status_code == 200 and not response.text.strip():
            spa_list_response = self.session.get("https://iot.controlmyspa.com/spas", headers=headers)
            
            if spa_list_response.status_code == 200 and spa_list_response.text.strip():
                spa_list_data = spa_list_response.json()
                spas = spa_list_data.get("data", {}).get("spas", [])
                if spas:
                    actual_spa_id = spas[0].get("_id")
                    if actual_spa_id:
                        self.spa_id = actual_spa_id
                        # Return the spa data directly from the spa list response
                        return spas[0]

        response.raise_for_status()
        return response.json()
