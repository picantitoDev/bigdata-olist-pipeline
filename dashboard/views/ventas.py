"""Ventas y Clientes — desempeño comercial con filtros globales."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import (
    q_kpis_ventas, q_ingresos_estado, q_evolucion,
    q_top_categorias, q_metodos_pago, q_una_compra,
)
from utils.charts import ranking_hbar, dual_line, donut, fmt_money, QUALITATIVE

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("🛒 Ventas y Clientes")
st.caption("Resumen ejecutivo del desempeño comercial · Período completo del dataset"
           + (f" · Estados: {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_ventas(dates, states)).iloc[0]

c = st.columns(6)
c[0].metric("Ingresos totales",   fmt_money(k["ingresos"]))
c[1].metric("Órdenes totales",    f"{int(k['ordenes']):,}")
c[2].metric("Clientes únicos",    f"{int(k['clientes']):,}")
c[3].metric("Ticket promedio",    f"R$ {k['ticket_promedio']:,.2f}")
c[4].metric("Órdenes por cliente", f"{k['ordenes_por_cliente']:.2f}")
c[5].metric("Tasa de retención",  f"{k['tasa_retencion']}%",
            help="% de clientes con 2 o más compras en el período")

st.divider()

# ------------------------------------------------------------------ Fila principal
col_izq, col_der = st.columns([3, 2])

estados_df = run_query(q_ingresos_estado(dates, states))
total_ing = estados_df["ingresos"].sum()
estados_df["participacion"] = 100 * estados_df["ingresos"] / total_ing

with col_izq:
    st.subheader("Ingresos por estado")
    top5 = estados_df.head(5).copy()
    st.plotly_chart(
        ranking_hbar(top5, "ingresos", "estado",
                     "Top 5 estados · participación % sobre ingresos totales",
                     pct_col="participacion"),
        use_container_width=True,
    )
    with st.expander("Ver todos los estados"):
        st.dataframe(
            estados_df, use_container_width=True, hide_index=True,
            column_config={
                "estado": "Estado",
                "ingresos": st.column_config.NumberColumn("Ingresos (R$)", format="%.0f"),
                "ticket_por_orden": st.column_config.NumberColumn("Ticket/orden (R$)", format="%.2f"),
                "participacion": st.column_config.NumberColumn("Participación %", format="%.1f%%"),
            },
        )

with col_der:
    st.subheader("💡 Insight clave")
    lider = estados_df.iloc[0]
    mayor_ticket = estados_df.sort_values("ticket_por_orden", ascending=False).iloc[0]
    st.markdown(
        f"**{lider['estado']}** concentra el **{lider['participacion']:.1f}%** de los "
        f"ingresos. Sin embargo, el mayor **ticket promedio por orden** está en "
        f"**{mayor_ticket['estado']}** (R$ {mayor_ticket['ticket_por_orden']:,.2f}), "
        "lo que indica oportunidades de crecimiento con estrategias logísticas y "
        "de promoción adecuadas en regiones de alto valor unitario."
    )
    st.metric("Mayor ticket promedio por orden",
              f"R$ {mayor_ticket['ticket_por_orden']:,.2f}",
              mayor_ticket["estado"])

    una = run_query(q_una_compra(dates, states)).iloc[0]
    st.markdown("---")
    st.metric("Clientes de una sola compra", f"{una['pct_una_compra']}%",
              help="El principal reto del negocio: retención")
    st.markdown(
        f"**Oportunidad:** un cliente recurrente vale R$ {una['ltv_recurrente']:,.0f} "
        f"vs R$ {una['ltv_una']:,.0f} del cliente único "
        f"(+{(una['ltv_recurrente']/una['ltv_una']-1)*100:.0f}%). Mejorar la experiencia "
        "postventa y personalización puede aumentar la retención y el valor "
        "del cliente a largo plazo."
    )

st.divider()

# ------------------------------------------------------------------ Fila secundaria
col_a, col_b, col_c = st.columns([3, 2, 2])

with col_a:
    st.subheader("Evolución de ingresos y órdenes")
    evo = run_query(q_evolucion(dates, states))
    st.plotly_chart(
        dual_line(evo, "mes", "ingresos", "ordenes",
                  "Tendencia mensual", "Ingresos (R$)", "Órdenes"),
        use_container_width=True,
    )

with col_b:
    st.subheader("Top 5 categorías")
    cats = run_query(q_top_categorias(dates, states, 5))
    cats["participacion"] = 100 * cats["ingresos"] / k["ingresos"]
    st.plotly_chart(
        ranking_hbar(cats, "ingresos", "categoria",
                     "Participación sobre ingresos totales",
                     pct_col="participacion", height=400),
        use_container_width=True,
    )

with col_c:
    st.subheader("Métodos de pago")
    pagos = run_query(q_metodos_pago(dates, states))
    st.plotly_chart(
        donut(pagos["metodo"], pagos["valor"],
              "Participación sobre valor total",
              colors=QUALITATIVE),
        use_container_width=True,
    )
    dom = pagos.iloc[0]
    pct_dom = 100 * dom["valor"] / pagos["valor"].sum()
    st.success(
        f"**Insight:** {dom['metodo']} domina con el {pct_dom:.1f}% del valor total "
        f"({dom['cuotas_prom']:.1f} cuotas promedio)."
    )

st.divider()

# ------------------------------------------------------------------ Decisiones
st.subheader("Decisiones accionables")
d1, d2, d3, d4 = st.columns(4)
d1.markdown("**📍 Expandir en regiones con alto ticket promedio**  \n"
            "Fortalecer la logística y campañas en el norte y noreste del país.")
d2.markdown("**👥 Impulsar la retención de clientes**  \n"
            "Programas de fidelización, descuentos personalizados y "
            "seguimiento postventa.")
d3.markdown("**💳 Optimizar métodos de pago**  \n"
            "Promociones con tarjeta y alianzas financieras para facilitar cuotas.")
d4.markdown("**📊 Foco en categorías estratégicas**  \n"
            "Invertir marketing en categorías con mayor participación y crecimiento.")
