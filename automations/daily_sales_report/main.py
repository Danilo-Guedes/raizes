from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
import pywhatkit
import os
from pathlib import Path
from datetime import date, datetime


def main():
    # file, search_date = download_bling_sales_csv()
    file = download_folder_path = f"{Path.cwd()}/excel/daily_sales_report.csv"
    search_date = date(2022, 9, 23)

    general_total, in_place_meals, in_place_delivery, third_party_delivery, top_5_sales_df = make_csv_analysis(
        file)

    send_whatsapp_msg(general_total, in_place_meals, in_place_delivery,
                      third_party_delivery, top_5_sales_df, search_date)


def download_bling_sales_csv():
    """log in to Bling ERP, browse and saves sales csv file"""

    path = Path()

    download_folder_path = f"{path.cwd()}/excel"

    sales_date_str = input('Qual data deseja pesquisar?  : ')

    print('Iniciando extração dos dados do ERP Bling')

    split = sales_date_str.split('/')

    selected_date = date(int(split[2]), int(split[1]), int(split[0]))

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
        # # Wait for the download process to complete
        # # Save downloaded file somewhere

        file_path = f"{download_folder_path}/daily_sales_report.csv"

        download.save_as(file_path)

        # page.wait_for_timeout(5000)

        print('Arquivo baixado e pronto para processamento dos dados')

        page.close()
        browser.close()

        return [file_path, selected_date]


def make_csv_analysis(file):
    df = pd.read_csv(file, sep=";",  decimal=',',
                     thousands='.', encoding="utf_8")
    # removing second column with no data and last row with totals
    df = df.drop(columns=df.columns[1])[:-1]
    # print(df.describe())
    # print('#' * 130)
    df_by_value = df.sort_values(by=['Total Venda'], ascending=False)
    df = df.sort_values(by=['Qtde'], ascending=False)

    # print(df_by_value.head()[['Produto', 'Qtde', 'Total Venda']])

    top_five_by_value = df_by_value.head()[['Produto', 'Qtde', 'Total Venda']]

    produtcs_to_count_as_client = df[df['Produto'].str.contains(
        '*', regex=False)]

    in_place_delivery = df[df['Produto'].str.contains(
        'Viagem salão', regex=False)]

    third_party_delivery = df[df['Produto'].str.contains(
        'Delivery', regex=False)]

    # print('#' * 130)
    # print(produtcs_to_count_as_client)
    number_of_clients_in_bling = produtcs_to_count_as_client['Qtde'].sum().astype(
        'int')

    number_of_in_place_delivery = in_place_delivery['Qtde'].sum().astype(
        'int')

    number_of_third_party_delivery = third_party_delivery['Qtde'].sum().astype(
        'int')

    number_of_in_place_meals = number_of_clients_in_bling - \
        number_of_in_place_delivery - number_of_third_party_delivery

    return [number_of_clients_in_bling, number_of_in_place_meals, number_of_in_place_delivery, number_of_third_party_delivery, top_five_by_value]


def send_whatsapp_msg(general_total, in_place_meals, in_place_delivery, third_party_delivery, top_5_sales_df, date):
    print('#' * 130)
    print(
        f"O número TOTAL de REFEIÇÕES VENDIDAS em {date.strftime('%d/%m/%Y')} foi => {general_total}")
    print(
        f"Sendo PESSOAS ATENDIDAS NO LOCAL => {in_place_meals}")
    print(
        f"Pessaos que RETIRARAM a marmita no local => {in_place_delivery}")
    print(""""""
          f"E pessaos que PEDIRAM NOS APPS DE DELIVERY => {third_party_delivery}")

    print('_' * 130)

    print('E essa é tabela dos 5 produtos com maior valor de venda')
    print(top_5_sales_df)

    msg = f"""

        O número TOTAL de REFEIÇÕES VENDIDAS em {date.strftime('%d/%m/%Y')} foi => {general_total}
    
        Sendo PESSOAS ATENDIDAS NO LOCAL => {in_place_meals}
    
        Pessaos que RETIRARAM a marmita no local => {in_place_delivery}

        E pessaos que PEDIRAM NOS APPS DE DELIVERY => {third_party_delivery}


        E essa é tabela dos 5 produtos com maior valor de venda
        {top_5_sales_df}
    """

    TESTE_MSG = 'BLABLA BALBLA'
    # print(msg)

    hour = int(datetime.now().time().hour)
    minute = int(datetime.now().time().minute + 1)

    try:
        pywhatkit.sendwhatmsg_to_group(
            'CkvTMz00lbUBaJaBKeYXYO', 'ta estrahno', hour, minute, 3, False, 3)

    except Exception as Error:
        print(f'aqui deu ruim {Error}')


if __name__ == '__main__':
    load_dotenv()
    main()
