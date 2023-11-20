import os
import base64
import requests
from datetime import datetime
from auth.bling import get_access_data, update_access_data

from colorama import Fore, init


def get_sales_by_date(date_string: str):
    try:
        endpoint = os.getenv("BLING_SALES_BY_DATE_API_URL")

        date = datetime.strptime(date_string, "%d/%m/%Y")

        formated_date = date.strftime("%Y-%m-%d")

        params = {
            "dataInicial": formated_date,
            "dataFinal": formated_date,
        }
        access_data = get_access_data()

        headers = {"Authorization": f"Bearer {access_data.get('access_token')}"}

        resp = requests.get(endpoint, params=params, headers=headers)

        dict_res = resp.json()
        # print("o dict_res=>", dict_res)

        if "error" in dict_res:
            print(
                Fore.RED + "Um Erro foi identificado ao requisitar os dados de vendas"
            )
            if resp.status_code == 401:
                print(Fore.YELLOW + "Acess Token Expirado, gerando um novo....")
                refresh_access_data()
                # call_bling_api(date_string)
                print("AQUI PRECISA CHAMAR RECURSIVAMENTE TALVEZ?/n/n/n/")

            else:
                raise requests.HTTPError(dict_res.get("error").get("description"))

        api_return = dict_res.get(
            "data",
        )
        return api_return
    except Exception as err:
        print(Fore.RED + f"OPA!!, ALGUM ERRO OCORREU em get_sales_by_date=> {err}")


def get_sale_by_id(sale_id: str):
    try:
        endpoint = os.getenv("BLING_SALES_BY_DATE_API_URL")
        access_data = get_access_data()

        headers = {"Authorization": f"Bearer {access_data.get('access_token')}"}

        resp = requests.get(endpoint + f"/{sale_id}", headers=headers)

        dict_res = resp.json()
        # print("o dict_res do detalhe=>", dict_res)

        if "error" in dict_res:
            print(
                Fore.RED
                + "Um Erro foi identificado ao requisitar os dados da venda po ID"
            )
            raise requests.HTTPError(dict_res.get("error").get("description"))

        api_return = dict_res.get(
            "data",
        )

        return api_return
    except Exception as err:
        print(Fore.RED + f"OPA!!, ALGUM ERRO OCORREU em get_sales_by_date=> {err}")


def refresh_access_data():
    API_URL = os.getenv("BLING_API_URL")
    CLIENT_ID = os.getenv("BLING_CLIENT_ID")
    SECRET_KEY = os.getenv("BLING_SECRET_KEY")

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
