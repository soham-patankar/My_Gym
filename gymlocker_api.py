import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")


def get_exercises(muscle):
    # Fail early with a clear message if .env didn't load
    if not API_URL or not API_KEY:
        raise ValueError("API_URL or API_KEY missing from .env file")

    response = requests.get(
        API_URL,
        params={"muscle": muscle},
        headers={"X-Api-Key": API_KEY},
        timeout=10,  # give up after 10 seconds instead of hanging
    )

    response.raise_for_status()

    return response.json()  # list of dicts