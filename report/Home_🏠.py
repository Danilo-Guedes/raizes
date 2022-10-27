import pandas as pd
import streamlit as st


# @st.cache
def load_data():
    df = pd.read_csv("data.csv", sep=";", thousands=".", decimal=",", encoding="utf_8")

    selected_columns = [
        "Data",
        "Cliente/Fornecedor",
        "Categoria",
        "Tipo",
        "Valor",
        "Banco",
        "Id",
    ]

    df = df[selected_columns]

    df.columns = df.columns.str.replace(" ", "_").str.lower()

    df["data"] = pd.to_datetime(
        df["data"],
        dayfirst=True,
    )

    df.assign(
        valor=df["valor"].astype("float16"),
        tipo=df["tipo"].astype("string").str.replace("C", "crédito", regex=False),
    )

    print(df.head())

    print(df["data"][0])
    print(type(df["data"][0]))
    print(df["valor"][0])
    print("#" * 50)
    print(df["valor"][0] + df["valor"][1])

    print("#" * 50)
    print(df.head()["tipo"])
    print(df.dtypes)
    print("#" * 50)
    print(df.tail()["tipo"])

    return df, df.columns


data, columns = load_data()

# print(data.head(50))

# st.write("Bem vindo ao Data-App de fechamento do Ra!zes")
_, col2, _ = st.columns([3, 5, 5])
col2.image("./images/logotipo_raizes.png", width=250)
st.markdown(
    """
    
    ## Olá :grinning:, seja bem vindo ao Data-App de análises do <span style='color:green;'>Ra!zes</span>

    > **Qual o objetivo do Data-App ?**

    - Ter uma visão da performance **Financeira** do Restaurante :moneybag: .
    - Também olhar para os detalhes e _insights_ sob a ótica de **Vendas** :credit_card:.
    - Pode Análisar os dados de **Delivery** :motor_scooter:.
    - Talvez analisar o perfil de consumidor pelo serviço da Stone? 

    """,
    unsafe_allow_html=True,
)

st.metric("metrica", value=600, delta=-1)
