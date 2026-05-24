resource "google_service_account" "pipeline_sa" {
  account_id   = "olist-pipeline-sa"
  display_name = "Cuenta de servicio del pipeline Olist"
  description  = "Cuenta de servicio para BigQuery y Google Cloud Storage"
  project      = var.project_id
}

resource "google_project_iam_member" "sa_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "sa_dataproc_admin" {
  project = var.project_id
  role    = "roles/dataproc.admin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "sa_dataproc_worker" {
  project = var.project_id
  role    = "roles/dataproc.worker"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "sa_dataproc_editor" {
  project = var.project_id
  role    = "roles/dataproc.editor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_service_account_key" "pipeline_sa_key" {
  service_account_id = google_service_account.pipeline_sa.name
}

resource "local_file" "sa_key_file" {
  content  = base64decode(google_service_account_key.pipeline_sa_key.private_key)
  filename = "${path.module}/../keys/google-creds.json"
}
