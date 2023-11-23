import locale
from dotenv import load_dotenv
from colorama import init

from tasks.tasks import (
    call_bling_api,
    api_response_to_list,
    generate_clean_df,
    prepare_relevant_info,
    send_whatsapp_msg,
)


def main():
    search_date_str = input("Qual data deseja pesquisar?  : ")
    sales = call_bling_api(search_date_str)
    products_list = api_response_to_list(sales)
    clean_df = generate_clean_df(products_list)
    info = prepare_relevant_info(clean_df)
    send_whatsapp_msg(info, search_date_str)


if __name__ == "__main__":
    load_dotenv()
    init(autoreset=True)
    # setar locale para português
    locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
    
    main()
