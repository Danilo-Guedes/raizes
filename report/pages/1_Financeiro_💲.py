from time import timezone
import pandas as pd
import streamlit as st
import locale
import calendar


locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


@st.cache
def load_data():

    ## main df

    df = pd.read_csv(
        "data.csv",
        sep=";",
        thousands=".",
        decimal=",",
        encoding="utf_8",
        parse_dates=["Data"],
        # date_parser=lambda col: pd.to_datetime(col, utc=True).tz_convert("UTC"),
        dayfirst=True,
    )

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

    df = df.rename(columns=str.lower)
    df = df.rename(columns={"cliente/fornecedor": "fornecedor"})
    df["tipo"] = df["tipo"].map(lambda tp: "receita" if tp == "C" else "despesa")

    df["dia"] = df["data"].dt.day
    df["mês"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name()

    df["data"] = df["data"].dt.date

    # print(df.dtypes)

    df.assign(
        valor=df["valor"].astype("float16"),
        tipo=df["tipo"].astype("category"),
        fornecedor=df["fornecedor"].astype("category"),
        categoria=df["categoria"].astype("category"),
    )
    ## end-main df cleanup and enhancements

    print(type(df["data"][0]))

    ## remove ! symbols
    df = df[df["categoria"].str.contains("!", regex=False, na=True) == False]

    ## extract totals and relevant data

    total_income = pd.pivot_table(data=df, columns="tipo", aggfunc=sum)  ##MUDAAAAAAR
    print("#" * 50)
    print(type(total_income))
    print(total_income)
    return df, total_income


data, total_income = load_data()

# print(data.head(50))

st.markdown(
    """
 ## Análise Financeira"""
)
# data.dtypes

with st.expander("A cara dos dados:"):
    st.write("(Linha,Colunas)", data.shape)
    st.dataframe(data)

st.write(
    f"O Total de Receitas do período foi de {locale.currency(total_income['receita'][-1], grouping=True)}"
)  ##MUDDAAARRR

st.bar_chart(data=data.sort_values(by=["data"], ascending=False), y="valor", x="data")
