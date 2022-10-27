import pandas as pd
import streamlit as st


@st.cache
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

    return df, df.columns


data, columns = load_data()

# print(data.head(50))

st.write("Essa é a pagina de Análise Financeira")

st.dataframe(data)
st.bar_chart(data=data, y="valor")
