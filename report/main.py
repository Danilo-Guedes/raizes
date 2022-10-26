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

st.write("Bem vindo ao Data-App de fechamento do Ra!zes")
st.write(data)
st.write(columns)
