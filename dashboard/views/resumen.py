"""Olist Analytics Platform — Executive Summary."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import (
    KPIS_GLOBALES, NPS_APROXIMADO, REVENUE_MENSUAL,
    ESTADO_CRECIMIENTO_ALERTAS, RFM_BASE, q_kpis_logistica,
)
from utils.charts import line_chart, ranking_hbar, fmt_money, insight, con_nombres_estado
from utils.ml import segment_customers

FULL_RANGE = ("2016-09-01", "2018-10-31")

st.title("📈 Olist Analytics Platform")
st.caption("E-commerce brasileño · dlt → Spark → BigQuery → dbt")

# ------------------------------------------------------------------ Indicadores generales
kpis = run_query(KPIS_GLOBALES)
nps = run_query(NPS_APROXIMADO)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Ingresos totales",   fmt_money(kpis["total_revenue"][0]))
c2.metric("Pedidos totales",    f"{kpis['total_orders'][0]:,}")
c3.metric("Clientes únicos",    f"{kpis['total_customers'][0]:,}")
c4.metric("Ticket promedio",    f"R$ {kpis['avg_order_value'][0]:,.2f}")
c5.metric("Tasa de recompra",   f"{kpis['tasa_recompra'][0]}%",
          help="Porcentaje de clientes que hicieron 2 o más pedidos")
c6.metric("Reseñas positivas",  f"{nps['pct_positive'][0]}%",
          help="Porcentaje de reseñas con puntaje 4 o 5")

st.divider()

# ------------------------------------------------------------------ Tendencia
st.subheader("Evolución mensual del negocio")

monthly = run_query(REVENUE_MENSUAL)

col_l, col_r = st.columns(2)

with col_l:
    st.plotly_chart(
        line_chart(monthly, "year_month", "revenue",
                   "Ingresos mensuales", "Ingresos (R$)"),
        use_container_width=True,
    )
    insight(
        "Cuánto dinero entró cada mes por ventas. La tendencia general muestra "
        "cómo ha ido creciendo el negocio a lo largo del tiempo, con picos en "
        "fechas comerciales como noviembre (Black Friday)."
    )

with col_r:
    st.plotly_chart(
        line_chart(monthly, "year_month", "orders",
                   "Pedidos mensuales", "Pedidos"),
        use_container_width=True,
    )
    insight(
        "Cuántos pedidos se hicieron cada mes. Comparado con el gráfico de "
        "ingresos, permite ver si el crecimiento viene de más clientes "
        "comprando o de que cada pedido vale más en promedio."
    )

st.divider()

# ------------------------------------------------------------------ Estado general: crecimiento con alertas
st.subheader("Panorama por estado: ingresos y alertas logísticas")

estado_df = run_query(ESTADO_CRECIMIENTO_ALERTAS)
avg_tardias = (estado_df["pct_tardias"] * estado_df["ordenes"]).sum() / estado_df["ordenes"].sum()
estado_df["alerta"] = estado_df["pct_tardias"] > avg_tardias
estado_df = con_nombres_estado(estado_df, "estado")

col_est, col_alert = st.columns([3, 2])

with col_est:
    top10 = estado_df.sort_values("ingresos", ascending=False).head(10)
    st.plotly_chart(
        ranking_hbar(top10, "ingresos", "estado", "", height=420),
        use_container_width=True,
    )
    insight(
        "Los 10 estados que más ingresos generan en todo el período. Es la "
        "base del negocio: dónde está concentrada la demanda."
    )

with col_alert:
    st.markdown("**⚠️ Estados en alerta logística**")
    st.caption(f"Estados con % de entregas tardías por encima del promedio nacional ({avg_tardias:.1f}%)")
    alertas = estado_df[estado_df["alerta"]].sort_values("pct_tardias", ascending=False)
    if alertas.empty:
        st.success("Ningún estado supera el promedio nacional de retrasos.")
    else:
        for _, r in alertas.head(6).iterrows():
            st.markdown(f"- **{r['estado']}** — {r['pct_tardias']}% de órdenes tardías "
                        f"({fmt_money(r['ingresos'])} en ingresos expuestos)")
    insight(
        "Un estado 'en alerta' vende bien pero entrega mal: ese riesgo logístico "
        "puede terminar dañando la reputación y la retención de esos clientes."
    )

st.divider()

# ------------------------------------------------------------------ Segmentación de clientes (K-Means)
st.subheader("Oportunidad comercial por segmentos")

rfm = run_query(RFM_BASE)
df_seg, summary = segment_customers(rfm)

total_clientes = summary["customers"].sum()
total_valor = summary["total_value"].sum()

at_risk = summary[summary["segment_name"] == "At Risk"].iloc[0]
top_valor_seg = summary[summary["segment_name"].isin(["Champions", "Loyal"])]

pct_at_risk = 100 * at_risk["customers"] / total_clientes
pct_top_clientes = 100 * top_valor_seg["customers"].sum() / total_clientes
pct_top_valor = 100 * top_valor_seg["total_value"].sum() / total_valor

s1, s2, s3 = st.columns(3)

with s1:
    st.metric("🎯 Segmento prioritario", f"{pct_at_risk:.1f}%", "de los clientes está en At Risk",
               delta_color="off")
    st.caption(
        "Es el grupo más numeroso de la base de clientes y requiere una "
        "estrategia de reactivación."
    )

with s2:
    st.metric("💰 Clientes de mayor valor", f"{pct_top_valor:.1f}% del valor",
               f"con solo {pct_top_clientes:.1f}% de los clientes", delta_color="off")
    st.caption(
        "Champions y Loyal son una porción reducida de la base, pero "
        "concentran una parte considerable del valor total generado."
    )

with s3:
    st.metric("🚀 Acción prioritaria", "Reactivar y proteger", delta_color="off")
    st.caption(
        "Reactivar a los clientes At Risk y proteger a los segmentos de mayor "
        "valor: aplicar campañas diferenciadas de reactivación, fidelización "
        "y venta cruzada según el perfil identificado."
    )

insight(
    "Vista ejecutiva de la oportunidad comercial: dónde está el mayor riesgo "
    "(At Risk), dónde está concentrado el valor (Champions + Loyal) y qué "
    "acción tomar. El detalle completo por segmento — clientes, valor "
    "individual, centroides RFM y campañas recomendadas — está disponible en "
    "Segmentación IA."
)

st.divider()

# ------------------------------------------------------------------ Riesgo logístico
st.subheader("Riesgo logístico: cómo afecta el retraso a la satisfacción")

log_k = run_query(q_kpis_logistica(FULL_RANGE, ())).iloc[0]

r1, r2 = st.columns(2)
r1.metric("Calificación en entregas puntuales", f"{log_k['score_a_tiempo']} ⭐",
          help="Score promedio de reseña cuando la orden llega a tiempo o antes")
r2.metric("Calificación en entregas con +15 días de retraso", f"{log_k['score_muy_tarde']} ⭐",
          f"-{log_k['score_a_tiempo'] - log_k['score_muy_tarde']:.2f} vs. a tiempo",
          delta_color="inverse")
insight(
    "Muestra el costo real del retraso en la percepción del cliente: cuando la "
    "entrega llega puntual, la calificación es alta; cuando se retrasa más de "
    "15 días, cae drásticamente. Ese es el mayor riesgo logístico del negocio."
)

st.divider()

# ------------------------------------------------------------------ Hallazgos
st.subheader("Hallazgos clave")
st.markdown(
    """
| # | Insight | Página con evidencia |
|---|---|---|
| 1 | El crecimiento 2017→2018 fue sostenido, con pico en nov-2017 (Black Friday) | Esta página |
| 2 | ~97% de los clientes compran **una sola vez** — la retención es el mayor problema del negocio | Ventas y Clientes |
| 3 | Las demoras de entrega **destruyen el puntaje de reseñas**: de ~4.3 a ~1.7 estrellas | Esta página · Logística |
| 4 | Dos estrategias de categoría coexisten: volumen (bed_bath_table) y valor alto (watches_gifts) | Productos |
| 5 | 4 segmentos accionables de clientes identificados vía K-Means sobre RFM | Esta página · Segmentación IA |
"""
)