resource "google_bigquery_dataset" "raw" {
  dataset_id    = var.bq_raw_dataset
  friendly_name = "Dataset Raw"
  description   = "Datos originales del proyecto Olist"
  location      = var.region
  project       = var.project_id
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    layer       = "raw"
  }
}

resource "google_bigquery_dataset" "staging" {
  dataset_id    = var.bq_staging_dataset
  friendly_name = "Dataset Staging"
  description   = "Modelos limpios y tipados para transformación"
  location      = var.region
  project       = var.project_id
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    layer       = "staging"
  }
}

resource "google_bigquery_dataset" "intermediate" {
  dataset_id    = var.bq_intermediate_dataset
  friendly_name = "Dataset Intermediate"
  description   = "Transformaciones y modelos intermedios"
  location      = var.region
  project       = var.project_id
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    layer       = "intermediate"
  }
}

resource "google_bigquery_dataset" "marts" {
  dataset_id    = var.bq_marts_dataset
  friendly_name = "Dataset Marts"
  description   = "Tablas analíticas finales para consumo y visualización"
  location      = var.region
  project       = var.project_id
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
    layer       = "marts"
  }
}
