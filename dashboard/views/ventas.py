"""Ventas y Clientes — desempeño comercial."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import (
    q_kpis_ventas, q_ingresos_estado, q_evolucion,
    q_top_categorias, q_metodos_pago, q_una_compra,
)
from utils.charts import (
    ranking_hbar, dual_line, donut, fmt_money, QUALITATIVE,
    con_nombres_estado, insight,
)

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("🛒 Ventas y Clientes")
st.caption("Resumen ejecutivo del desempeño comercial"
           + (f" · {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_ventas(dates, states)).iloc[0]

c = st.columns(6)
c[0].metric("Ingresos totales",   fmt_money(k["ingresos"]))
c[1].metric("Órdenes totales",    f"{int(k['ordenes']):,}")
c[2].metric("Clientes únicos",    f"{int(k['clientes']):,}")
c[3].metric("Ticket promedio",    f"R$ {k['ticket_promedio']:,.2f}")
c[4].metric("Órdenes por cliente", f"{k['ordenes_por_cliente']:.2f}")
c[5].metric("Tasa de retención",  f"{k['tasa_retencion']}%")

st.divider()

# ------------------------------------------------------------------ Fila principal
col_izq, col_der = st.columns([3, 2])

estados_df = run_query(q_ingresos_estado(dates, states))
total_ing = estados_df["ingresos"].sum()
estados_df["participacion"] = 100 * estados_df["ingresos"] / total_ing
estados_df = con_nombres_estado(estados_df, "estado")

with col_izq:
    st.subheader("Ingresos por estado")
    top5 = estados_df.head(5).copy()
    st.plotly_chart(
        ranking_hbar(top5, "ingresos", "estado", "",
                     pct_col="participacion"),
        use_container_width=True,
    )
    insight(
        "Muestra los 5 estados que más ingresos generan y qué porcentaje del "
        "total representa cada uno. Ayuda a ver dónde está concentrado el negocio "
        "y dónde hay oportunidad de crecer."
    )
    with st.expander("Ver todos los estados"):
        st.dataframe(
            estados_df, use_container_width=True, hide_index=True,
            column_config={
                "estado": "Estado",
                "ingresos": st.column_config.NumberColumn("Ingresos (R$)", format="%.0f"),
                "ticket_por_orden": st.column_config.NumberColumn("Valor promedio por orden (R$)", format="%.2f"),
                "participacion": st.column_config.NumberColumn("Participación %", format="%.1f%%"),
            },
        )

with col_der:
    lider = estados_df.iloc[0]
    mayor_ticket = estados_df.sort_values("ticket_por_orden", ascending=False).iloc[0]

    st.subheader("Concentración")
    st.metric(lider["estado"], f"{lider['participacion']:.1f}% de los ingresos")
    st.metric("Mayor ticket promedio", mayor_ticket["estado"],
              f"R$ {mayor_ticket['ticket_por_orden']:,.2f}", delta_color="off")

    una = run_query(q_una_compra(dates, states)).iloc[0]
    st.markdown("---")
    st.metric("Clientes de una sola compra", f"{una['pct_una_compra']}%")
    st.metric("LTV recurrente vs. único",
              f"R$ {una['ltv_recurrente']:,.0f}",
              f"+{(una['ltv_recurrente']/una['ltv_una']-1)*100:.0f}%",
              delta_color="off")
    insight(
        "El estado líder concentra el mayor porcentaje de ingresos, mientras "
        "que el de mayor valor promedio por orden no siempre es el mismo. "
        "Abajo: qué tan grande es el problema de que un cliente compre una sola "
        "vez y cuánto vale, en promedio, un cliente que sí regresa a comprar."
    )

st.divider()

# ------------------------------------------------------------------ Fila secundaria
col_a, col_b, col_c = st.columns([3, 2, 2])

with col_a:
    st.subheader("Evolución de ingresos y órdenes")
    evo = run_query(q_evolucion(dates, states))
    st.plotly_chart(
        dual_line(evo, "mes", "ingresos", "ordenes",
                  "", "Ingresos (R$)", "Órdenes"),
        use_container_width=True,
    )
    insight(
        "Compara mes a mes cómo crecen (o caen) los ingresos junto con la "
        "cantidad de órdenes. Si ambas líneas suben juntas, el crecimiento es "
        "sano; si los ingresos suben pero las órdenes no, el ticket promedio "
        "está creciendo."
    )

with col_b:
    st.subheader("Top 5 categorías")
    cats = run_query(q_top_categorias(dates, states, 5))
    cats["participacion"] = 100 * cats["ingresos"] / k["ingresos"]
    st.plotly_chart(
        ranking_hbar(cats, "ingresos", "categoria", "",
                     pct_col="participacion", height=400),
        use_container_width=True,
    )
    insight(
        "Las 5 categorías de producto que más ingresos generan. Útil para "
        "saber dónde priorizar inventario y campañas de marketing."
    )

with col_c:
    st.subheader("Métodos de pago")
    pagos = run_query(q_metodos_pago(dates, states))
    st.plotly_chart(
        donut(pagos["metodo"], pagos["valor"], "",
              colors=QUALITATIVE),
        use_container_width=True,
    )
    dom = pagos.iloc[0]
    pct_dom = 100 * dom["valor"] / pagos["valor"].sum()
    st.metric(dom["metodo"], f"{pct_dom:.1f}% del valor total",
              f"{dom['cuotas_prom']:.1f} cuotas prom.", delta_color="off")
    insight(
        "Cómo se reparte el valor de las ventas entre los distintos métodos "
        "de pago, y en cuántas cuotas suele pagar el cliente con el método "
        "más usado."
    )