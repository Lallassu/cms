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
        #_LOGGER.debug(f"Sending login request with email: {self.email}")
        response = self.session.post(LOGIN_URL, json=payload, headers=headers)
        #_LOGGER.debug(f"Login response code: {response.status_code}")
        #_LOGGER.debug(f"Login response body: {response.text}")

        response.raise_for_status()
        data = response.json().get("data", {})
        self.token = data.get("accessToken")
        self.refresh_token = data.get("refreshToken")
        self.token_expiry = time.time() + 3600  # Assume 1 hour expiry
        if not self.token:
            raise ValueError("Login succeeded but no access_token returned")

    def ensure_authenticated(self):
        if not self.token or time.time() >= self.token_expiry:
            _LOGGER.debug("Access token expired or missing, re-authenticating")
            self.login()
            self.get_profile()

    def get_profile(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0"
        }
    
        # Optional profile request (logging only)
        #_LOGGER.debug("Fetching user profile")
        response = self.session.get(PROFILE_URL, headers=headers)
        #_LOGGER.debug(f"Profile response code: {response.status_code}")
        #_LOGGER.debug(f"Profile response body: {response.text}")
        response.raise_for_status()
    
        # Required spa ID fetch
        #_LOGGER.debug("Fetching spa list to extract spa ID")
        spa_response = self.session.get("https://iot.controlmyspa.com/spas", headers=headers)
        #_LOGGER.debug(f"Spas response code: {spa_response.status_code}")
        #_LOGGER.debug(f"Spas response body: {spa_response.text}")
        spa_response.raise_for_status()
    
        spas = spa_response.json().get("_embedded", {}).get("spas", [])
        if not spas:
            raise ValueError("No spas found in account")
    
        self.spa_id = spas[0].get("_id")
        if not self.spa_id:
            raise ValueError("Spa ID could not be extracted from response")
    
        _LOGGER.debug(f"Extracted spa ID: {self.spa_id}")
    
    
    def fetch_spa_data(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0"
        }
        url = SPA_URL_TEMPLATE.format(self.spa_id)
        #_LOGGER.debug(f"Fetching spa data from {url}")
        response = self.session.get(url, headers=headers)
        #_LOGGER.debug(f"Spa data response code: {response.status_code}")
        #_LOGGER.debug(f"Spa data response body: {response.text}")

        response.raise_for_status()
        return response.json()
