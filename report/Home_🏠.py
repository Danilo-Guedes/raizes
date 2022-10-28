import pandas as pd
import streamlit as st

_, col2, _ = st.columns([3, 5, 5])
col2.image("./images/logotipo_raizes.png", width=250)
st.markdown(
    """
    
    ## Olá :grinning: seja bem vindo(a) ao Data-App de análises do <span style='color:green;'>Ra!zes</span>

    > **Qual o objetivo do Data-App ?**

    - Ter uma visão da performance **Financeira** do Restaurante :moneybag: .
    - Também olhar para os detalhes e _insights_ sob a ótica de **Vendas** :credit_card:.
    - Pode Análisar os dados de **Delivery** :motor_scooter:.
    - Talvez analisar o perfil de consumidor pelo serviço da Stone? 

    """,
    unsafe_allow_html=True,
)
