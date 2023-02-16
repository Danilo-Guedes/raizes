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

    income_sum_by_weekday_df = (
        income_df.groupby("dia_semana", as_index=False)
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
        .sort_values(by="valor", ascending=False)
    )

    # ADDING TOTAL LAST LINE
    income_sum_by_weekday_df.loc[len(income_sum_by_weekday_df)] = [
        "Total",
        income_sum_by_weekday_df["valor"].sum(),
    ]
    # SET VALUES TO CURRENCY
    income_sum_by_weekday_df["valor"] = income_sum_by_weekday_df["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )
    income_sum_by_weekday_df.reset_index(drop=True, inplace=True)

    print(income_sum_by_weekday_df)

    income_by_category_df = income_by_category_df.sort_values(
        by="valor", ascending=False
    ).assign(
        position=range(len(income_by_category_df))
    )  ##adding position foir conditional render color, ...

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

    ## TOPS DFS

    top10_exp_df = (
        expenses_by_category_df.nlargest(10, "valor")
        .sort_values(by="valor", ascending=False)
        .assign(position=range(10))
    )

    return (
        df,
        income_df,
        expenses_df,
        income_by_category_df,
        expenses_by_category_df,
        top10_exp_df,
        income_sum_by_weekday_df,
    )


# data, tt_income, tt_expenses = load_data()


st.set_page_config(layout="wide")

st.markdown(
    """
 ### Análise Financeira"""
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
        top10_exp_df,
        income_sum_by_weekday_df,
    ) = load_data(uploaded_file)

    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("A cara dos dados:"):
        st.write("(Linha,Colunas)", data.shape)
        st.dataframe(data)

    st.markdown(
        f""" #### <br> O total de <b style='color:#a7c52b'>Receitas</b> do período foi de <b style='color:#a7c52b;'>{locale.currency(income_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" #### O total de <b style='color:#f19904'>Despesas</b> do período foi de <b style='color:#f19904'>{locale.currency(expenses_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f""" ##### O resultado bruto (rec - des) foi de <b style='color:#003400;font-size:26px;text-decoration:underline;'>{locale.currency(income_df['valor'].sum() - expenses_df['valor'].sum(), grouping=True)}</b>.<br>""",
        unsafe_allow_html=True,
    )

    st.markdown("***")

    st.markdown(
        f""" #### Top 10  <b style='color:#f19904'>Despesas</b> por categoria + (%) <br><br>
        """,
        unsafe_allow_html=True,
    )

    top10_expenses = (
        alt.Chart(top10_exp_df)
        .mark_bar()
        .encode(
            alt.Y(
                "categoria:N",
                sort=alt.EncodingSortField("value", op="max", order="descending"),
                axis=alt.Axis(title=""),
            ),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor", titlePadding=15, format="$,.2f", tickMinStep=5000
                ),
            ),
            color=alt.condition(
                alt.datum.position < 3,
                alt.value("#f19904"),
                alt.value("lightgray"),  ## higlight only top 3 expenses
            ),
        )
        .properties(width=1400, height=500)
    )

    label_top10_expenses = (
        top10_expenses.mark_text(
            align="left",
            baseline="middle",
            dx=15,  # Nudges text to right so it doesn't appear on top of the bar
        )
        .encode(text=alt.Text("percentage:Q", format=".2%"))
        .transform_calculate(percentage=f"datum.valor / {expenses_df['valor'].sum()}")
    )

    st.altair_chart(
        (top10_expenses + label_top10_expenses).configure_axis(
            labelFontSize=16, titleFontSize=20, titleColor="#f19904", grid=False
        )
    )

    st.markdown("***")

    st.markdown(
        f""" #### <b style='color:#a7c52b'>Receitas</b> por categoria<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.altair_chart(
        alt.Chart(income_by_category_df)
        .mark_bar()
        .encode(
            alt.Y("categoria:N", sort="-x", axis=alt.Axis(title="")),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor", titlePadding=15, format="$,.2f", tickMinStep=5000
                ),
            ),
            color=alt.condition(
                alt.datum.position == 0,
                alt.value("#a7c52b"),
                alt.value("lightgray"),  ## higlight only top 3 expenses
            ),
        )
        .properties(width=1400, height=350)
        .configure_axis(
            labelFontSize=16, titleFontSize=20, titleColor="#a7c52b", grid=False
        )
    )

    st.markdown("***")

    st.markdown(
        f""" #### <b style='color:#a7c52b'>Repasse</b> por dia da semana<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.table(income_sum_by_weekday_df)
    st.dataframe(income_sum_by_weekday_df)
