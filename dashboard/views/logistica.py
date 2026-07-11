"""Logística — desempeño de entrega y su impacto en la satisfacción."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import (
    q_kpis_logistica, q_retraso_estado, q_retraso_mensual,
    q_score_por_retraso, q_seller_vs_transito,
)
from utils.charts import (
    ranking_hbar, dual_line, donut, stacked_hbar, fmt_money,
    PRIMARY, NEGATIVE, ACCENT, POSITIVE,
)

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("🚚 Logística")
st.caption("Desempeño de entrega y su impacto en la satisfacción del cliente · "
           "Período completo del dataset"
           + (f" · Estados: {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_logistica(dates, states)).iloc[0]

c = st.columns(6)
c[0].metric("Entregas a tiempo",      f"{k['pct_a_tiempo']}%")
c[1].metric("Tiempo de entrega prom.", f"{k['dias_entrega_prom']} días")
c[2].metric("Retraso prom. (si ocurre)", f"{k['retraso_prom']} días",
            help="Sobre la fecha prometida, solo en órdenes tardías")
c[3].metric("Score entrega a tiempo", f"{k['score_a_tiempo']} ⭐")
c[4].metric("Score con +15 días",     f"{k['score_muy_tarde']} ⭐",
            f"-{k['score_a_tiempo'] - k['score_muy_tarde']:.2f} vs puntual",
            delta_color="inverse")
c[5].metric("Ingresos en órdenes tardías", fmt_money(k["ingresos_tardias"]),
            f"{k['pct_tardias']}% de las órdenes", delta_color="off")

st.divider()

# ------------------------------------------------------------------ Fila principal
col_izq, col_med, col_der = st.columns([3, 2, 2])

retrasos = run_query(q_retraso_estado(dates, states))

with col_izq:
    st.subheader("Retrasos por estado")
    st.caption("% de órdenes entregadas después de la fecha prometida")
    st.plotly_chart(
        ranking_hbar(retrasos.head(8), "pct_tardias", "estado",
                     "Ranking de estados con más retrasos",
                     color=NEGATIVE, height=380),
        use_container_width=True,
    )
    st.info(f"**Referencia:** promedio nacional {k['pct_tardias']}% · "
            f"el mejor estado registra {retrasos['pct_tardias'].min()}%.")

with col_med:
    st.subheader("💡 Insight clave")
    peor = retrasos.iloc[0]
    st.markdown(
        f"El retraso es un problema **geográficamente concentrado**: "
        f"**{peor['estado']}** registra {peor['pct_tardias']}% de órdenes tardías, "
        f"{peor['pct_tardias']/max(k['pct_tardias'], 0.1):.1f}x el promedio. "
        "La causa dominante no es la preparación del vendedor sino el "
        "**tránsito del transportista** (ver descomposición), lo que orienta "
        "la solución hacia transportistas regionales y no hacia los vendedores."
    )

with col_der:
    st.subheader("Cumplimiento de entregas")
    st.plotly_chart(
        donut(["A tiempo", "Con retraso"],
              [k["pct_a_tiempo"], k["pct_tardias"]],
              "Participación sobre órdenes entregadas",
              colors=[PRIMARY, ACCENT],
              center_text=f"{k['pct_a_tiempo']}%"),
        use_container_width=True,
    )
    st.error(
        f"**Riesgo reputacional:** {fmt_money(k['ingresos_tardias'])} en ingresos "
        "está asociado a órdenes con retraso — cada punto porcentual evitado "
        "protege ingresos y previene reseñas negativas."
    )

st.divider()

# ------------------------------------------------------------------ Fila secundaria
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("Evolución de la tasa de retraso")
    mensual = run_query(q_retraso_mensual(dates, states))
    st.plotly_chart(
        dual_line(mensual, "mes", "pct_tardias", "dias_prom",
                  "% tardías vs días promedio de entrega",
                  "% tardías", "Días de entrega"),
        use_container_width=True,
    )

with col_b:
    st.subheader("Score según magnitud del retraso")
    score = run_query(q_score_por_retraso(dates, states))
    colores = {"A tiempo": POSITIVE, "1-5 días": "#F59E0B",
               "6-15 días": "#F97316", "+15 días": NEGATIVE}
    import plotly.graph_objects as go
    from utils.charts import DARK_LAYOUT, GRID
    fig = go.Figure(go.Bar(
        x=score["tramo"], y=score["score_prom"],
        marker=dict(color=[colores.get(t, PRIMARY) for t in score["tramo"]]),
        text=score["score_prom"], textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(**{**DARK_LAYOUT, "title": "Puntaje promedio por tramo de demora",
                         "height": 400, "yaxis": dict(**GRID, range=[0, 5], title="Score promedio"),
                         "xaxis": dict(**GRID, title=None)})
    st.plotly_chart(fig, use_container_width=True)

with col_c:
    st.subheader("¿Quién causa la demora?")
    desc = run_query(q_seller_vs_transito(dates, states))
    st.plotly_chart(
        stacked_hbar(desc, "estado",
                     ["dias_vendedor", "dias_transito"],
                     ["Preparación del vendedor", "Tránsito del transportista"],
                     "Días promedio por etapa (estados con más retraso)",
                     [PRIMARY, ACCENT], "Días promedio"),
        use_container_width=True,
    )

st.divider()

# ------------------------------------------------------------------ Decisiones
st.subheader("Decisiones accionables")
d1, d2, d3, d4 = st.columns(4)
d1.markdown("**📌 Ajustar promesa en estados críticos**  \n"
            "Ampliar el margen de la fecha estimada en los estados del ranking — "
            "protege el score a costo cero.")
d2.markdown("**🚛 Transportista alternativo en el nordeste**  \n"
            "El tránsito, no el vendedor, domina la demora en la región: evaluar "
            "transportistas regionales o un hub.")
d3.markdown("**⏱️ SLA de despacho de 48h**  \n"
            "Para los vendedores cuyo tramo de preparación excede los 3 días.")
d4.markdown("**🛡️ Intervención proactiva 6+ días**  \n"
            "Contacto y compensación preventiva en órdenes con retraso proyectado "
            "de 6+ días, donde el score cae bajo 2.4.")
