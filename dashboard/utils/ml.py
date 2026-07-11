"""Segmentación de clientes RFM + K-Means con propósito de negocio explícito.

Cada segmento resultante mapea a una acción de marketing concreta.
Los customer_unique_id se truncan al mostrarse (principio de minimización
de datos, alineado con LGPD).
"""

import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Acciones de negocio por perfil de segmento
SEGMENT_ACTIONS = {
    "Campeones": {
        "desc": "Compraron recientemente, alta frecuencia y alto valor.",
        "action": "Programa de fidelidad y acceso anticipado a nuevos productos. "
                  "Son los mejores candidatos para referidos.",
        "color": "🏆",
    },
    "Leales": {
        "desc": "Frecuencia y valor por encima del promedio, compra no tan reciente.",
        "action": "Venta cruzada de categorías complementarias y recordatorios "
                  "personalizados para mantener el hábito.",
        "color": "💎",
    },
    "En Riesgo": {
        "desc": "Fueron buenos clientes pero llevan mucho tiempo sin comprar.",
        "action": "Campaña de reactivación con descuento agresivo (15-20%) "
                  "antes de perderlos definitivamente.",
        "color": "⚠️",
    },
    "Inactivos": {
        "desc": "Compraron una vez hace mucho, bajo valor.",
        "action": "Email de bajo costo con novedades. No invertir en ads pagados "
                  "para este segmento — el ROI no lo justifica.",
        "color": "😴",
    },
}


@st.cache_data(ttl=3600, show_spinner="Entrenando modelo de segmentación...")
def segment_customers(rfm_df: pd.DataFrame, n_clusters: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica K-Means sobre las variables RFM estandarizadas.

    Retorna:
        df con columna de segmento asignado por cliente,
        resumen por segmento con métricas y acción recomendada.
    """
    df = rfm_df.copy()

    features = df[["recency_days", "frequency", "monetary"]]
    scaled = StandardScaler().fit_transform(features)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(scaled)

    # Mapear clusters a nombres de negocio según su perfil promedio:
    # ordenamos por "salud" del segmento (recency baja + monetary alto = mejor)
    profile = (
        df.groupby("cluster")
        .agg(recency=("recency_days", "mean"), monetary=("monetary", "mean"))
        .assign(health=lambda x: x["monetary"].rank() - x["recency"].rank())
        .sort_values("health", ascending=False)
    )
    names = ["Campeones", "Leales", "En Riesgo", "Inactivos"]
    cluster_to_name = {c: names[i] for i, c in enumerate(profile.index)}
    df["segment_name"] = df["cluster"].map(cluster_to_name)

    # Anonimizar ID para display (minimización de datos / LGPD)
    df["customer_id_display"] = df["customer_unique_id"].str[:8] + "..."

    summary = (
        df.groupby("segment_name")
        .agg(
            customers=("customer_unique_id", "count"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_value=("monetary", "sum"),
        )
        .round(2)
        .reset_index()
    )
    summary["accion_recomendada"] = summary["segment_name"].map(
        lambda s: SEGMENT_ACTIONS[s]["action"]
    )

    return df, summary