from time import timezone
import streamlit as st
import altair as alt
import numpy as np

from services.finance import load_financial_data
from config import colors
from utils.locale_util import locale

st.set_page_config(layout="wide")


st.header("Análise Financeira")
st.divider()


uploaded_file = st.file_uploader(
    label="Importe o extrato **:green[Financeiro]** no ERP Bling np formato **CSV**",
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
    ) = load_financial_data(uploaded_file)

    st.balloons()

    

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("A cara dos dados:"):
        st.write("(Linha,Colunas)", data.shape)
        st.dataframe(data)

    st.markdown(
        f""" #### <br> O total de <b style='color:{colors.light_green}'>Receitas</b> do período foi de <b style='color:{colors.light_green};'>{locale.currency(income_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f""" #### O total de <b style='color:{colors.orange}'>Despesas</b> do período foi de <b style='color:{colors.orange}'>{locale.currency(expenses_df['valor'].sum(), grouping=True)}</b>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f""" ##### O resultado bruto (rec - des) foi de <b style='color:{colors.dark_green};font-size:26px;text-decoration:underline;'>{locale.currency(income_df['valor'].sum() - expenses_df['valor'].sum(), grouping=True)}</b>.<br>""",
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        f""" #### Top 15  <b style='color:{colors.orange}'>Despesas</b> por categoria + (%) <br><br>
        """,
        unsafe_allow_html=True,
    )

    top15_exp_df = (
        alt.Chart(top15_exp_df)
        .mark_bar()
        .encode(
            alt.Y(
                "categoria:N",
                sort=alt.EncodingSortField("value", op="max", order="descending"),
                axis=alt.Axis(title=None),
            ),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor", titlePadding=15, format="$,.2f", tickMinStep=1000
                ),
            ),
            color=alt.condition(
                alt.datum.position < 3,
                alt.value(colors.orange),
                alt.value(colors.light_gray),  ## higlight only top 3 expenses
            ),
        )
        .properties(height=900)
    )

    label_top10_expenses = (
        top15_exp_df.mark_text(
            align="right",
            baseline="middle",
            fontSize=20,
            fontWeight=600,
        )
        .encode(
            text=alt.Text("percentage:Q", format=".2%"), color=alt.value(colors.white)
        )
        .transform_calculate(percentage=f"datum.valor / {expenses_df['valor'].sum()}")
    )

    st.altair_chart(
        (top15_exp_df + label_top10_expenses).configure_axis(
            labelFontSize=16, titleFontSize=20, titleColor=colors.orange, grid=False
        ),
        use_container_width=True,
    )

    st.divider()

    st.markdown(
        f""" #### <b style='color:{colors.light_green}'>Receitas</b> por categoria<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.altair_chart(
        alt.Chart(income_by_category_df)
        .mark_bar()
        .encode(
            alt.Y("categoria:N", sort="-x", axis=alt.Axis(title=None)),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor", titlePadding=15, format="$,.2f", tickMinStep=5000
                ),
            ),
            color=alt.condition(
                alt.datum.position == 0,  ## higlight only top expense
                alt.value(colors.light_green),
                alt.value(colors.light_gray),
            ),
        )
        .properties(height=350)
        .configure_axis(labelFontSize=16, titleFontSize=20, grid=False),
        use_container_width=True,
    )

    st.divider()

    st.markdown(
        f""" #### A média de <b style='color:{colors.light_green}'>Repasse</b> por dia foi de {locale.currency(income_df['valor'].sum() / len(income_sum_by_day_df), grouping=True) } (o período teve {len(income_sum_by_day_df)} dias com ocorrências)<br>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        f""" #### <b style='color:{colors.light_green}'>Repasse</b> por dia da semana<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.table(income_sum_by_weekday_df)

    st.divider()

    st.markdown(
        f""" #### <b style='color:{colors.light_green}'>Receitas</b> por dia do mes<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.table(income_sum_by_day_df)

    st.divider()

    st.markdown(
        f""" #### A média de <b style='color:{colors.orange}'>Despesas</b> por dia foi de {locale.currency(expenses_df['valor'].sum() / len(expenses_sum_by_day_df), grouping=True) } (o período teve {len(expenses_sum_by_day_df)} dias com ocorrências)<br>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        f""" #### <b style='color:{colors.orange}'>Despesas</b> por dia da semana<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.table(expenses_sum_by_weekday_df)

    st.divider()

    st.markdown(
        f""" #### <b style='color:{colors.orange}'>Despesas</b> por dia do mes<br><br>
        """,
        unsafe_allow_html=True,
    )

    st.table(expenses_sum_by_day_df)

    st.divider()

    st.markdown(
        f""" ## Análise <b style='color:{colors.orange}'>Fornecedores</b><br><br>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "15 maiores Fornecedores por Valor R$",
    )

    top10_expenses_by_supplier = (
        alt.Chart(top15_exp_df_by_supplier)
        .mark_bar()
        .encode(
            alt.Y(
                "fornecedor:N",
                sort=alt.EncodingSortField("valor", op="max", order="descending"),
                axis=alt.Axis(title=None),
            ),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor",
                    titlePadding=15,
                    format="$,.2f",
                ),
            ),
            color=alt.condition(
                alt.datum.position < 3,
                alt.value(colors.orange),
                alt.value(colors.light_gray),  ## higlight only top 3 expenses
            ),
        )
        .properties(height=900)
    )

    label_top10_expenses_by_supplier = (
        top10_expenses_by_supplier.mark_text(
            align="right",
            baseline="middle",
            fontSize=24,
            fontWeight=600,
        ).encode(
            text=alt.Text("valor:Q", format="$,.2f"), color=alt.value(colors.white)
        )
        # .transform_calculate(percentage=f"datum.valor / {expenses_df['valor'].sum()}")
    )

    st.altair_chart(
        (top10_expenses_by_supplier + label_top10_expenses_by_supplier).configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            grid=False,
            # labelAlign="right"
        ),
        # .configure_view(stroke=None, clip=False)
        use_container_width=True,
    )

    st.divider()

    st.subheader("15 maiores Fornecedores por ocorrências")

    top_15_by_occurrence = (
        alt.Chart(top_15_supplier_expenses_counts)
        .mark_bar()
        .encode(
            alt.Y(
                "count:Q",
                axis=alt.Axis(title=None, labels=False),
            ),
            alt.X(
                "fornecedor:N",
                sort=alt.EncodingSortField("count", op="max", order="descending"),
                axis=alt.Axis(
                    title=None, labelAngle=25, labelFontSize=18, labelBaseline="top"
                ),
            ),
            color=alt.condition(
                alt.datum.position < 3,
                alt.value(colors.orange),
                alt.value(colors.light_gray),  ## higlight only top 3 expenses
            ),
        )
        .properties(height=600)
    )
    label_top_15_by_occurrence = top_15_by_occurrence.mark_text(
        align="center",
        baseline="top",
        fontSize=30,
        fontWeight=600,
    ).encode(text=alt.Text("count:Q"), color=alt.value(colors.white))

    st.altair_chart(
        top_15_by_occurrence + label_top_15_by_occurrence,
        use_container_width=True,
    )

    st.divider()
    
    st.subheader("10 maiores despesas fixas")


    top10_variables_expenses = (
        alt.Chart(top_10_fixes_expenses)
        .mark_bar()
        .encode(
            alt.Y(
                "categoria:N",
                sort=alt.EncodingSortField("valor", op="max", order="descending"),
                axis=alt.Axis(title=None),
            ),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor",
                    titlePadding=15,
                    format="$,.2f",
                ),
            ),
            color=alt.condition(
                alt.datum.position <= 3,
                alt.value(colors.orange),
                alt.value(colors.light_gray),  ## higlight only top 3 expenses
            ),
        )
        .properties(height=900)
    )

    label_top10_variabless_expenses = (
        top10_variables_expenses.mark_text(
            align="right",
            baseline="middle",
            fontSize=24,
            fontWeight=600,
        ).encode(
            text=alt.Text("valor:Q", format="$,.2f"), color=alt.value(colors.white)
        )
        # .transform_calculate(percentage=f"datum.valor / {expenses_df['valor'].sum()}")
    )

    st.altair_chart(
        (top10_variables_expenses + label_top10_variabless_expenses).configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            grid=False,
            # labelAlign="right"
        ),
        # .configure_view(stroke=None, clip=False)
        use_container_width=True,
    )

    
    st.divider()

    st.subheader("10 maiores despesas variáveis")


    top10_variables_expenses = (
        alt.Chart(top_10_variables_expenses)
        .mark_bar()
        .encode(
            alt.Y(
                "categoria:N",
                sort=alt.EncodingSortField("valor", op="max", order="descending"),
                axis=alt.Axis(title=None),
            ),
            alt.X(
                "valor:Q",
                axis=alt.Axis(
                    title="R$ Valor",
                    titlePadding=15,
                    format="$,.2f",
                ),
                scale=alt.Scale(type="log" , base=10, domain=[300,40_000])
            ),
            color=alt.condition(
                alt.datum.position <= 3,
                alt.value(colors.orange),
                alt.value(colors.light_gray),  ## higlight only top 3 expenses
            ),
        )
        .properties(height=900)
    )

    label_top10_variabless_expenses = (
        top10_variables_expenses.mark_text(
            align="right",
            baseline="middle",
            fontSize=24,
            fontWeight=600,
        ).encode(
            text=alt.Text("valor:Q", format="$,.2f"), color=alt.value(colors.white)
        )
        # .transform_calculate(percentage=f"datum.valor / {expenses_df['valor'].sum()}")
    )

    st.altair_chart(
        (top10_variables_expenses + label_top10_variabless_expenses).configure_axis(
            labelFontSize=16,
            titleFontSize=20,
            grid=False,
            # labelAlign="right"
        ),
        # .configure_view(stroke=None, clip=False)
        use_container_width=True,
    )



