"""Olist Analytics Platform — Executive Summary."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import KPIS_GLOBALES, NPS_APROXIMADO, REVENUE_MENSUAL
from utils.charts import line_chart, fmt_money

st.title("📈 Olist Analytics Platform")
st.caption("E-commerce brasileño · dlt → Spark → BigQuery → dbt")

# ------------------------------------------------------------------ KPIs
kpis = run_query(KPIS_GLOBALES)
nps = run_query(NPS_APROXIMADO)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ingresos totales", fmt_money(kpis["total_revenue"][0]))
c2.metric("Órdenes", f"{kpis['total_orders'][0]:,}")
c3.metric("Ticket promedio", f"R$ {kpis['avg_order_value'][0]:,.2f}")
c4.metric("Clientes", f"{kpis['total_customers'][0]:,}")
c5.metric("Reseñas positivas", f"{nps['pct_positive'][0]}%",
          help="Porcentaje de reseñas con puntaje 4 o 5")

st.divider()

# ------------------------------------------------------------------ Tendencia
monthly = run_query(REVENUE_MENSUAL)

col_l, col_r = st.columns(2)

with col_l:
    st.plotly_chart(
        line_chart(monthly, "year_month", "revenue",
                   "Evolución mensual de ingresos", "Ingresos (R$)"),
        use_container_width=True,
    )

with col_r:
    st.plotly_chart(
        line_chart(monthly, "year_month", "orders",
                   "Evolución mensual de órdenes", "Órdenes"),
        use_container_width=True,
    )

# ------------------------------------------------------------------ Hallazgos
st.subheader("Hallazgos clave")
st.markdown(
    """
| # | Insight | Página con evidencia |
|---|---|---|
| 1 | El crecimiento 2017→2018 fue sostenido, con pico en nov-2017 (Black Friday) | Esta página |
| 2 | ~97% de los clientes compran **una sola vez** — la retención es el mayor problema del negocio | Ventas y Clientes |
| 3 | Las demoras de entrega **destruyen el puntaje de reseñas**: de ~4.3 a ~1.7 estrellas | Logística |
| 4 | Dos estrategias de categoría coexisten: volumen (bed_bath_table) y ticket alto (watches_gifts) | Productos |
| 5 | 4 segmentos accionables de clientes identificados vía K-Means sobre RFM | Segmentación IA |
"""
)

