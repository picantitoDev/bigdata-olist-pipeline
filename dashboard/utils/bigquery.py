"""Conexión a BigQuery con caché de recursos y datos."""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT_ID = "big-data-495719"
DATASET_MARTS = "olist_marts"


@st.cache_resource
def get_client() -> bigquery.Client:
    """Cliente BigQuery singleton, autenticado vía service account."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"],
    )


@st.cache_data(ttl=3600, show_spinner="Consultando BigQuery...")
def run_query(query: str):
    """Ejecuta una query y retorna DataFrame. Cache de 1 hora."""
    client = get_client()
    return client.query(query).to_dataframe()
