import requests
import pyperclip
from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
from tabulate import tabulate
import os
from pathlib import Path
from datetime import date, datetime
import locale
from classes import DailyInfo
from appdirs import user_config_dir


def main():
    sales_date_str = input("Qual data deseja pesquisar?  : ")
    orders = call_bling_api(sales_date_str)

    products_list = data_adapter(orders, sales_date_str)

    do_the_pandas_magic(products_list)

    # file, search_date = download_bling_sales_csv()
    # # file = download_folder_path = f"{Path.cwd()}/excel/daily_sales_report.csv"
    # # search_date = datetime(2022, 10, 21)
    # info = make_csv_analysis(file, search_date)
    # send_whatsapp_msg(info)


def call_bling_api(date_string):

    endpoint = "https://bling.com.br/Api/v2/pedidos/json/"
    api_key = os.getenv("BLING_API_KEY")
    search_date_param = f"dataEmissao[{date_string} TO {date_string}]"

    try:
        r = requests.get(
            endpoint, params={"apikey": api_key, "filters": search_date_param}
        )
        # print(r.url)

        dict_res = r.json()
        # print(dict.keys(dict_res))

        api_return = dict_res.get("retorno")
        # print("retorno", api_return)

        if api_return.get("erros") is not None:
            api_errors = api_return.get("erros")
            print(api_errors)

            if type(api_errors) == list:
                print("erro na api ==>>>", api_errors[0]["erro"]["msg"])
            else:
                print("erro na api ==>>>", api_errors["erro"]["msg"])

        else:
            print("Api do Blig retornou com sucesso!")
            orders = api_return.get("pedidos")

            if orders is not None:
                # print("orders", orders)
                print(f"{len(orders)} ocorrências de vendas")
                print("type da orders", type(orders))
                return orders

    except Exception as err:
        print("aqui deu erro", err)


def data_adapter(raw_orders, searched_date):
    """
    aqui é pra jogar o dado pro pandas e gerar os totais conf o retorno da função antiga
    """

    list_of_products = []

    for order in raw_orders:
        if order["pedido"]["desconto"] != "0,00":

            discount_in_cash = float(order["pedido"]["totalprodutos"]) - float(
                order["pedido"]["totalvenda"]
            )

            for order_itens in order["pedido"]["itens"]:
                final_item_value = float(order_itens["item"]["quantidade"]) * float(
                    order_itens["item"]["valorunidade"]
                )

                if final_item_value > discount_in_cash:
                    order_itens["item"]["descontoItem"] = discount_in_cash
                    break

        for product in order["pedido"]["itens"]:
            list_of_products.append(product["item"])

    print("Dado Tratado com Sucesso e enviado pra o Pandas fazer sua mágica....")

    return list_of_products


def do_the_pandas_magic(prod_list):

    df = pd.DataFrame(prod_list)

    print("columns", df.columns)

    # print("types before", df.dtypes)

    df = df.drop(
        columns=[
            "un",
            "precocusto",
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
    df["descontoItem"] = df["descontoItem"].astype("float64")
    df["total"] = (df["valorunidade"] * df["quantidade"]) - df["descontoItem"]

    print("types after", df.dtypes)

    print("o df antes de gerar o arquivo", df)

    df.to_csv(f"{Path.cwd()}/excel/api.csv", sep=";", decimal=",")
    print("### Arquivo Gerado com Sucesso! ###")

    # df = pd.read_csv(file, sep=";", decimal=",", thousands=".", encoding="utf_8")
    # df.columns = df.columns.str.replace(" ", "_").str.lower()
    # # print(df.columns)
    # df = df.drop(columns=df.columns[1])[:-1]

    # df_by_value = df.sort_values(by=["total_venda"], ascending=False)
    # df = df.sort_values(by=["qtde"], ascending=False)

    # total_sales = round(df["total_venda"].sum(), 2)

    # top_seven_by_value = df_by_value.head(7)[["produto", "qtde", "total_venda"]]

    # top_seven_by_value = top_seven_by_value.assign(
    #     total_venda=top_seven_by_value["total_venda"]
    #     .astype("float16")
    #     .map(lambda x: locale.currency(x, grouping=True)),
    #     qtde=top_seven_by_value["qtde"].astype("int"),
    #     # produto=top_seven_by_value['produto'].astype('string').str[:15],
    # ).reindex(columns=["qtde", "total_venda", "produto"])

    # # print(top_seven_by_value)

    # produtcs_to_count_as_client = df[df["produto"].str.contains("*", regex=False)]

    # in_place_delivery = df[df["produto"].str.startswith("(Viagem")]

    # # print(in_place_delivery)

    # third_party_delivery = df[
    #     df["produto"].str.contains("Delivery", regex=False)
    #     & df["produto"].str.contains("*", regex=False)
    # ]

    # number_of_clients_in_bling = produtcs_to_count_as_client["qtde"].sum().astype("int")

    # number_of_in_place_delivery = in_place_delivery["qtde"].sum().astype("int")

    # number_of_third_party_delivery = third_party_delivery["qtde"].sum().astype("int")

    # number_of_in_place_meals = (
    #     number_of_clients_in_bling
    #     - number_of_in_place_delivery
    #     - number_of_third_party_delivery
    # )

    # return DailyInfo(
    #     number_of_clients_in_bling,
    #     number_of_in_place_meals,
    #     number_of_in_place_delivery,
    #     number_of_third_party_delivery,
    #     top_seven_by_value,
    #     total_sales,
    #     searched_date,
    # )


def send_whatsapp_msg(msg_info):

    msg = f"""
No(a) *{handle_week_text(datetime.strftime(msg_info.search_date, '%A'))}* dia *{msg_info.search_date.strftime('%d/%m/%Y')}* vendemos *{msg_info.general_total}* refeições no TOTAL

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
            msg_input = page.locator("div [title='Mensagem']")
            msg_input.fill(msg)
            send_btn = page.locator("[aria-label='Enviar']")
            send_btn.click()
            print("Sucesso!! Mensagem enviada")
            page.wait_for_timeout(2500)
            page.close()

    except Exception as Error:
        print(f"aqui deu ruim {Error}")


def handle_week_text(weekday_text):

    if weekday_text in ["segunda", "terça", "quarta", "quinta", "sexta"]:
        return weekday_text + "-feira"
    else:
        return weekday_text


if __name__ == "__main__":
    load_dotenv()
    # setar locale para português
    locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
    main()
