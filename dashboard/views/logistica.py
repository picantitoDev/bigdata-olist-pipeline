"""Logística — desempeño de entrega y su impacto en la satisfacción."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import (
    q_kpis_logistica, q_retraso_estado, q_retraso_mensual,
    q_score_por_retraso, q_seller_vs_transito,
)
from utils.charts import (
    ranking_hbar, dual_line, donut, stacked_hbar, fmt_money, insight,
    con_nombres_estado, PRIMARY, NEGATIVE, ACCENT, POSITIVE,
)

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("🚚 Logística")
st.caption("Desempeño de entrega y su impacto en la satisfacción del cliente"
           + (f" · {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_logistica(dates, states)).iloc[0]

c = st.columns(6)
c[0].metric("Entregas a tiempo",      f"{k['pct_a_tiempo']}%")
c[1].metric("Tiempo de entrega prom.", f"{k['dias_entrega_prom']} días")
c[2].metric("Retraso prom. (si ocurre)", f"{k['retraso_prom']} días")
c[3].metric("Score entrega a tiempo", f"{k['score_a_tiempo']} ⭐")
c[4].metric("Score con +15 días",     f"{k['score_muy_tarde']} ⭐",
            f"-{k['score_a_tiempo'] - k['score_muy_tarde']:.2f}",
            delta_color="inverse")
c[5].metric("Ingresos en órdenes tardías", fmt_money(k["ingresos_tardias"]),
            f"{k['pct_tardias']}% de las órdenes", delta_color="off")

st.divider()

# ------------------------------------------------------------------ Fila principal
col_izq, col_med, col_der = st.columns([3, 2, 2])

retrasos = run_query(q_retraso_estado(dates, states))
retrasos = con_nombres_estado(retrasos, "estado")

with col_izq:
    st.subheader("Retrasos por estado")
    st.plotly_chart(
        ranking_hbar(retrasos.head(8), "pct_tardias", "estado",
                     "% de órdenes entregadas fuera de plazo",
                     color=NEGATIVE, height=380),
        use_container_width=True,
    )
    insight(
        "Los estados donde un mayor porcentaje de órdenes llega después de la "
        "fecha estimada. Cuanto más larga la barra, más frecuente es el retraso "
        "en ese estado."
    )

with col_med:
    st.subheader("Concentración geográfica")
    peor = retrasos.iloc[0]
    st.metric(peor["estado"], f"{peor['pct_tardias']}% tardías",
              f"{peor['pct_tardias']/max(k['pct_tardias'], 0.1):.1f}x promedio",
              delta_color="inverse")
    st.metric("Mejor estado", retrasos.iloc[-1]["estado"],
              f"{retrasos['pct_tardias'].min()}% tardías", delta_color="off")
    insight(
        "Compara el estado con más retrasos contra el promedio general del "
        "país, y muestra cuál es el estado con mejor cumplimiento de entrega."
    )

with col_der:
    st.subheader("Cumplimiento de entregas")
    st.plotly_chart(
        donut(["A tiempo", "Con retraso"],
              [k["pct_a_tiempo"], k["pct_tardias"]],
              "",
              colors=[PRIMARY, ACCENT],
              center_text=f"{k['pct_a_tiempo']}%"),
        use_container_width=True,
    )
    insight(
        "De cada 100 órdenes entregadas, cuántas llegan dentro del plazo "
        "prometido y cuántas llegan tarde."
    )

st.divider()

# ------------------------------------------------------------------ Fila secundaria
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("Evolución de la tasa de retraso")
    mensual = run_query(q_retraso_mensual(dates, states))
    st.plotly_chart(
        dual_line(mensual, "mes", "pct_tardias", "dias_prom",
                  "", "% tardías", "Días de entrega"),
        use_container_width=True,
    )
    insight(
        "Cómo evoluciona mes a mes el porcentaje de órdenes tardías junto con "
        "el tiempo de entrega promedio. Picos que coinciden con fechas como "
        "Black Friday suelen indicar problemas de capacidad logística."
    )

with col_b:
    st.subheader("Score según demora")
    score = run_query(q_score_por_retraso(dates, states))
    colores = {"A tiempo": POSITIVE, "1-5 días": "#F59E0B",
               "6-15 días": "#F97316", "+15 días": NEGATIVE}
    import plotly.graph_objects as go
    from utils.charts import layout_dict, grid_style
    fig = go.Figure(go.Bar(
        x=score["tramo"], y=score["score_prom"],
        marker=dict(color=[colores.get(t, PRIMARY) for t in score["tramo"]]),
        text=score["score_prom"], textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(**{**layout_dict(), "title": "",
                         "height": 400, "yaxis": dict(**grid_style(), range=[0, 5], title="Score promedio"),
                         "xaxis": dict(**grid_style(), title=None)})
    st.plotly_chart(fig, use_container_width=True)
    insight(
        "Muestra cómo cae la calificación (de 1 a 5 estrellas) que deja el "
        "cliente a medida que la entrega se retrasa más. Es la prueba de que "
        "el retraso afecta directamente la satisfacción."
    )

with col_c:
    st.subheader("Vendedor vs. transportista")
    desc = run_query(q_seller_vs_transito(dates, states))
    desc = con_nombres_estado(desc, "estado")
    st.plotly_chart(
        stacked_hbar(desc, "estado",
                     ["dias_vendedor", "dias_transito"],
                     ["Vendedor", "Transportista"],
                     "", [PRIMARY, ACCENT], "Días promedio"),
        use_container_width=True,
    )
    insight(
        "**Vendedor** = días entre que se aprueba el pago y el vendedor entrega "
        "el paquete al transportista (tiempo de preparación/despacho). "
        "**Transportista** = días entre que el transportista recoge el paquete "
        "y lo entrega al cliente (tiempo de tránsito/reparto). Juntos suman el "
        "tiempo total de entrega; el color más largo indica dónde está el cuello "
        "de botella en cada estado — si es 'Vendedor', el problema es de "
        "despacho; si es 'Transportista', es de distancia o del operador logístico."
    )

st.divider()