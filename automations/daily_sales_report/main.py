import json
import os
import locale
import base64

import requests
import pyperclip
from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
from tabulate import tabulate
from pathlib import Path
from datetime import datetime
from classes import DailyInfo
from appdirs import user_config_dir
from colorama import Fore, init


def main():
    init(autoreset=True)

    search_date_str = input("Qual data deseja pesquisar?  : ")

    orders = call_bling_api(search_date_str)

    products_list = api_response_to_list(orders, search_date_str)

    clean_df = generate_clean_df(products_list)

    info = prepare_relevant_info(clean_df)

    send_whatsapp_msg(info, search_date_str)


def call_bling_api(date_string):
    endpoint = os.getenv("BLING_ORDERS_ENDPOINT")
    api_key = os.getenv("BLING_API_KEY")
    search_date_param = f"dataEmissao[{date_string} TO {date_string}]"

    print("date_string", date_string)

    date = datetime.strptime(date_string, '%d/%m/%Y')

    formated_date = date.strftime("%Y-%m-%d")

    params = {
        "dataInicial": formated_date,
        "dataFinal": formated_date,
    }
    try:
        access_token, refresh_token = get_access_token()

        headers = {"Authorization": f"Bearer {access_token}"}
        req = requests.get(endpoint, params=params, headers=headers)

        print("Request URL:", req.request.url)
        print("Request Headers:", req.request.headers)
        print("Request Method:", req.request.method)
        print("Request Body:", req.request.body)
        print("Response Status Code:", req.status_code)
        # print("Response Content:", req.text)
        # print("a req=>", req)

        dict_res = req.json()
        print("o dict_res=>", dict_res)

        if "error" in dict_res:
            print("AQUI ESTA ENTRANDO SIMMMM")
            raise requests.HTTPError(dict_res.get("error").get("description"))

        api_return = dict_res.get(
            "retorno",
        )

        # print("o retorno =>", dict_res)

        if api_return.get("erros") is not None:
            api_errors = api_return.get("erros")

            if type(api_errors) == list:
                raise requests.HTTPError(api_errors[0]["erro"]["msg"])
            else:
                raise requests.HTTPError(api_errors["erro"]["msg"])

        else:
            print("Api do Blig retornou com sucesso!")
            orders = api_return.get("pedidos")

            if orders is not None:
                return orders

    except Exception as err:
        print(Fore.RED + f"OPA!!, ALGUM ERRO OCORREU => {err}")


def api_response_to_list(raw_orders, searched_date):
    """
    tranform the api response into a list while treat discount values
    """

    list_of_products = []

    for order in raw_orders:
        # print(f"a ORDERMMMMMM ==> {order}\n\n\n\n")
        if order["pedido"]["desconto"] != "0,00":  # verificando se tem desconto
            # print("aqui teve desconto", order["pedido"]["desconto"])

            discount_in_cash = float(order["pedido"]["totalprodutos"]) - float(
                order["pedido"]["totalvenda"]
            )

            # print("discount_in_cash", discount_in_cash)
            for order_itens in order["pedido"][
                "itens"
            ]:  # initializing every discout as 0.00
                order_itens["item"]["desconto"] = "0.00"

            for order_itens in order["pedido"]["itens"]:
                # print("no forr =>>", order_itens)
                final_item_value = float(order_itens["item"]["quantidade"]) * float(
                    order_itens["item"]["valorunidade"]
                )

                if final_item_value > discount_in_cash:
                    order_itens["item"]["desconto"] = discount_in_cash
                    break

        else:  # zerar valor de desconto mesmo qdo o pedido-desconto é 0 mas vem uns valores estranhos de desconto no item
            for order_itens in order["pedido"]["itens"]:
                order_itens["item"]["desconto"] = "0.00"

        for product in order["pedido"]["itens"]:
            # if product["item"]["desconto"] != "0.00":
            #     print("aqui deu ruim", product)

            list_of_products.append(product["item"])

    print("Dado Tratado com Sucesso e enviado pra o Pandas fazer sua mágica....")

    return list_of_products


def generate_clean_df(prod_list):
    df = pd.DataFrame(prod_list)

    df = df.drop(
        columns=[
            "un",
            "codigo",
            "precocusto",
            "descontoItem",
            "pesoBruto",
            "largura",
            "altura",
            "profundidade",
            "descricaoDetalhada",
            "unidadeMedida",
            "gtin",
        ]
    )

    df["quantidade"] = df["quantidade"].astype("float64")
    df["valorunidade"] = df["valorunidade"].astype("float64")
    df["desconto"] = df["desconto"].astype("float64")
    df["total"] = (df["valorunidade"] * df["quantidade"]) - df["desconto"]

    # GROUPING ROWS WITH THE SAME CODE
    agg_options = {
        "quantidade": "sum",
        "valorunidade": "last",
        "descricao": "last",
        "desconto": "sum",
        "total": "sum",
    }

    df = df.groupby(by="descricao", as_index=False).aggregate(agg_options)

    df.to_csv(f"{Path.cwd()}/excel/api.csv", sep=";", decimal=",")

    print("### Arquivo Gerado com Sucesso! ###")

    return df


