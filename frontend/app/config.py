import os

import requests
from decouple import config

SESSION = requests.Session()
BACKEND_URL = config("BACKEND_URL", default="http://reqcheck-web-1:8000")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def get_csrf_token():
    try:
        url = f"{BACKEND_URL}/csrf-token/"
        response = SESSION.get(url, timeout=5)
        response.raise_for_status()
        return SESSION.cookies.get("csrftoken")
    except requests.RequestException as e:
        print(f"[CSRF ERROR] Could not get CSRF token: {e}")
        return None


def get_header(content_type="application/json"):
    csrf_token = get_csrf_token()
    if not csrf_token:
        print("[HEADER WARNING] CSRF token is missing.")
        return {}, SESSION

    headers = {
        "X-CSRFToken": csrf_token,
    }
    if content_type:
        headers["Content-Type"] = content_type

    return headers, SESSION
