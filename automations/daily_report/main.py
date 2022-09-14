from playwright.sync_api import sync_playwright
import os
import time
from dotenv import load_dotenv



def outracoisa():
    print('coisa')

def main():
    print('main')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(os.getenv('BLING_LOGIN_URL'))
        print(page.title())

        page.locator('id=username').fill(os.getenv('BLING_USERNAME'))
        page.locator('id=senha').fill(os.getenv('BLING_PASSWORD'))
        page.locator('//*[@id="login-buttons-site"]/button').click()

        time.sleep(5000)
        print('finalizou')
        browser.close()




if __name__ == '__main__':
    load_dotenv()
    main()