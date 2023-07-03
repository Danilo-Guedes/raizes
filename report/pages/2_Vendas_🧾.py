from time import timezone
import pandas as pd
import streamlit as st
import locale
import altair as alt
import numpy as np

from utils.string_utils import prepare_column_name


locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


@st.cache_data
def load_data(file):
    ##util_fns

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

    df = df.rename(columns=prepare_column_name)

    df["dia"] = df["data"].dt.day
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name(locale.getlocale())
    df["num_dia_semana"] = df["data"].dt.weekday
    df["num_semana"] = df["data"].dt.isocalendar().week.astype(int)

    df["data"] = df["data"].dt.date

    df["quantidade"] = df["quantidade"].astype(int)

    # ## end-main df cleanup and enhancements

    # ## extract totals and relevant data

    total_sales_sum = df["valor_total"].sum(numeric_only=True)

    only_meals = (
        df[df["descricao"].str.contains("*", regex=False, na=True)].drop(
            labels=["mes", "dia", "ano", "dia_semana", "num_semana", "num_dia_semana"],
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

    sales_by_weekday_df = (
        df.groupby("dia_semana", as_index=False)
        .sum(numeric_only=True)
        .sort_values("valor_total", ascending=False)
    )

    sales_by_date_df = (
        df.groupby(["num_dia_semana", "dia_semana", "num_semana"], as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "quantidade",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
    ).sort_values("num_dia_semana")


    #PIVOT TABLE
    sales_by_weekday_pivot = pd.pivot_table(
        data=sales_by_date_df,
        values="valor_total",
        index="num_semana",
        columns="dia_semana",
        aggfunc="sum",
        fill_value=0.00,
        margins=True,
        margins_name="Total",
        sort=False,
    )


    sales_by_weekday_pivot.index = sales_by_weekday_pivot.index.astype(str)
    sales_by_weekday_pivot = sales_by_weekday_pivot.sort_index(ascending=True)

    

    # REMOVING UNNECESSARY COLUMN

    sales_by_weekday_df = sales_by_weekday_df.drop(
        labels=["dia", "quantidade", "num_semana", "mes", "ano", "num_dia_semana"],
        axis="columns",
    )

    ## ADDING PERCENTAGE COLUMN
    sales_by_weekday_df["percentage"] = sales_by_weekday_df["valor_total"].apply(
        lambda x: str(round(x / sales_by_weekday_df["valor_total"].sum() * 100, 2))
        + " %"
    )
    # ADDING TOTAL LAST LINE
    sales_by_weekday_df.loc[len(sales_by_weekday_df)] = [
        "Total",
        sales_by_weekday_df["valor_total"].sum(),
        "100.00 %",
    ]

    # SET VALUES TO CURRENCY

    sales_by_weekday_df["valor_total"] = sales_by_weekday_df["valor_total"].apply(
        lambda x: locale.currency(x, grouping=True)
    )
    sales_by_weekday_pivot = sales_by_weekday_pivot.applymap(
        lambda x: locale.currency(x, grouping=True)
    )

    # ## TOPS DFS

    top_15_sales_items_by_value = sales_by_item.nlargest(15, "valor_total").assign(
        position=range(1, 16)
    )

    top_15_sales_items_by_qtd = sales_by_item.nlargest(15, "quantidade").assign(
        position=range(1, 16)
    )

    # top10_exp_df = (
    #     expenses_by_category_df.nlargest(10, "valor")
    #     .sort_values(by="valor", ascending=False)
    #     .assign(position=range(10))
    # )

    # print(df.head())
    # print(df.columns)
    # print(total_sales_sum)
    # print(sales_by_item)
    # print("#" * 99)
    # print(top_15_sales_items_by_value)
    # print(top_15_sales_items_by_qtd)
    # print("#" * 99)
    # print(only_meals)
    # print(only_meals_totals)
    # print(delivery_totals)
    # print(in_place_delivery)
    # print(in_place_meals)
    # print(df)
    # print(df.columns)
    # print(df.info())
    # print(sales_by_weekday_df)
    # print(sales_by_weekday_pivot)

    return (
        df,
        total_sales_sum,
        sales_by_item,
        top_15_sales_items_by_value,
        top_15_sales_items_by_qtd,
        only_meals,
        only_meals_totals,
        in_place_meals,
        delivery_totals,
        in_place_delivery,
        sales_by_weekday_df,
        sales_by_weekday_pivot,
    )


st.set_page_config(layout="wide")

# st.markdown(
#     """
#  ### Análise de Vendas"""
# )
# data.dtypes

st.header("Análise de Vendas")
st.divider()

uploaded_file = st.file_uploader(
    label="Importe o relatório de **:green[VENDAS]** do ERP bling no formato **CSV**",
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
        top_15_sales_items_by_qtd,
        only_meals,
        only_meals_totals,
        in_place_meals,
        delivery_totals,
        in_place_delivery,
        sales_by_weekday_df,
        sales_by_weekday_pivot,
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
                    labelLimit=300,
                ),
            ),
            alt.X(
                "valor_total:Q",
                axis=alt.Axis(
                    title="R$ Valor",
                    titlePadding=15,
                    format="$,.2f",
                    tickMinStep=5000,
                    tickOffset=50,
                ),
            ),
            color=alt.condition(
                alt.datum.position <= 5,
                alt.value("#f19904"),
                alt.value("	darkgray"),  ## higlight only top 5 items
            ),
            tooltip=["valor_total", "quantidade", "descricao"],
        )
        .properties(width=1700, height=600)
    )

    label_top15_sales_by_value = top15_sales_by_value.mark_text(
        align="left",
        baseline="middle",
        dx=5,  # Nudges text to right so it doesn't appear on top of the bar
        fontSize=16,
    ).encode(text=alt.Text("valor_total:Q", format="$,.2f", formatType="number"))

    st.altair_chart(
        (top15_sales_by_value + label_top15_sales_by_value).configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            titleColor="#f19904",
            grid=False,
        )
    )

    st.markdown(
        f""" #### <br><br> Top 15 <b style='color:#f19904'>Produtos</b> por unidades vendidas<br><br>""",
        unsafe_allow_html=True,
    )

    top15_sales_by_qtd = (
        alt.Chart(top_15_sales_items_by_qtd)
        .mark_bar()
        .encode(
            alt.X(
                "descricao:N",
                sort=alt.EncodingSortField("value", op="max", order="descending"),
                axis=alt.Axis(title="", labelPadding=20, labelAngle=-30),
            ),
            alt.Y(
                "quantidade:Q",
                axis=alt.Axis(
                    title="Unidades Vendidas",
                    titlePadding=15,
                    labels=False,
                ),
            ),
            color=alt.condition(
                alt.datum.position <= 5,
                alt.value("#f19904"),
                alt.value("	darkgray"),  ## higlight only top 5 items
            ),
            tooltip=["valor_total", "quantidade", "descricao"],
        )
        .properties(width=1600, height=500)
    )

    label_top15_sales_by_qtd = top15_sales_by_qtd.mark_text(
        align="center",
        baseline="bottom",
        fontSize=18,
    ).encode(text=alt.Text("quantidade:Q", formatType="number"))

    st.altair_chart(
        (top15_sales_by_qtd + label_top15_sales_by_qtd).configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            titleColor="#f19904",
            grid=False,
        )
    )

    st.divider()

    st.markdown(
        f""" #### <b style='color:#a7c52b'>Vendas</b> por dia do mes<br><br>
        """,
        unsafe_allow_html=True,
    )
    st.table(sales_by_weekday_df)

    st.subheader("Visão de Calendário")
    st.table(sales_by_weekday_pivot)
