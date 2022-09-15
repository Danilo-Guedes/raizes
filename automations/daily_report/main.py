from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from datetime import date


def main():
    print('Iniciando extração dos dados do ERP Bling')
    download_bling_sales_csv()


def download_bling_sales_csv():
    """log in to Bling ERP, browse and saves sales csv file"""

    sales_date_str = input('Qual data deseja pesquisar?  : ')

    split = sales_date_str.split('/')

    dateobj = date(int(split[2]), int(split[1]), int(split[0]))
    print('o date obj', dateobj)
    print(type(dateobj))

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

        page.locator("#btn_visualizar").click()

        page.locator("#exportarRelatorio").click()
        page.locator("button:has-text('Exportar')").click()
        page.wait_for_timeout(10000)

        print('finalizou')
        browser.close()


if __name__ == '__main__':
    load_dotenv()
    main()
