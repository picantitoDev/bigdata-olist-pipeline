"""Ventas y Clientes — ingresos geográficos, retención, métodos de pago."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import REVENUE_POR_ESTADO, RETENCION_CLIENTES, METODOS_PAGO
from utils.charts import bar_chart, pie_chart

st.set_page_config(page_title="Ventas y Clientes", page_icon="📊", layout="wide")
st.title("📊 Ventas y Clientes")

# ------------------------------------------------------------------ Estados
estados = run_query(REVENUE_POR_ESTADO)

st.subheader("Ingresos por estado")
col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(
        bar_chart(estados.head(15), "customer_state", "revenue",
                  "Top 15 estados por ingresos", color="revenue"),
        use_container_width=True,
    )

with col_r:
    sp = estados.iloc[0]
    pct_sp = sp["revenue"] / estados["revenue"].sum() * 100
    st.metric("Estado líder", sp["customer_state"], f"{pct_sp:.1f}% de los ingresos totales")
    st.metric("Mayor ingreso por orden",
              estados.sort_values("revenue_per_order", ascending=False).iloc[0]["customer_state"],
              f"R$ {estados['revenue_per_order'].max():,.2f}")
    st.markdown(
        "**Insight:** São Paulo concentra la mayor parte del negocio, "
        "pero estados del norte tienen tickets promedio más altos — "
        "el costo logístico eleva el valor mínimo de compra que justifica el envío."
    )

st.divider()

# ------------------------------------------------------------------ Retención
retencion = run_query(RETENCION_CLIENTES)

st.subheader("Retención de clientes")
col_l, col_r = st.columns([1, 2])

with col_l:
    st.plotly_chart(
        pie_chart(retencion, "segment", "customers", "Clientes por tipo"),
        use_container_width=True,
    )

with col_r:
    una = retencion[retencion["segment"] == "Una compra"].iloc[0]
    rec = retencion[retencion["segment"] == "Recurrente (2+)"].iloc[0]
    total = una["customers"] + rec["customers"]

    st.metric("Clientes de una sola compra",
              f"{una['customers']:,} ({una['customers']/total*100:.1f}%)")
    st.metric("LTV promedio recurrentes vs únicos",
              f"R$ {rec['avg_ltv']:,.2f}",
              f"+{(rec['avg_ltv']/una['avg_ltv']-1)*100:.0f}% vs una compra")
    st.markdown(
        "**Insight accionable:** la retención es el mayor problema del negocio. "
        "Un cliente recurrente vale significativamente más — cada punto porcentual "
        "de mejora en retención tiene impacto directo en los ingresos. "
        "Ver página **Segmentación IA** para las campañas recomendadas por segmento."
    )

st.divider()

# ------------------------------------------------------------------ Pagos
pagos = run_query(METODOS_PAGO)

st.subheader("Métodos de pago")
col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(
        bar_chart(pagos, "payment_type", "total_value", "Valor total por método de pago"),
        use_container_width=True,
    )

with col_r:
    cc = pagos[pagos["payment_type"] == "credit_card"]
    if not cc.empty:
        st.metric("Cuotas promedio (tarjeta de crédito)",
                  f"{cc.iloc[0]['avg_installments']:.1f}")
    st.markdown(
        "**Insight:** tarjeta de crédito domina y el uso intensivo de cuotas "
        "(~3 en promedio) refleja el hábito de pago brasileño — cualquier fricción "
        "en el financiamiento impacta la conversión directamente."
    )
