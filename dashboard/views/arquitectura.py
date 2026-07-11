"""Arquitectura — documentación del pipeline ELT completo y sus garantías."""

import streamlit as st
import streamlit.components.v1 as components

st.title("🏗️ Arquitectura del Pipeline ELT")
st.caption(
    "De Kaggle a un dashboard analítico: ingesta, procesamiento distribuido, "
    "modelo dimensional y consumo, orquestados end-to-end."
)

# ------------------------------------------------------------------ Métricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tests de calidad dbt", "94", help="unique, not_null, relationships, accepted_values")
c2.metric("Capas del medallón", "3", help="staging → intermediate → marts")
c3.metric("Modelos en marts", "8", help="5 dimensiones + 3 hechos")
c4.metric("Filas en los hechos", "315.3k", help="items + pagos + reviews")

st.divider()

# ------------------------------------------------------------------ Diagrama
st.subheader("Flujo de datos end-to-end")

PIPELINE_SVG = """
<style>
  .box   { rx: 8; stroke-width: 0.5; }
  .t     { font: 500 13px -apple-system, "Segoe UI", Roboto, sans-serif; }
  .ts    { font: 400 11px -apple-system, "Segoe UI", Roboto, sans-serif; }
  .gray  { fill: #262b36; stroke: #4a5262; }
  .purple{ fill: #2b2560; stroke: #7f77dd; }
  .teal  { fill: #0f3b32; stroke: #3fbfae; }
  .title { fill: #e8eaed; }
  .sub   { fill: #9aa3b2; }
  .arr   { stroke: #6b7484; stroke-width: 1.5; fill: none; }
</style>
<svg width="100%" viewBox="0 0 1180 170" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Pipeline ELT horizontal: Kaggle, dlt hacia GCS raw,
     Spark en Dataproc, BigQuery, dbt en tres capas y Streamlit.">
  <defs>
    <marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6"
            orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#6b7484" stroke-width="1.5"
            stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <rect class="box gray" x="20" y="50" width="170" height="64"/>
  <text class="t title" x="105" y="74" text-anchor="middle" dominant-baseline="central">Kaggle</text>
  <text class="ts sub"  x="105" y="94" text-anchor="middle" dominant-baseline="central">Olist, 9 archivos csv</text>
  <line class="arr" x1="190" y1="82" x2="204" y2="82" marker-end="url(#a)"/>

  <rect class="box purple" x="210" y="50" width="170" height="64"/>
  <text class="t title" x="295" y="74" text-anchor="middle" dominant-baseline="central">dlt · GCS raw</text>
  <text class="ts sub"  x="295" y="94" text-anchor="middle" dominant-baseline="central">Parquet, retry, schema</text>
  <line class="arr" x1="380" y1="82" x2="394" y2="82" marker-end="url(#a)"/>

  <rect class="box purple" x="400" y="50" width="170" height="64"/>
  <text class="t title" x="485" y="74" text-anchor="middle" dominant-baseline="central">Spark 3 · Dataproc</text>
  <text class="ts sub"  x="485" y="94" text-anchor="middle" dominant-baseline="central">Limpieza distribuida</text>
  <line class="arr" x1="570" y1="82" x2="584" y2="82" marker-end="url(#a)"/>

  <rect class="box teal" x="590" y="50" width="170" height="64"/>
  <text class="t title" x="675" y="74" text-anchor="middle" dominant-baseline="central">BigQuery · olist_raw</text>
  <text class="ts sub"  x="675" y="94" text-anchor="middle" dominant-baseline="central">External tables</text>
  <line class="arr" x1="760" y1="82" x2="774" y2="82" marker-end="url(#a)"/>

  <rect class="box teal" x="780" y="50" width="170" height="64"/>
  <text class="t title" x="865" y="74" text-anchor="middle" dominant-baseline="central">dbt · 3 capas</text>
  <text class="ts sub"  x="865" y="94" text-anchor="middle" dominant-baseline="central">Staging, interm., marts</text>
  <line class="arr" x1="950" y1="82" x2="964" y2="82" marker-end="url(#a)"/>

  <rect class="box gray" x="970" y="50" width="170" height="64"/>
  <text class="t title" x="1055" y="74" text-anchor="middle" dominant-baseline="central">Streamlit · sklearn</text>
  <text class="ts sub"  x="1055" y="94" text-anchor="middle" dominant-baseline="central">Dashboards + ML</text>

  <text class="ts sub" x="105"  y="136" text-anchor="middle">Fuente</text>
  <text class="ts sub" x="295"  y="136" text-anchor="middle">Ingesta</text>
  <text class="ts sub" x="485"  y="136" text-anchor="middle">Procesamiento</text>
  <text class="ts sub" x="675"  y="136" text-anchor="middle">Warehouse</text>
  <text class="ts sub" x="865"  y="136" text-anchor="middle">Transformación</text>
  <text class="ts sub" x="1055" y="136" text-anchor="middle">Consumo</text>
</svg>
"""

