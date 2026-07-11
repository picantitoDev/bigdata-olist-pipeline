"""Productos — rentabilidad del catálogo y eficiencia logística."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import q_kpis_productos, q_categoria_ranking, q_flete_eficiencia
from utils.charts import ranking_hbar, diverging_hbar, fmt_money, PRIMARY, ACCENT

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("📦 Productos")
st.caption("Rentabilidad del catálogo y eficiencia logística"
           + (f" · {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_productos(dates, states)).iloc[0]
cats = run_query(q_categoria_ranking(dates, states, 15))
# "ticket_prom" = valor promedio de venta por unidad en esa categoría.
top_valor = cats.sort_values("ticket_prom", ascending=False).iloc[0]

c = st.columns(6)
c[0].metric("Ingreso del catálogo", fmt_money(k["ingreso_catalogo"]))
c[1].metric("Unidades vendidas",    f"{int(k['unidades']):,}")
c[2].metric("Categorías activas",   f"{int(k['categorias'])}",
            f"{int(k['skus']):,} SKUs", delta_color="off")
c[3].metric("Categoría de mayor valor por venta", top_valor["categoria"],
            f"R$ {top_valor['ticket_prom']:,.0f} en promedio", delta_color="off")
c[4].metric("Flete sobre ingreso",  f"{k['flete_sobre_ingreso']}%")
c[5].metric("SKUs sin dimensiones", f"{int(k['skus_sin_dimensiones'])}",
            f"{100*k['skus_sin_dimensiones']/k['skus']:.1f}% del catálogo",
            delta_color="off")

st.divider()

# ------------------------------------------------------------------ Ranking ingresos
st.subheader("Ingresos por categoría")

cats["participacion"] = 100 * cats["ingresos"] / k["ingreso_catalogo"]
st.plotly_chart(
    ranking_hbar(cats, "ingresos", "categoria", "",
                 pct_col="participacion"),
    use_container_width=True,
)

st.divider()

# ------------------------------------------------------------------ Volumen vs valor promedio
st.subheader("Volumen de ventas frente al valor promedio por unidad")

top_vol = cats.sort_values("unidades", ascending=False).head(10).copy()
umbral_premium = cats["ticket_prom"].quantile(0.75)
top_vol["texto"] = top_vol.apply(
    lambda r: f"{r['unidades']:,.0f} u.  ·  R$ {r['ticket_prom']:,.0f}", axis=1)

import plotly.graph_objects as go
from utils.charts import layout_dict, grid_style

d = top_vol.sort_values("unidades")
colores = [ACCENT if t > umbral_premium else PRIMARY for t in d["ticket_prom"]]
fig = go.Figure(go.Bar(
    x=d["unidades"], y=d["categoria"], orientation="h",
    marker=dict(color=colores, line=dict(width=0)),
    text=d["texto"], textposition="outside", cliponaxis=False,
    textfont=dict(size=12),
))
fig.update_layout(**{**layout_dict(),
    "title": "",
    "height": 440,
    "xaxis": dict(**grid_style(), title="Unidades vendidas"),
    "yaxis": dict(dtick=1, title=None),
    "margin": dict(l=10, r=140, t=30, b=10)})
st.plotly_chart(fig, use_container_width=True)

st.caption(
    f"🔵 Categorías de volumen  ·  🔴 Categorías premium "
    f"(valor promedio por unidad sobre R$ {umbral_premium:,.0f})"
)

st.divider()

# ------------------------------------------------------------------ Eficiencia de flete
st.subheader("Eficiencia de flete por categoría")

flete = run_query(q_flete_eficiencia(dates, states))
st.plotly_chart(
    diverging_hbar(flete, "desviacion_pct", "categoria", "",
                   "Desviación vs media"),
    use_container_width=True,
)
st.caption(
    f"🔵 Por debajo de la media  ·  🔴 Sobrecosto  ·  "
    f"{int(k['skus_sin_dimensiones'])} SKUs excluidos por falta de datos"
)