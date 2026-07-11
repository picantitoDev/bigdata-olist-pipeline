"""Olist Analytics — router principal con navegación y filtro de estados."""

import streamlit as st

st.set_page_config(
    page_title="Olist Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ Sidebar
# Sin fondos hardcodeados: hereda el tema y solo añade acentos sutiles.
st.markdown("""
<style>
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(124,111,232,0.25);
}
[data-testid="stSidebarNav"] a {
    border-radius: 8px;
    margin: 2px 8px;
    padding: 8px 12px;
}
[data-testid="stSidebar"] a[aria-current="page"] {
    background: rgba(124,111,232,0.16) !important;
    border-left: 3px solid #7C6FE8;
}
.sidebar-brand { padding: 4px 6px 14px 6px; margin-bottom: 6px;
                 border-bottom: 1px solid rgba(124,111,232,0.25); }
.sidebar-brand h2 { font-size: 1.12rem; margin: 0; letter-spacing: .3px; }
.sidebar-brand p  { font-size: .70rem; margin: 3px 0 0 0; opacity: .55;
                    text-transform: uppercase; letter-spacing: 1.3px; }
.sidebar-footer   { font-size: .70rem; opacity: .45; padding: 14px 6px 4px 6px;
                    border-top: 1px solid rgba(124,111,232,0.25); margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

ESTADOS_BR = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
              "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]

# Período completo del dataset — sin filtro de fechas en la UI
st.session_state["f_dates"] = ("2016-09-01", "2018-10-31")

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand"><h2>🛍️ Olist Analytics</h2>'
        '<p>Inteligencia comercial</p></div>',
        unsafe_allow_html=True,
    )
    estados_sel = st.multiselect(
        "Filtrar por estado", ESTADOS_BR, default=[],
        placeholder="Todos los estados",
        help="Vacío = análisis de todo Brasil",
    )
    st.session_state["f_states"] = tuple(sorted(estados_sel))

    st.markdown(
        '<div class="sidebar-footer">Período completo: sep 2016 – oct 2018<br>'
        'BigQuery · olist_marts · 94 tests ✓</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ Navegación
pages = [
    st.Page("views/resumen.py",      title="Resumen Ejecutivo", icon="📈", default=True),
    st.Page("views/ventas.py",       title="Ventas y Clientes", icon="🛒"),
    st.Page("views/logistica.py",    title="Logística",         icon="🚚"),
    st.Page("views/productos.py",    title="Productos",         icon="📦"),
    st.Page("views/segmentacion.py", title="Segmentación IA",   icon="🤖"),
    st.Page("views/arquitectura.py", title="Arquitectura",      icon="🏗️"),
]

st.navigation(pages).run()
