"""Logística — desempeño de entrega y su impacto en satisfacción."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import DELIVERY_VS_SATISFACCION, ONTIME_POR_ESTADO, DISTRIBUCION_DELIVERY
from utils.charts import bar_chart, histogram

st.set_page_config(page_title="Logística", page_icon="🚚", layout="wide")
st.title("🚚 Logística y Satisfacción")

# ------------------------------------------------------------------ Insight estrella
st.subheader("El costo real de una entrega tardía")

sat = run_query(DELIVERY_VS_SATISFACCION)

col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(
        bar_chart(sat, "delivery_bucket", "avg_score",
                  "Puntaje promedio de reseñas según demora de entrega"),
        use_container_width=True,
    )

with col_r:
    on_time = sat.iloc[0]
    worst = sat.iloc[-1]
    drop = on_time["avg_score"] - worst["avg_score"]

    st.metric("Puntaje con entrega a tiempo", f"{on_time['avg_score']} ⭐")
    st.metric("Puntaje con +15 días de demora", f"{worst['avg_score']} ⭐",
              f"-{drop:.1f} estrellas", delta_color="inverse")
    st.markdown(
        "**Insight estrella:** la demora de entrega es el predictor "
        "más fuerte de una mala reseña. Una demora mayor a 15 días "
        "prácticamente garantiza una reseña de 1-2 estrellas, dañando "
        "el ranking del seller y la conversión futura del marketplace."
    )

st.dataframe(
    sat, use_container_width=True, hide_index=True,
    column_config={
        "delivery_bucket": "Demora de entrega",
        "reviews": "Reseñas",
        "avg_score": "Puntaje promedio",
        "pct_positive": "% positivas",
    },
)

st.divider()

# ------------------------------------------------------------------ Por estado
st.subheader("Cumplimiento de entrega por estado")

ontime = run_query(ONTIME_POR_ESTADO)

col_l, col_r = st.columns([2, 1])

with col_l:
    st.plotly_chart(
        bar_chart(ontime.sort_values("pct_on_time"), "pct_on_time", "customer_state",
                  "% de entregas a tiempo por estado", horizontal=True),
        use_container_width=True,
    )

with col_r:
    best = ontime.iloc[0]
    worst_st = ontime.iloc[-1]
    st.metric("Mejor estado", best["customer_state"], f"{best['pct_on_time']}% a tiempo")
    st.metric("Peor estado", worst_st["customer_state"],
              f"{worst_st['pct_on_time']}% a tiempo", delta_color="inverse")
    st.markdown(
        "**Recomendación:** los estados con menor cumplimiento deberían "
        "recibir promesas de entrega más conservadoras (margen en la fecha estimada) "
        "para proteger el puntaje de reseñas, mientras se evalúan transportistas alternativos."
    )

st.divider()

# ------------------------------------------------------------------ Distribución
st.subheader("Distribución de tiempos de entrega")

dist = run_query(DISTRIBUCION_DELIVERY)
st.plotly_chart(
    histogram(dist, "delivery_days", "orders",
              "Distribución de días de entrega (0-60 días)", "Días de entrega"),
    use_container_width=True,
)
st.caption(
    "La mayoría de las órdenes se entrega en 5-15 días. La cola larga "
    "más allá de 30 días representa el segmento de mayor riesgo reputacional."
)
