import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

_, first_line_col2, _ = st.columns((1, 1, 1))

_, second_line_col2, _ = st.columns((1, 5, 1))
first_line_col2.image("./images/logotipo_raizes.png", width=300)
second_line_col2.markdown(
    """
    
    ## Olá :grinning: seja bem vindo(a) ao Data-App de análises do <span style='color:#a7c52b;'>Ra!zes</span>

    > **Qual o objetivo do Data-App ?**

    - Ter uma visão da performance **Financeira** do Restaurante :moneybag: .
    - Também olhar para os detalhes e _insights_ sob a ótica de **Vendas** :credit_card:.
    - Pode Análisar os dados de **Delivery** :motor_scooter:.
    - Talvez analisar o perfil de consumidor pelo serviço da Stone? 

    """,
    unsafe_allow_html=True,
)
