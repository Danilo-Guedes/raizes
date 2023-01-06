from time import timezone
import pandas as pd
import streamlit as st
import locale
import altair as alt
import numpy as np


locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


@st.cache
def load_data(file):

    ## main df

    df = pd.read_csv(
        file,
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
        # "Preço de custo",
        "Descrição",
        "Quantidade",
        # "Preço unitário",
        # "Total dos Produtos",
        "Valor total",
    ]

    df = df[selected_columns]

    df = df.rename(columns=str.lower)
    df = df.rename(
        columns={
            "descrição": "descricao",
            # "preço de custo": "preco_de_custo",
            "valor total": "valor_total",
            # "preço unitário": "preco_unitario",
            # "total dos produtos": "total_dos_produtos",
        }
    )

    df["dia"] = df["data"].dt.day
    df["mês"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name(locale.getlocale())

    df["data"] = df["data"].dt.date

    # # print(df.columns)
    # # print(df.dtypes)

    df["quantidade"] = df["quantidade"].astype(int)

    # df.assign(
    #     valor=df["valor"].round(2).astype("float16"),
    #     fornecedor=df["fornecedor"].astype("category"),
    #     categoria=df["categoria"].astype("category"),
    # )

    # ## end-main df cleanup and enhancements

    # ## extract totals and relevant data

    total_sales_sum = df["valor_total"].sum()

    # ## GROUPBY
    # income_by_category_df = (
    #     income_df.groupby("categoria", as_index=False)
    #     .sum(numeric_only=True)
    #     .drop(
    #         labels=[
    #             "id",
    #             "dia",
    #             "mês",
    #             "ano",
    #         ],
    #         axis="columns",
    #     )
    # )

    # income_by_category_df = income_by_category_df.sort_values(
    #     by="valor", ascending=False
    # ).assign(
    #     position=range(len(income_by_category_df))
    # )  ##adding position foir conditional render color, ...

    # expenses_by_category_df = (
    #     expenses_df.groupby(by="categoria", as_index=False)
    #     .sum(numeric_only=True)
    #     .drop(
    #         labels=[
    #             "id",
    #             "dia",
    #             "mês",
    #             "ano",
    #         ],
    #         axis="columns",
    #     )
    # )

    # ## TOPS DFS

    # top10_exp_df = (
    #     expenses_by_category_df.nlargest(10, "valor")
    #     .sort_values(by="valor", ascending=False)
    #     .assign(position=range(10))
    # )

    print(df.head())
    print(total_sales_sum)
    # print(df)
    # print(df.columns)
    # print(df.info())

    return (df, total_sales_sum)


# data, tt_income, tt_expenses = load_data()


# st.set_page_config(layout="wide")

st.markdown(
    """
 ### Análise de Vendas"""
)
# data.dtypes

uploaded_file = st.file_uploader(
    label="IMPORTE O RELATÓRIO DE VENDAS DO BLING NO FORMATO CSV",
    key="uploader",
    type=["csv"],
    help="para de ser burro, não tem segredo fazer um upload",
)

if uploaded_file is not None:
    (data, total_sales_sum) = load_data(uploaded_file)

    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("A cara dos dados:"):
        st.write("(Linha,Colunas)", data.shape)
        st.dataframe(data)