components.html(PIPELINE_SVG, height=190)

st.caption(
    "Orquestado por **Kestra** (4 flows encadenables) e infraestructura provisionada "
    "con **Terraform** en un solo comando."
)

st.divider()

# ------------------------------------------------------------------ Componentes
st.subheader("Componentes y su rol")

COMPONENTES = [
    ("Terraform", "Infraestructura", "Buckets, datasets, cluster, SA e IAM", "IaC reproducible"),
    ("dlt + Kestra", "Ingesta", "Kaggle → GCS raw en parquet", "Retry y schema inference"),
    ("Spark 3 · Dataproc", "Procesamiento", "Limpieza y tipado distribuido, 2 workers", "Escalabilidad horizontal"),
    ("GCS + BigQuery", "Almacenamiento", "Data lake y warehouse serverless", "Alta disponibilidad gestionada"),
    ("dbt", "Transformación", "Modelo dimensional en 3 capas", "94 tests automatizados"),
    ("Streamlit + sklearn", "Analítica", "Dashboards y segmentación ML", "Caché de queries, TTL 1h"),
]

for fila in range(0, len(COMPONENTES), 3):
    for col, (tec, capa, rol, garantia) in zip(st.columns(3), COMPONENTES[fila : fila + 3]):
        with col:
            with st.container(border=True):
                st.caption(capa.upper())
                st.markdown(f"**{tec}**")
                st.write(rol)
                st.markdown(
                    f"<span style='background:#ede9fd;color:#4a3bb0;padding:3px 9px;"
                    f"border-radius:6px;font-size:12px'>{garantia}</span>",
                    unsafe_allow_html=True,
                )

st.divider()

# ------------------------------------------------------------------ Modelo dimensional
st.subheader("Capa Gold — Modelado dimensional de Kimball (olist_marts)")
st.caption(
    "Esquema en estrella: tres tablas de hechos rodeadas de cinco dimensiones conformadas. "
    "Las uniones usan llaves surrogate generadas en el modelo; FK = clave foránea hacia la dimensión."
)

MERMAID = """
<div class="mermaid">
erDiagram
  DIM_ORDERS    ||--o{ FCT_ORDER_ITEMS   : "contiene"
  DIM_CUSTOMERS ||--o{ FCT_ORDER_ITEMS   : "compra"
  DIM_PRODUCTS  ||--o{ FCT_ORDER_ITEMS   : "aparece en"
  DIM_SELLERS   ||--o{ FCT_ORDER_ITEMS   : "vende"
  DIM_DATES     ||--o{ FCT_ORDER_ITEMS   : "fecha de"
  DIM_ORDERS    ||--o{ FCT_PAYMENTS      : "se paga con"
  DIM_ORDERS    ||--|| FCT_ORDER_REVIEWS : "es evaluada por"

  DIM_CUSTOMERS {
    string customer_key PK
    string customer_id
    string customer_unique_id
    string city
    string state
  }
  DIM_PRODUCTS {
    string product_key PK
    string product_id
    string product_category_name
    string product_category
    float  product_weight_g
  }
  DIM_DATES {
    string date_key PK
    date   calendar_date
    int    year
    int    month
    int    day_of_month
  }
  DIM_ORDERS {
    string order_key PK
    string order_id
    string order_status
    date   order_purchase_date
    int    delivery_days
    int    delivery_vs_estimate_days
    bool   is_delivered_on_time
  }
  DIM_SELLERS {
    string seller_key PK
    string seller_id
    string city
    string state
  }
  FCT_ORDER_ITEMS {
    string order_item_key PK
    string order_key FK
    string customer_key FK
    string product_key FK
    string seller_key FK
    string date_key FK
    float  price
    float  freight_value
    float  total_item_value
  }
  FCT_ORDER_REVIEWS {
    string review_key PK
    string order_key FK
    string customer_key FK
    string date_key FK
    int    review_score
    string review_comment_title
    string review_comment_message
    bool   is_positive_review
    bool   has_comment
  }
  FCT_PAYMENTS {
    string payment_key PK
    string order_key FK
    string customer_key FK
    string date_key FK
    int    payment_sequential
    float  payment_value
    int    payment_installments
    string payment_type
  }
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
      darkMode: true,
      background: 'transparent',
      primaryColor: '#2b2560',
      primaryBorderColor: '#7f77dd',
      primaryTextColor: '#e8eaed',
      lineColor: '#6b7484',
      textColor: '#c3c2b7',
      fontSize: '13px',
    },
  });
</script>
"""

