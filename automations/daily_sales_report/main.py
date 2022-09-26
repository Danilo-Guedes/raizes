from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
import pywhatkit as pwk
from tabulate import tabulate
import os
from pathlib import Path
from datetime import date, datetime
import locale


def main():
    file, search_date = download_bling_sales_csv()
    # file = download_folder_path = f"{Path.cwd()}/excel/daily_sales_report.csv"
    # search_date = date(2022, 9, 23)

    general_total, in_place_meals, in_place_delivery, third_party_delivery, top_5_sales_df, total_sales = make_csv_analysis(
        file)

    send_whatsapp_msg(general_total, in_place_meals, in_place_delivery,
                      third_party_delivery, top_5_sales_df, total_sales,  search_date)


def download_bling_sales_csv():
    """log in to Bling ERP, browse and saves sales csv file"""

    path = Path()

    download_folder_path = f"{path.cwd()}/excel"

    sales_date_str = input('Qual data deseja pesquisar?  : ')

    print('Iniciando extração dos dados do ERP Bling')

    selected_date = datetime.strptime(sales_date_str, '%d/%m/%Y').date()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(os.getenv('BLING_LOGIN_URL'))
        print(f"abrindo {page.title()}")

        page.locator('id=username').fill(os.getenv('BLING_USERNAME'))
        page.locator('id=senha').fill(os.getenv('BLING_PASSWORD'))
        page.locator("button:has-text('Entrar')").click()

        print('Acesso do Bling realizado')
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

        print('Arquivo baixado e pronto para processamento dos dados')

        page.close()
        browser.close()

        return [file_path, selected_date]


def make_csv_analysis(file):
    df = pd.read_csv(file, sep=";",  decimal=',',
                     thousands='.', encoding="utf_8")
    df = df.drop(columns=df.columns[1])[:-1]
    df_by_value = df.sort_values(by=['Total Venda'], ascending=False)
    df = df.sort_values(by=['Qtde'], ascending=False)

    total_sales = round(df['Total Venda'].sum(), 2)

    top_five_by_value = df_by_value.head()[['Produto', 'Qtde', 'Total Venda']]

    produtcs_to_count_as_client = df[df['Produto'].str.contains(
        '*', regex=False)]

    in_place_delivery = df[df['Produto'].str.contains(
        'Viagem salão', regex=False)]

    third_party_delivery = df[df['Produto'].str.contains(
        'Delivery', regex=False)]

    number_of_clients_in_bling = produtcs_to_count_as_client['Qtde'].sum().astype(
        'int')

    number_of_in_place_delivery = in_place_delivery['Qtde'].sum().astype(
        'int')

    number_of_third_party_delivery = third_party_delivery['Qtde'].sum().astype(
        'int')

    number_of_in_place_meals = number_of_clients_in_bling - \
        number_of_in_place_delivery - number_of_third_party_delivery

    return [number_of_clients_in_bling, number_of_in_place_meals, number_of_in_place_delivery, number_of_third_party_delivery, top_five_by_value, total_sales]


def send_whatsapp_msg(general_total, in_place_meals, in_place_delivery, third_party_delivery, top_5_sales_df, total_money, date):
    # print('#' * 130)
    # print(
    #     f"O número TOTAL de REFEIÇÕES VENDIDAS em {date.strftime('%d/%m/%Y')} foi => {general_total}")
    # print(
    #     f"Sendo PESSOAS ATENDIDAS NO LOCAL => {in_place_meals}")
    # print(
    #     f"Pessaos que RETIRARAM a marmita no local => {in_place_delivery}")
    # print(""""""
    #       f"E pessaos que PEDIRAM NOS APPS DE DELIVERY => {third_party_delivery}")

    # print('_' * 130)

    # print('E essa é tabela dos 5 produtos com maior valor de venda')
    # print(top_5_sales_df)

    msg = f"""
O numero *total* de REFEICOES VENDIDAS na(o) {datetime.strftime(date, '%A')} dia {date.strftime('%d/%m/%Y')} foi => *{general_total}*   
ATENDIDAS EM MESA => *{in_place_meals}* 
LEVOU MARMITA => *{in_place_delivery}*
APPS DE DELIVERY => *{third_party_delivery}*

O total de vendas foi => R$ {total_money}

E essa eh a tabela dos 5 produtos com maior valor de venda
{tabulate(top_5_sales_df, showindex=False, tablefmt="simple", colalign=['left', 'right', 'right'])}
    """

    hour = datetime.now().hour
    minute = datetime.now().minute + 2

    try:
        print(msg)
        pwk.sendwhatmsg_to_group_instantly(group_id=os.getenv('WHATSAPP_GROUP_ID'), message=msg,
                                           wait_time=10, tab_close=True, close_time=5)

    except Exception as Error:
        print(f'aqui deu ruim {Error}')


if __name__ == '__main__':
    load_dotenv()
    # setar locale para português
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    main()
