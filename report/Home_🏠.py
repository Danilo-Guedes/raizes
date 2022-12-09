import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

_, first_line_col2, _ = st.columns((1, 1, 1))

_, second_line_col2, _ = st.columns((1, 7, 1))
first_line_col2.image("./images/logotipo_raizes.png", width=250)
second_line_col2.markdown(
    """    
    ## Olá :grinning: seja bem vindo(a) ao Data-App de análises do <span style='color:#a7c52b;'>Ra!zes</span><br>

    > <b style='color:#003400;font-size:22px'>Qual o objetivo do DataApp ?</b>

    - Ter uma visão da performance <b style='color:#003400;font-size:18px'>Financeira</b> do Restaurante :moneybag: .
    - Também olhar para os detalhes e _insights_ sob a ótica de <b style='color:#003400;font-size:18px'>Vendas</b> :credit_card:.
    - Pode Análisar os dados de <b style='color:#003400;font-size:18px'>Delivery</b> :motor_scooter:.
    - Talvez analisar o perfil de consumidor pelo serviço da Stone? :zombie:
    """,
    unsafe_allow_html=True,
)
