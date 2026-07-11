"""Productos — rentabilidad del catálogo y eficiencia logística."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import q_kpis_productos, q_categoria_ranking, q_flete_eficiencia
from utils.charts import ranking_hbar, diverging_hbar, fmt_money, PRIMARY, ACCENT

dates  = st.session_state.get("f_dates", ("2016-09-01", "2018-10-31"))
states = st.session_state.get("f_states", ())

st.title("📦 Productos")
st.caption("Rentabilidad del catálogo y eficiencia logística · "
           "Período completo del dataset"
           + (f" · Estados: {', '.join(states)}" if states else " · Todo Brasil"))

# ------------------------------------------------------------------ 6 KPIs
k = run_query(q_kpis_productos(dates, states)).iloc[0]
cats = run_query(q_categoria_ranking(dates, states, 15))
top_ticket = cats.sort_values("ticket_prom", ascending=False).iloc[0]

c = st.columns(6)
c[0].metric("Ingreso del catálogo", fmt_money(k["ingreso_catalogo"]))
c[1].metric("Unidades vendidas",    f"{int(k['unidades']):,}")
c[2].metric("Categorías activas",   f"{int(k['categorias'])}",
            f"{int(k['skus']):,} SKUs en catálogo", delta_color="off")
c[3].metric("Ticket más alto",      top_ticket["categoria"],
            f"R$ {top_ticket['ticket_prom']:,.0f} promedio", delta_color="off")
c[4].metric("Flete sobre ingreso",  f"{k['flete_sobre_ingreso']}%")
c[5].metric("SKUs sin dimensiones", f"{int(k['skus_sin_dimensiones'])}",
            f"{100*k['skus_sin_dimensiones']/k['skus']:.1f}% del catálogo",
            delta_color="off")

st.divider()

# ------------------------------------------------------------------ Ranking ingresos
st.subheader("Ingresos por categoría")
st.caption("Top 15 · participación sobre ingresos totales")

cats["participacion"] = 100 * cats["ingresos"] / k["ingreso_catalogo"]
st.plotly_chart(
    ranking_hbar(cats, "ingresos", "categoria",
                 "Barras de un solo tono: el largo ya codifica la magnitud",
                 pct_col="participacion"),
    use_container_width=True,
)

st.divider()

# ------------------------------------------------------------------ Volumen vs ticket
st.subheader("Volumen contra ticket promedio")
st.caption("Top 10 por unidades · el ticket va escrito junto a la barra · "
           "rosa = estrategia premium (ticket sobre el percentil 75)")

top_vol = cats.sort_values("unidades", ascending=False).head(10).copy()
umbral_premium = cats["ticket_prom"].quantile(0.75)
top_vol["texto"] = top_vol.apply(
    lambda r: f"{r['unidades']:,.0f} u.  ·  R$ {r['ticket_prom']:,.0f}", axis=1)

import plotly.graph_objects as go
from utils.charts import DARK_LAYOUT, GRID

d = top_vol.sort_values("unidades")
colores = [ACCENT if t > umbral_premium else PRIMARY for t in d["ticket_prom"]]
fig = go.Figure(go.Bar(
    x=d["unidades"], y=d["categoria"], orientation="h",
    marker=dict(color=colores, line=dict(width=0)),
    text=d["texto"], textposition="outside", cliponaxis=False,
    textfont=dict(size=12),
))
fig.update_layout(**{**DARK_LAYOUT,
    "title": "Unidades vendidas por categoría (color = estrategia)",
    "height": 440,
    "xaxis": dict(**GRID, title="Unidades vendidas"),
    "yaxis": dict(dtick=1, title=None),
    "margin": dict(l=10, r=140, t=60, b=10)})
st.plotly_chart(fig, use_container_width=True)

st.caption("Reemplaza la matriz de burbujas: en vez de decodificar tres canales "
           "visuales a la vez, las categorías se ordenan y el segundo dato se lee como texto.")

st.divider()

# ------------------------------------------------------------------ Eficiencia de flete
st.subheader("Eficiencia de flete por categoría")
st.caption("Desviación del costo por kilo facturable respecto a la media")

flete = run_query(q_flete_eficiencia(dates, states))
st.plotly_chart(
    diverging_hbar(flete, "desviacion_pct", "categoria",
                   "Rojo = sobrecosto · Cian = por debajo de la media",
                   "Desviación vs media"),
    use_container_width=True,
)

st.warning(
    "**Nota metodológica:** kilo facturable = el mayor entre el peso real y el "
    "peso volumétrico (`product_volume_cm3 / 6000`), el estándar de la industria "
    "courier. Las categorías en rojo son voluminosas y livianas: pagan flete por "
    "espacio, no por peso. "
    f"**Calidad de datos:** {int(k['skus_sin_dimensiones'])} SKUs "
    f"({100*k['skus_sin_dimensiones']/k['skus']:.1f}% del catálogo) se excluyen "
    "de este análisis por carecer de peso o dimensiones."
)

st.divider()

# ------------------------------------------------------------------ Decisiones
st.subheader("Decisiones accionables")
d1, d2, d3 = st.columns(3)
d1.markdown("**💎 Marketing en categorías premium**  \n"
            "Cada conversión en watches_gifts u office_furniture vale ~2x el "
            "promedio — el presupuesto rinde más ahí.")
d2.markdown("**📦 Renegociar flete de voluminosos**  \n"
            "furniture_decor y bed_bath_table pagan sobrecosto por peso "
            "volumétrico: renegociar tarifa o ajustar el precio de envío.")
d3.markdown("**🧹 Completar dimensiones del catálogo**  \n"
            "Exigir peso y medidas a los SKUs incompletos — sin ellos el "
            "cálculo de flete es impreciso y el sobrecosto invisible.")
