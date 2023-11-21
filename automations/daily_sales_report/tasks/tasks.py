import os
import pyperclip
import locale

from playwright.sync_api import sync_playwright
from colorama import Fore
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from datetime import datetime
from appdirs import user_config_dir

from api.bling import  get_sales_by_date, get_sale_by_id
from utils.strings import handle_week_text
from classes import DailyInfo



def call_bling_api(date_string):
    try:
        resp = get_sales_by_date(date_string)

        sales_ids = [item.get("id") for item in resp]
        # print("the idssss", sales_ids)

        print(
            f"Foram identificadas {len(sales_ids)} ocorrências de vendas, e serão requisitadas individualmente..."
        )

        final_data = []

        for id in sales_ids:
            resp = get_sale_by_id(id)

            final_data.append(resp)

        # print("final_data: ", final_data)

        return final_data

    except Exception as err:
        print(Fore.RED + f"OPA!!, ALGUM ERRO OCORREU em call_bling_api=> {err}")


def api_response_to_list(raw_sales):
    """
    tranform the api response into a list while treat discount values
    """

    list_of_products = []

    for sales in raw_sales:

        if sales.get("desconto").get("valor", 0) > 0:
            disccount_value: float = sales.get("totalProdutos") - sales.get("total")
            item_to_disccount = max(
                sales.get("itens", []), key=lambda x: x.get("valor", 0)
            )

            item_to_disccount["valor"] = (
                item_to_disccount.get("valor", 0) - disccount_value
            )

        for item in sales.get("itens"):
            list_of_products.append(item)

    print("Dado Tratado com Sucesso e enviado pra o Pandas fazer sua mágica....")

    return list_of_products


def generate_clean_df(prod_list):
    df = pd.DataFrame(prod_list)

    df = df.drop(
        columns=[
            "unidade",
            "codigo",
            "aliquotaIPI",
            "descricaoDetalhada",
            "produto",
            "comissao",
        ]
    )

    df["total"] = df["valor"] * df["quantidade"]

    # GROUPING ROWS WITH THE SAME CODE
    agg_options = {
        "quantidade": "sum",
        "valor": "last",
        "descricao": "last",
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
