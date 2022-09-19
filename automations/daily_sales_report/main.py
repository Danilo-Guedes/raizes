from playwright.sync_api import sync_playwright
import pandas as pd
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import date


def main():
    file, search_date = download_bling_sales_csv()
    # file = download_folder_path = f"{Path.cwd()}/excel/daily_sales_report.csv"
    # search_date = date(2022, 9, 18)

    make_csv_analysis(file, search_date)


def download_bling_sales_csv():
    """log in to Bling ERP, browse and saves sales csv file"""
    print('Iniciando extração dos dados do ERP Bling')

    path = Path()

    download_folder_path = f"{path.cwd()}/excel"

    sales_date_str = input('Qual data deseja pesquisar?  : ')

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

        page.wait_for_timeout(5000)

        print('Arquivo baixado e pronto para processamento dos dados')

        page.close()
        browser.close()

        return [file_path, selected_date]


def make_csv_analysis(file, date):
    df = pd.read_csv(file, sep=";",  decimal=',',
                     thousands='.', encoding="utf_8")
    # removing second column with no data and last row with totals
    df = df.drop(columns=df.columns[1])[:-1]
    print(df.describe())
    print('#' * 130)
    df = df.sort_values(by=['Qtde'], ascending=False)
    print(df.head())

    produtcs_to_count_as_client = df[df['Produto'].str.contains(
        '*', regex=False)]

    print('#' * 130)
    print(produtcs_to_count_as_client)
    number_of_clients_in_bling = produtcs_to_count_as_client['Qtde'].sum().astype(
        'int')
    print('#' * 130)
    print(
        f"o número de pessoas atendidas em {date.strftime('%d/%m/%Y')} foi => {number_of_clients_in_bling}")


if __name__ == '__main__':
    load_dotenv()
    main()
