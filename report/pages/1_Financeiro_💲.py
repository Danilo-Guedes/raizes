from time import timezone
import pandas as pd
import streamlit as st
import locale
import calendar
import altair as alt


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
    df["dia_semana"] = df["data"].dt.day_name(locale.getlocale())

    df["data"] = df["data"].dt.date

    # print(df.columns)
    # print(df.dtypes)

    df.assign(
        valor=df["valor"].round(2).astype("float16"),
        tipo=df["tipo"].astype("category"),
        fornecedor=df["fornecedor"].astype("category"),
        categoria=df["categoria"].astype("category"),
    )

    ## end-main df cleanup and enhancements

    ## remove ! symbols
    df = df[df["categoria"].str.contains("!", regex=False, na=True) == False]

    ## extract totals and relevant data

    income_df = df.loc[df["tipo"] == "receita"]
    expenses_df = df.loc[df["tipo"] == "despesa"]

    # print(expenses_df)

    ## GROUPBY
    income_by_category_df = (
        income_df.groupby("categoria", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mês",
                "ano",
            ],
            axis="columns",
        )
    )
    expenses_by_category_df = (
        expenses_df.groupby(by="categoria", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mês",
                "ano",
            ],
            axis="columns",
        )
    )

    # print(income_by_category_df)
    # print(expenses_by_category_df)
    # print(expenses_by_category_df)

    return df, income_df, expenses_df, income_by_category_df, expenses_by_category_df


# data, tt_income, tt_expenses = load_data()

# print(data.head(50))

st.set_page_config(layout="wide")

st.markdown(
    """
 # Análise Financeira"""
)
# data.dtypes

uploaded_file = st.file_uploader(
    label="IMPORTE O EXTRATO NO BLING NO FORMATO CSV",
    key="uploader",
    type=["csv"],
    help="para de ser burro, não tem segredo fazer um upload",
)

if uploaded_file is not None:
    (
        data,
        income_df,
        expenses_df,
        income_by_category_df,
        expenses_by_category_df,
    ) = load_data(uploaded_file)

    with st.expander("A cara dos dados:"):
        st.write("(Linha,Colunas)", data.shape)
        st.dataframe(data)

    st.markdown(
        f""" ## O Total de Receitas do período foi de <b style='color:green;'>{locale.currency(income_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" ## O Total de Despesas do período foi de <b style='color:red;'>{locale.currency(expenses_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f""" ### O Resultado Bruto (rec - des) foi de <b>{locale.currency(income_df['valor'].sum() - expenses_df['valor'].sum(), grouping=True)}</b>.""",
        unsafe_allow_html=True,
    )

    st.header("Top 10 despesas por valor R$")

    top10_expenses = (
        alt.Chart(expenses_by_category_df.nlargest(10, "valor"))
        .mark_bar()
        .encode(alt.X("categoria", sort="-y"), alt.Y("valor"))
        .properties(width=1400, height=500)
    )

    st.altair_chart(top10_expenses)