def prepare_relevant_info(dataframe):
    df_by_value = dataframe.sort_values(by=["total"], ascending=False)

    total_sales = round(dataframe["total"].sum(), 2)

    top_seven_by_value = df_by_value.head(7)[["quantidade", "total", "descricao"]]

    ##handle R$ locale currency
    top_seven_by_value = top_seven_by_value.assign(
        total=top_seven_by_value["total"].map(
            lambda x: locale.currency(x, grouping=True)
        )
    )

    produtcs_to_count_as_client = dataframe[
        dataframe["descricao"].str.contains("*", regex=False)
    ]

    in_place_delivery = dataframe[dataframe["descricao"].str.startswith("(Viagem")]

    third_party_delivery = dataframe[
        dataframe["descricao"].str.contains("Delivery", regex=False)
        & dataframe["descricao"].str.contains("*", regex=False)
    ]

    number_of_clients_in_bling = (
        produtcs_to_count_as_client["quantidade"].sum().astype("int")
    )

    number_of_in_place_delivery = in_place_delivery["quantidade"].sum().astype("int")

    number_of_third_party_delivery = (
        third_party_delivery["quantidade"].sum().astype("int")
    )

    number_of_in_place_meals = (
        number_of_clients_in_bling
        - number_of_in_place_delivery
        - number_of_third_party_delivery
    )

    return DailyInfo(
        number_of_clients_in_bling,
        number_of_in_place_meals,
        number_of_in_place_delivery,
        number_of_third_party_delivery,
        top_seven_by_value,
        total_sales,
    )


def send_whatsapp_msg(msg_info, search_date_str):
    search_date = datetime.strptime(search_date_str, "%d/%m/%Y").date()

    msg = f"""
No(a) *{handle_week_text(datetime.strftime(search_date, '%A'))}* dia *{search_date.strftime('%d/%m/%Y')}* vendemos *{msg_info.general_total}* refeições no TOTAL

O RECEITA foi de => *{locale.currency(msg_info.total_sales, grouping=True)}*

Sendo que:   
ATENDIDAS EM MESA => *{msg_info.in_place_meals}*
LEVOU MARMITA => *{msg_info.in_place_delivery}*
APPS DE DELIVERY => *{msg_info.third_party_delivery}*

E essa é a tabela dos 7 produtos com maior valor de venda

{tabulate(msg_info.top_7_sales_df, headers=['*Qtd*', '*Total R$*', '*Descrição*'], showindex=False, tablefmt="simple", numalign="left" )}
"""
    print(msg)

    pyperclip.copy(msg)
    print("Dados Copiados, para utilizar pressione CRTL + V")

    chrome_dir = user_config_dir("google-chrome")
    profile_path = os.path.join(chrome_dir, "Default")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=False,
                args=["--start-maximized"],
                no_viewport=True,
            )

            page = context.new_page()

            url = (
                f"https://web.whatsapp.com/accept?code={os.getenv('WHATSAPP_GROUP_ID')}"
            )
            # print(url)
            print(f"abrindo {page.title()}")
            page.goto(url, wait_until="domcontentloaded")
            print("WhatsappWeb Acessado com Sucesso!")
            msg_input = page.locator("div [title='Digite uma mensagem']")
            msg_input.fill(msg)
            send_btn = page.locator("[aria-label='Enviar']")
            send_btn.click()
            page.wait_for_timeout(6000)
            print("Sucesso!! Mensagem enviada")
            page.close()

    except Exception as Error:
        print(f"aqui deu ruim {Error}")


def handle_week_text(weekday_text):
    if weekday_text in ["segunda", "terça", "quarta", "quinta", "sexta"]:
        return weekday_text + "-feira"
    else:
        return weekday_text


def auth():
    print("auth")
    # code, state, env = read_config_file()
    server_init()
    API_URL = os.getenv("NEW_BLING_API_URL")
    CLIENT_ID = os.getenv("NEW_BLING_CLIENT_ID")
    SECRET_KEY = os.getenv("NEW_BLING_SECRET_KEY")
    AUTH_CODE = os.getenv("NEW_BLING_AUTH_CODE")
    # SCOPES_CODES = os.getenv("NEW_BLING_SCOPES")
    # api_key = os.getenv("BLING_API_KEY")
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        # "state": STATE_CODE,
        # "scopes": SCOPES_CODES,
    }

    client_id_in_base64 = base64.b64encode(CLIENT_ID.encode()).decode()
    secret_key_in_base64 = base64.b64encode(SECRET_KEY.encode()).decode()

    print(client_id_in_base64)
    print(secret_key_in_base64)
    credentials = f"{CLIENT_ID}:{SECRET_KEY}"
    credentials_in_base_64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "1.0",
        "Authorization": f"Basic {credentials_in_base_64}",
    }

    body = {
        "grant_type": "authorization_code",
        "code": "3376b6870ddb859d3b63a2eb945842f4988a42ed",
    }

    # print(params)

    try:
        resp = requests.post(f"{API_URL}/oauth/token", headers=headers, data=body)

        # reqtext = resp.text
        # print("o req=>", resp)
        # print("o reqtext=>", reqtext)
        # print("o is_redirect=>", resp.is_redirect)
        # dict_res = resp.json()
        # print("o dict_res=>", dict_res)

        print("Request URL:", resp.request.url)
        print("Request Headers:", resp.request.headers)
        print("Request Method:", resp.request.method)
        print("Request Body:", resp.request.body)
        print("Response Status Code:", resp.status_code)
        print("Response Content:", resp.text)

        # if "error" in dict_res:
        #     print("AQUI ESTA ENTRANDO SIMMMM")
        #     raise requests.HTTPError(dict_res.get("error").get("description"))

        # # api_return = dict_res.get(
        # #     "retorno",
        # # )

    except Exception as Error:
        print(f"aqui deu ruim na chamada nova {Error}")


def get_access_token():
    print("get_access_token")
    # Load configuration
    with open("config.json") as config_file:
        config_data = json.load(config_file)

        # Access values
        access_token: str = config_data["access_token"]
        refresh_token: str = config_data["refresh_token"]

        return (access_token, refresh_token)


def server_init():
    print("server_init")


if __name__ == "__main__":
    load_dotenv()
    # setar locale para português
    locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
    # auth()
    main()
