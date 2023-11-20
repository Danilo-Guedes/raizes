import os
import base64
import requests
from auth.bling import get_access_data, update_access_data


def refresh_access_data():
    API_URL = os.getenv("NEW_BLING_API_URL")
    CLIENT_ID = os.getenv("NEW_BLING_CLIENT_ID")
    SECRET_KEY = os.getenv("NEW_BLING_SECRET_KEY")

    access_data = get_access_data()

    credentials = f"{CLIENT_ID}:{SECRET_KEY}"
    credentials_in_base_64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "1.0",
        "Authorization": f"Basic {credentials_in_base_64}",
    }

    body = {
        "grant_type": "refresh_token",
        "refresh_token": access_data.get("refresh_token"),
    }

    # print(params)

    try:
        response = requests.post(f"{API_URL}/oauth/token", headers=headers, data=body)
        resp = response.json()

        print("o dict_res=>", resp)

        if "error" in resp:
            print("AQUI ESTA ENTRANDO SIMMMM")
            raise requests.HTTPError(resp.get("error").get("description"))
        if "access_token" in resp:
            update_access_data(resp)

    except Exception as Error:
        print(f"aqui deu ruim na chamada do auth() {Error}")
