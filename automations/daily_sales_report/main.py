from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
import pywhatkit as pwk
from tabulate import tabulate
import os
from pathlib import Path
from datetime import date, datetime
import locale
from classes import DailyInfo
from appdirs import user_config_dir
import pyperclip


def main():
    file, search_date = download_bling_sales_csv()
    # file = download_folder_path = f"{Path.cwd()}/excel/daily_sales_report.csv"
    # search_date = datetime(2022, 10, 21)
    info = make_csv_analysis(file, search_date)
    send_whatsapp_msg(info)


def download_bling_sales_csv():
    """log in to Bling ERP, browse and saves sales csv file"""

    path = Path()

    download_folder_path = f"{path.cwd()}/excel"

    sales_date_str = input("Qual data deseja pesquisar?  : ")

    print("Iniciando extração dos dados do ERP Bling")

    selected_date = datetime.strptime(sales_date_str, "%d/%m/%Y").date()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        page = browser.new_page(no_viewport=True)
        page.goto(os.getenv("BLING_LOGIN_URL"))
        print(f"abrindo {page.title()}")

        page.locator("id=username").fill(os.getenv("BLING_USERNAME"))
        page.locator("id=senha").fill(os.getenv("BLING_PASSWORD"))
        page.locator("button:has-text('Entrar')").click()

        print("Acesso do Bling realizado")
        page.locator("xpath=//*[@id='menu-novo']/ul[1]/li[4]").click()
        page.locator("text=Relatórios >> nth=2").click()
        page.locator("text=Relatório de Vendas").click()
        page.locator("#periodoPesq").click()
        page.locator("#periodoPesq").select_option(value="opc-dia")

        page.locator("#p-data").fill(sales_date_str)

        page.locator("#campo1").click()
        page.locator("#campo1").select_option(value="p")

        page.wait_for_timeout(1000)

        page.locator("#btn_visualizar").click()

        with page.expect_download() as download_info:
            # Perform the action that initiates download
            page.locator("#exportarRelatorio").click()
            page.locator("button:has-text('Exportar')").click()

        download = download_info.value

        file_path = f"{download_folder_path}/daily_sales_report.csv"

        download.save_as(file_path)

        print("Arquivo baixado e pronto para processamento dos dados")

        page.close()
        browser.close()

        return file_path, selected_date


def make_csv_analysis(file, searched_date):
    df = pd.read_csv(file, sep=";", decimal=",", thousands=".", encoding="utf_8")
    df.columns = df.columns.str.replace(" ", "_").str.lower()
    # print(df.columns)
    df = df.drop(columns=df.columns[1])[:-1]

    df_by_value = df.sort_values(by=["total_venda"], ascending=False)
    df = df.sort_values(by=["qtde"], ascending=False)

    total_sales = round(df["total_venda"].sum(), 2)

    top_seven_by_value = df_by_value.head(7)[["produto", "qtde", "total_venda"]]

    top_seven_by_value = top_seven_by_value.assign(
        total_venda=top_seven_by_value["total_venda"]
        .astype("float16")
        .map(lambda x: locale.currency(x, grouping=True)),
        qtde=top_seven_by_value["qtde"].astype("int"),
        # produto=top_seven_by_value['produto'].astype('string').str[:15],
    ).reindex(columns=["qtde", "total_venda", "produto"])

    # print(top_seven_by_value)

    produtcs_to_count_as_client = df[df["produto"].str.contains("*", regex=False)]

    in_place_delivery = df[df["produto"].str.startswith("(Viagem")]

    # print(in_place_delivery)

    third_party_delivery = df[
        df["produto"].str.contains("Delivery", regex=False)
        & df["produto"].str.contains("*", regex=False)
    ]

    number_of_clients_in_bling = produtcs_to_count_as_client["qtde"].sum().astype("int")

    number_of_in_place_delivery = in_place_delivery["qtde"].sum().astype("int")

    number_of_third_party_delivery = third_party_delivery["qtde"].sum().astype("int")

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
        searched_date,
    )


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