components.html(MERMAID, height=620, scrolling=True)

with st.expander("Notas del modelo"):
    st.markdown(
        """
**Grano de cada hecho**
- `fct_order_items` — 1 fila por ítem del pedido (`order_item_id`) · 112.7k filas
- `fct_payments` — 1 fila por pago (`payment_sequential`) · 103.9k filas
- `fct_order_reviews` — 1 fila por review (`review_id`) · 98.7k filas

**Convenciones**
- Las uniones se realizan mediante llaves surrogate generadas en el modelo
  (`customer_key`, `order_key`, `product_key`, `seller_key`, `date_key`).
- Los tres hechos incluyen `customer_key` y `order_key`; en el diagrama se omiten
  algunas relaciones hacia `dim_customers` y `dim_dates` para mantenerlo legible.
- `dim_products` incluye la categoría original en portugués y su traducción al inglés.
"""
    )

st.divider()

# ------------------------------------------------------------------ Garantías
st.subheader("Garantías del pipeline")

tab_seg, tab_int, tab_rend = st.tabs(
    ["🔒 Seguridad", "✅ Integridad de datos", "⚡ Rendimiento y disponibilidad"]
)

with tab_seg:
    st.caption("Alineado con ISO/IEC 27001")
    st.markdown(
        """
- Service Account con **mínimo privilegio**: roles separados por servicio, nunca `owner`
- Buckets con `uniform_bucket_level_access`, sin ACLs por objeto
- Credenciales fuera del repositorio (`.gitignore`), inyectadas como secretos en Kestra y Streamlit
- Lifecycle rules: los datos raw se purgan a los 90 días (minimización de datos)
"""
    )

with tab_int:
    st.caption("Alineado con ISO/IEC 25012")
    m1, m2, m3 = st.columns(3)
    m1.metric("Tests ejecutados por corrida", "94")
    m2.metric("Cobertura de integridad referencial", "100%")
    m3.metric("Tablas con trazabilidad temporal", "8 / 8")
    st.markdown(
        """
- Tipos de test: `unique`, `not_null`, `relationships`, `accepted_values`
- Integridad referencial verificada entre todos los hechos y sus dimensiones
- Columna `processed_at` en cada tabla, para trazabilidad temporal
- Deduplicación documentada: geolocation por zip, reviews por orden
"""
    )

with tab_rend:
    st.markdown(
        """
**Rendimiento**
- Las agregaciones se ejecutan **en BigQuery**, no en la aplicación
- `st.cache_data` con TTL de una hora: una query por hora por vista, no por usuario
- Marts materializados como tablas; staging como vistas (balance costo/velocidad)

**Alta disponibilidad**
- GCS y BigQuery son servicios gestionados multi-zona por defecto
- El pipeline es idempotente: cualquier flow puede reejecutarse sin efectos colaterales
"""
    )

st.divider()

st.caption(
    "Repositorio: github.com/picantitoDev/bigdata-olist-pipeline — infraestructura, ingesta, "
    "procesamiento, transformación y esta aplicación en un único monorepo versionado."
)
