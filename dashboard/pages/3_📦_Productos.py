"""Productos — categorías, estrategia volumen vs ticket, costos de envío."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import TOP_CATEGORIAS, FREIGHT_VS_PESO
from utils.charts import bar_chart, scatter_chart

st.set_page_config(page_title="Productos", page_icon="📦", layout="wide")
st.title("📦 Análisis de Productos")

# ------------------------------------------------------------------ Top categorías
cats = run_query(TOP_CATEGORIAS)

st.subheader("Top categorías por ingresos")
st.plotly_chart(
    bar_chart(cats.head(15), "product_category", "product_revenue",
              "Top 15 categorías", color="product_revenue"),
    use_container_width=True,
)

st.divider()

# ------------------------------------------------------------------ Volumen vs ticket
st.subheader("Matriz estratégica: volumen vs precio promedio")

col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(
        scatter_chart(
            cats, "items_sold", "avg_price", "product_revenue", "product_category",
            "Unidades vendidas vs precio promedio (tamaño = ingresos)",
            "Unidades vendidas", "Precio promedio (R$)",
        ),
        use_container_width=True,
    )

with col_r:
    vol = cats.sort_values("items_sold", ascending=False).iloc[0]
    ticket = cats.sort_values("avg_price", ascending=False).iloc[0]
    st.metric("Categoría de volumen", vol["product_category"],
              f"{vol['items_sold']:,} unidades")
    st.metric("Categoría premium", ticket["product_category"],
              f"R$ {ticket['avg_price']:,.2f} promedio")
    st.markdown(
        "**Insight:** coexisten dos estrategias ganadoras. Las categorías "
        "de volumen (bed_bath_table) generan ingresos por cantidad; las premium "
        "(watches_gifts) por ticket. El presupuesto de marketing rinde más "
        "en las premium: cada conversión vale ~2x el promedio."
    )

st.divider()

# ------------------------------------------------------------------ Freight
st.subheader("Costo de envío vs peso por categoría")

freight = run_query(FREIGHT_VS_PESO)

st.plotly_chart(
    scatter_chart(
        freight, "avg_weight_kg", "avg_freight", "items", "product_category",
        "Peso promedio vs flete promedio (tamaño = unidades)",
        "Peso promedio (kg)", "Flete promedio (R$)",
    ),
    use_container_width=True,
)
st.caption(
    "El flete escala con el peso como se espera, pero las categorías que se "
    "desvían por encima de la tendencia son candidatas a renegociación con transportistas "
    "o a un ajuste del precio de envío al cliente."
)
