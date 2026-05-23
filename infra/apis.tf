resource "google_project_service" "services" {
  for_each = toset([
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com",
    "dataproc.googleapis.com",
    "cloudresourcemanager.googleapis.com"
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
