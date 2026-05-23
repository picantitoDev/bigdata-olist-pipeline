resource "google_storage_bucket" "raw" {
  name                        = var.gcs_raw_bucket_name
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    layer       = "raw"
    project     = var.project_name
  }
}

resource "google_storage_bucket" "processed" {
  name                        = var.gcs_processed_bucket_name
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  labels = {
    environment = var.environment
    layer       = "processed"
    project     = var.project_name
  }
}

resource "google_storage_bucket" "temp" {
  name                        = "${var.project_id}-dataproc-temp"
  project                     = var.project_id
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 7 }
    action { type = "Delete" }
  }

  labels = {
    environment = var.environment
    layer       = "temp"
    project     = var.project_name
  }
}

resource "google_storage_bucket" "staging" {
  name                        = "${var.project_id}-dataproc-staging"
  project                     = var.project_id
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 30 }
    action { type = "Delete" }
  }

  labels = {
    environment = var.environment
    layer       = "staging"
    project     = var.project_name
  }
}

resource "google_storage_bucket" "scripts" {
  name                        = "${var.project_id}-dataproc-scripts"
  project                     = var.project_id
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    layer       = "scripts"
    project     = var.project_name
  }
}

resource "google_storage_bucket_object" "bootstrap_script" {
  name   = "init/bootstrap.sh"
  bucket = google_storage_bucket.scripts.name
  source = "../scripts/bootstrap.sh"
}
