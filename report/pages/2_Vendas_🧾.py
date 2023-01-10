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
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name(locale.getlocale())

    df["data"] = df["data"].dt.date

    df["quantidade"] = df["quantidade"].astype(int)

    # ## end-main df cleanup and enhancements

    # ## extract totals and relevant data

    total_sales_sum = df["valor_total"].sum(numeric_only=True)

    only_meals = (
        df[df["descricao"].str.contains("*", regex=False, na=True)].drop(
            labels=[
                "mes",
                "dia",
                "ano",
                "dia_semana",
            ],
            axis="columns",
        )
        # .sum()
    )

    delivery_totals = only_meals[
        only_meals["descricao"].str.contains("Delivery", regex=False)
    ].sum(numeric_only=True)

    in_place_delivery = only_meals[
        only_meals["descricao"].str.startswith("(Viagem")
    ].sum(numeric_only=True)

    in_place_meals = only_meals[
        ~(
            only_meals["descricao"].str.contains("Delivery")
            | only_meals["descricao"].str.startswith("(Viagem")
        )
    ].sum(numeric_only=True)

    only_meals_totals = only_meals.drop(
        labels=[
            "descricao",
        ],
        axis="columns",
    ).sum(numeric_only=True)

    # ## GROUPBY

    sales_by_item = (
        df.groupby("descricao", as_index=False)
        .sum(numeric_only=True)
        .drop(labels=["mes", "dia", "ano"], axis="columns")
    )

    top_15_sales_items_by_value = sales_by_item.nlargest(15, "valor_total")

    top_15_sales_items_by_value["position"] = range(
        1, len(top_15_sales_items_by_value) + 1
    )

    # ## TOPS DFS

    # top10_exp_df = (
    #     expenses_by_category_df.nlargest(10, "valor")
    #     .sort_values(by="valor", ascending=False)
    #     .assign(position=range(10))
    # )

    # print(df.head())
    # print(total_sales_sum)
    # print(sales_by_item)
    # print("#" * 99)
    # print(top_15_sales_items_by_value)
    # print("#" * 99)
    # print(only_meals)
    # print(only_meals_totals)
    # print(delivery_totals)
    # print(in_place_delivery)
    # print(in_place_meals)
    # print(df)
    # print(df.columns)
    # print(df.info())

    return (
        df,
        total_sales_sum,
        sales_by_item,
        top_15_sales_items_by_value,
        only_meals,
        only_meals_totals,
        in_place_meals,
        delivery_totals,
        in_place_delivery,
    )


st.set_page_config(layout="wide")

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
    (
        data,
        total_sales_sum,
        sales_by_item,
        top_15_sales_items_by_value,
        only_meals,
        only_meals_totals,
        in_place_meals,
        delivery_totals,
        in_place_delivery,
    ) = load_data(uploaded_file)

    st.balloons()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("A cara dos dados:"):
        st.write("(Linha,Colunas)", data.shape)
        st.dataframe(data)

    st.markdown(
        f""" ### <br> As <b style='color:#a7c52b'>Vendas</b> totais do período foi de <b style='color:#a7c52b;'>{locale.currency(total_sales_sum, grouping=True)}</b>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" #### <br> Sendo <b style='color:#a7c52b'>{locale.format_string('%.0f', only_meals_totals.loc['quantidade'], grouping=True, monetary=False)}</b> refeições no total.  :spaghetti:  :curry:<br>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" ##### - <b style='color:#a7c52b'>{int(in_place_meals['quantidade'])}</b> foram no Restaurante   :knife_fork_plate: <br>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f""" ##### - <b style='color:#a7c52b'>{locale.format_string('%.0f', delivery_totals.loc['quantidade'], grouping=True, monetary=False)}</b> foram nos deliveries (plataformas)  :motor_scooter:<br>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f""" ##### - <b style='color:#a7c52b'>{locale.format_string('%.0f', in_place_delivery.loc['quantidade'], grouping=True, monetary=False)}</b> foram refeições viagem no local :handbag:<br>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" #### <br><br> Top 15 <b style='color:#f19904'>Produtos</b> por valor (R$) <br><br>""",
        unsafe_allow_html=True,
    )

    top15_sales_by_value = (
        alt.Chart(top_15_sales_items_by_value)
        .mark_bar()
        .encode(
            alt.Y(
                "descricao:N",
                sort=alt.EncodingSortField("value", op="max", order="descending"),
                axis=alt.Axis(
                    title="",
                    labelPadding=10,
                    labelLimit=250,
                ),
            ),
            alt.X(
                "valor_total:Q",
                axis=alt.Axis(
                    title="R$ Valor", titlePadding=15, format="$,.2f", tickMinStep=5000
                ),
            ),
            color=alt.condition(
                alt.datum.position <= 5,
                alt.value("#f19904"),
                alt.value("lightgray"),  ## higlight only top 5 items
            ),
        )
        .properties(width=1400, height=600)
    )

    st.altair_chart(
        top15_sales_by_value.configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            titleColor="#f19904",
            grid=False,
        )
    )
