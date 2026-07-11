"""Arquitectura — documentación del pipeline ELT completo y sus garantías."""

import streamlit as st

st.title("🏗️ Arquitectura del Pipeline ELT")

# ------------------------------------------------------------------ Diagrama
st.subheader("Flujo de datos end-to-end")

st.code(
    """
Kaggle (Olist dataset)
   │
   ▼  dlt (Python) — ingesta automatizada con retry + schema inference
GCS Raw Bucket (parquet)
   │
   ▼  Apache Spark en Dataproc — limpieza, tipado, normalización
GCS Processed Bucket (parquet, particionado por fecha)
   │
   ▼  BigQuery External Tables — mapeo sin duplicar almacenamiento
BigQuery olist_raw
   │
   ▼  dbt — transformación en 3 capas con 94 tests de calidad
BigQuery olist_staging → olist_intermediate → olist_marts
   │
   ▼  Streamlit + scikit-learn (esta aplicación)
Dashboard analítico + Segmentación IA
""",
    language=None,
)

st.markdown(
    "Todo el flujo está **orquestado por Kestra** (4 flows encadenables) y la "
    "**infraestructura gestionada por Terraform** (IaC, reproducible en un comando)."
)

st.divider()

# ------------------------------------------------------------------ Componentes
st.subheader("Componentes y su rol")

st.markdown(
    """
| Capa | Tecnología | Rol | Garantía que aporta |
|---|---|---|---|
| Infraestructura | Terraform | Buckets, datasets, cluster, SA, IAM | Reproducibilidad, IaC versionado |
| Ingesta | dlt + Kestra + Docker | Kaggle → GCS raw como parquet | Retry automático, schema inference |
| Procesamiento | Spark 3 en Dataproc (2 workers) | Limpieza y tipado distribuido | Escalabilidad horizontal |
| Almacenamiento | GCS + BigQuery | Data lake + warehouse serverless | Alta disponibilidad gestionada por GCP |
| Transformación | dbt (BigQuery adapter) | Modelo dimensional en 3 capas | 94 tests de integridad automatizados |
| Orquestación | Kestra (Docker Compose) | Flows programables y monitoreables | Observabilidad, reejecución |
| Analítica | Streamlit + scikit-learn | Dashboards + segmentación ML | Caché de queries (TTL 1h) |
"""
)

st.divider()

# ------------------------------------------------------------------ Modelo dimensional
st.subheader("Modelo dimensional (olist_marts)")

col_l, col_r = st.columns(2)

with col_l:
    st.markdown(
        """
**Dimensiones**
- `dim_customers` — cliente + coordenadas geográficas
- `dim_sellers` — vendedor + coordenadas geográficas
- `dim_products` — producto + categoría en inglés + volumen
- `dim_orders` — orden + métricas de entrega precalculadas
- `dim_dates` — calendario generado 2016-2019
"""
    )

with col_r:
    st.markdown(
        """
**Hechos**
- `fct_order_items` — grano: ítem de orden (112.7k filas)
- `fct_payments` — grano: pago secuencial (103.9k filas)
- `fct_order_reviews` — grano: una review por orden (98.7k filas)
"""
    )

st.divider()

# ------------------------------------------------------------------ Seguridad
st.subheader("Seguridad e integridad")

st.markdown(
    """
**Seguridad (ISO/IEC 27001 alineado):**
- Service Account con **mínimo privilegio** — roles separados por servicio, no `owner`
- Buckets con `uniform_bucket_level_access` — sin ACLs por objeto
- Credenciales fuera del repositorio (`.gitignore`), inyectadas como secretos en Kestra y Streamlit
- Lifecycle rules: datos raw se purgan a los 90 días (minimización de datos)

**Integridad de datos (ISO/IEC 25012 alineado):**
- **94 tests dbt** ejecutados en cada corrida: `unique`, `not_null`, `relationships`, `accepted_values`
- Integridad referencial verificada entre todos los hechos y dimensiones
- Columna `processed_at` en cada tabla para trazabilidad temporal
- Deduplicación documentada (geolocation por zip, reviews por orden)

**Rendimiento:**
- Agregaciones ejecutadas **en BigQuery**, no en la aplicación
- `st.cache_data` con TTL de 1 hora — una query por hora por vista, no por usuario
- Marts materializados como tablas; staging como vistas (balance costo/velocidad)

**Alta disponibilidad:**
- GCS y BigQuery son servicios gestionados multi-zona por defecto
- El pipeline es idempotente: cualquier flow puede reejecutarse sin efectos colaterales
"""
)

st.divider()

st.caption(
    "Repositorio: github.com/picantitoDev/bigdata-olist-pipeline — "
    "Infraestructura, ingesta, procesamiento, transformación y esta aplicación "
    "en un único monorepo versionado."
)
