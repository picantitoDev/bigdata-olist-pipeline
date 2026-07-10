"""Segmentación IA — RFM + K-Means con acciones de campaña por segmento."""

import streamlit as st

from utils.bigquery import run_query
from utils.queries import RFM_BASE
from utils.ml import segment_customers, SEGMENT_ACTIONS
from utils.charts import segment_scatter_3d

st.set_page_config(page_title="Segmentación IA", page_icon="🤖", layout="wide")
st.title("🤖 Segmentación de Clientes con IA")

st.markdown(
    """
**Propósito de negocio:** dado que ~97% de los clientes compra una sola vez
(ver *Ventas y Clientes*), este módulo identifica **a quién dirigir cada tipo de
campaña de retención** para maximizar el ROI del presupuesto de marketing.

**Metodología:** análisis RFM (Recency, Frequency, Monetary) calculado en BigQuery
sobre `customer_unique_id` (la persona real, no la instancia de orden), seguido de
clustering K-Means (k=4) sobre variables estandarizadas.
"""
)

# ------------------------------------------------------------------ Modelo
rfm = run_query(RFM_BASE)
df_seg, summary = segment_customers(rfm)

st.subheader("Perfiles de segmento")

cols = st.columns(4)
for i, (_, row) in enumerate(summary.iterrows()):
    seg = row["segment_name"]
    with cols[i]:
        st.metric(
            f"{SEGMENT_ACTIONS[seg]['color']} {seg}",
            f"{row['customers']:,} clientes",
            f"R$ {row['total_value']:,.0f} en valor",
        )

st.dataframe(
    summary[["segment_name", "customers", "avg_recency_days",
             "avg_frequency", "avg_monetary", "accion_recomendada"]],
    use_container_width=True, hide_index=True,
    column_config={
        "segment_name": "Segmento",
        "customers": "Clientes",
        "avg_recency_days": "Recency prom. (días)",
        "avg_frequency": "Frecuencia prom.",
        "avg_monetary": "Valor prom. (R$)",
        "accion_recomendada": "Acción de campaña recomendada",
    },
)

st.divider()

# ------------------------------------------------------------------ Visualización
st.subheader("Visualización de clusters (espacio RFM)")

sample = df_seg.sample(min(5000, len(df_seg)), random_state=42)
st.plotly_chart(
    segment_scatter_3d(sample, "Clusters de clientes en el espacio RFM (muestra de 5,000)"),
    use_container_width=True,
)

st.divider()

# ------------------------------------------------------------------ Exportar
st.subheader("Exportar lista de campaña")

seg_choice = st.selectbox("Segmento a exportar", summary["segment_name"].tolist())
seg_df = df_seg[df_seg["segment_name"] == seg_choice][
    ["customer_id_display", "recency_days", "frequency", "monetary"]
]

st.download_button(
    f"Descargar lista '{seg_choice}' ({len(seg_df):,} clientes) como CSV",
    seg_df.to_csv(index=False),
    file_name=f"campaign_{seg_choice.lower().replace(' ', '_')}.csv",
    mime="text/csv",
)

st.divider()

# ------------------------------------------------------------------ Ética
st.subheader("Consideraciones éticas y legales")
st.markdown(
    """
- **Minimización de datos (LGPD):** los identificadores de cliente se muestran
  truncados. La exportación contiene solo el hash parcial y las métricas RFM,
  nunca datos de contacto ni ubicación precisa.
- **No discriminación:** los segmentos se basan exclusivamente en comportamiento
  de compra — no se usan atributos demográficos, geográficos ni proxies de ellos
  que pudieran generar sesgo.
- **Propósito limitado:** el modelo se entrena y usa únicamente para priorización
  de campañas de retención; no se emplea para decisiones de precio diferenciado
  ni de acceso a servicios.
"""
)
