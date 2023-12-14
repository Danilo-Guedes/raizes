import streamlit as st
import pandas as pd

from utils.string_utils import prepare_column_name
from utils.date_util import weekday_map
from utils.locale_util import locale


@st.cache_data
def load_financial_data(file):
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

    df = df.rename(columns=prepare_column_name)
    df = df.rename(columns={"cliente/fornecedor": "fornecedor"})
    df["tipo"] = df["tipo"].map(lambda tp: "receita" if tp == "C" else "despesa")

    df["dia"] = df["data"].dt.day
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name(locale.getlocale()).astype("category")

    df["data"] = df["data"].dt.date

    # print(df.columns)
    # print(df.dtypes)

    df.assign(
        valor=df["valor"].round(2).astype("float16"),
        tipo=df["tipo"].astype("category"),
        fornecedor=df["fornecedor"].astype("category"),
        categoria=df["categoria"].astype("category"),
    )

    empty_category = df["categoria"].isna()
    df.loc[empty_category, "categoria"] = "Sem Categoria #v"
    ## end-main df cleanup and enhancements

    ## remove ! symbols
    df = df[df["categoria"].str.contains("!", regex=False, na=True) == False]

    ## extract totals and relevant data

    income_df = df.loc[df["tipo"] == "receita"]
    expenses_df = df.loc[df["tipo"] == "despesa"]

    fixes_expenses = expenses_df[expenses_df["categoria"].str.contains("#f")]

    variables_expenses = expenses_df[expenses_df["categoria"].str.contains("#v")]

    ## GROUPBY
    income_by_category_df = (
        income_df.groupby("categoria", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
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
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    income_sum_by_day_df = (
        income_df.groupby("data", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    expenses_sum_by_weekday_df = (
        expenses_df.groupby("dia_semana", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    expenses_sum_by_day_df = (
        expenses_df.groupby("data", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    expenses_sum_by_supplier = (
        expenses_df.groupby("fornecedor", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    supplier_expenses_counts = (
        expenses_df.groupby("fornecedor")
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    fixes_expenses_by_category = (
        fixes_expenses.groupby("categoria", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )

    variables_expenses_by_category = (
        variables_expenses.groupby("categoria", as_index=False)
        .sum(numeric_only=True)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
            ],
            axis="columns",
        )
        .sort_values(by="valor", ascending=False)
    )
    ## ADDING DAYWEEK COLUMN

    income_sum_by_day_df["dia_semana"] = income_sum_by_day_df["data"].apply(
        lambda x: weekday_map[x.weekday()]
    )

    expenses_sum_by_day_df["dia_semana"] = expenses_sum_by_day_df["data"].apply(
        lambda x: weekday_map[x.weekday()]
    )

    ## ADDING PERCENTAGE COLUMN

    income_sum_by_weekday_df["percentage"] = income_sum_by_weekday_df["valor"].apply(
        lambda x: str(round(x / income_sum_by_weekday_df["valor"].sum() * 100, 2))
        + " %"
    )

    expenses_sum_by_weekday_df["percentage"] = expenses_sum_by_weekday_df[
        "valor"
    ].apply(
        lambda x: str(round(x / expenses_sum_by_weekday_df["valor"].sum() * 100, 2))
        + " %"
    )

    # ADDING TOTAL LAST LINE
    income_sum_by_weekday_df.loc[len(income_sum_by_weekday_df)] = [
        "Total",
        income_sum_by_weekday_df["valor"].sum(),
        "100.00 %",
    ]
    expenses_sum_by_weekday_df.loc[len(expenses_sum_by_weekday_df)] = [
        "Total",
        expenses_sum_by_weekday_df["valor"].sum(),
        "100.00 %",
    ]

    ## RESETING INDEXES AND POSITION COLUMN

    income_sum_by_weekday_df.reset_index(drop=True, inplace=True)
    income_sum_by_day_df.reset_index(drop=True, inplace=True)
    expenses_sum_by_day_df.reset_index(drop=True, inplace=True)
    expenses_sum_by_supplier.reset_index(drop=True, inplace=True)

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
                "mes",
                "ano",
            ],
            axis="columns",
        )
    )

    ## TOPS DFS

    top15_exp_df = (
        expenses_by_category_df.nlargest(15, "valor")
        .sort_values(by="valor", ascending=False)
        .assign(position=range(15))
    )

    supplier_to_exclude = [
        "GABRIELA RUSSI ZAMBONI",
        "DANILO PAZ GUEDES DE FREITAS",
        "DANILO BALDARENA FRANZA",
        "ADRIELLE BORSARINI RIBEIRO",
        "FERNANDO CARRIÃO",
    ]

    top15_exp_df_by_supplier = (
        expenses_sum_by_supplier[
            ~expenses_sum_by_supplier["fornecedor"].isin(supplier_to_exclude)
        ]
        .nlargest(15, "valor")
        .sort_values(by="valor", ascending=False)
        .assign(position=range(15))
    )

    top_15_supplier_expenses_counts = supplier_expenses_counts.nlargest(
        15, "count"
    ).assign(position=range(15))

    top_10_fixes_expenses = (
        fixes_expenses_by_category.nlargest(10, "valor")
        .sort_values(by="valor", ascending=False)
        .assign(position=range(1, 11))
    )

    top_10_variables_expenses = (
        variables_expenses_by_category.nlargest(10, "valor")
        .sort_values(by="valor", ascending=False)
        .assign(position=range(1, 11))
    )

    top_15_higher_single_values_expenses = (
        expenses_df[~expenses_df["fornecedor"].isin(supplier_to_exclude)]
        .nlargest(15, "valor")
        .sort_values(by="valor", ascending=False)
        .drop(
            labels=[
                "id",
                "dia",
                "mes",
                "ano",
                "dia_semana",
                "banco",
                "tipo"
            ],
            axis="columns",
        )
        .assign(position=range(1, 16))
        .assign(position_with_name=lambda x: x["position"].astype(str) + " " + x["fornecedor"])
    )

    # SET VALUES TO CURRENCY

    income_sum_by_weekday_df["valor"] = income_sum_by_weekday_df["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )

    income_sum_by_day_df["valor"] = income_sum_by_day_df["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )

    expenses_sum_by_weekday_df["valor"] = expenses_sum_by_weekday_df["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )

    expenses_sum_by_day_df["valor"] = expenses_sum_by_day_df["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )

    expenses_sum_by_supplier["valor"] = expenses_sum_by_supplier["valor"].apply(
        lambda x: locale.currency(x, grouping=True)
    )

    return (
        df,
        income_df,
        expenses_df,
        income_by_category_df,
        expenses_by_category_df,
        top15_exp_df,
        income_sum_by_weekday_df,
        income_sum_by_day_df,
        expenses_sum_by_weekday_df,
        expenses_sum_by_day_df,
        expenses_sum_by_supplier,
        top15_exp_df_by_supplier,
        top_15_supplier_expenses_counts,
        top_10_fixes_expenses,
        top_10_variables_expenses,
        top_15_higher_single_values_expenses,
    )
