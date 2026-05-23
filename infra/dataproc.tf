resource "google_dataproc_cluster" "spark_cluster" {
  name    = var.dataproc_cluster_name
  project = var.project_id
  region  = var.region

  labels = {
    environment = var.environment
    project     = var.project_name
  }

  cluster_config {
    staging_bucket = google_storage_bucket.staging.name
    temp_bucket    = google_storage_bucket.temp.name

    endpoint_config {
      enable_http_port_access = true
    }

    master_config {
      num_instances = 1
      machine_type  = var.master_machine_type
      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 100
      }
    }

    worker_config {
      num_instances = var.num_workers
      machine_type  = var.worker_machine_type
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 200
      }
    }

    software_config {
      image_version       = var.dataproc_image_version
      optional_components = ["JUPYTER"]
      override_properties = {
        "dataproc:dataproc.allow.zero.workers"    = "false"
        "spark:spark.sql.legacy.timeParserPolicy" = "LEGACY"
        "spark:spark.sql.adaptive.enabled"        = "true"
      }
    }

    gce_cluster_config {
      service_account        = google_service_account.pipeline_sa.email
      service_account_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
      metadata = {
        "PIP_PACKAGES" = "google-cloud-storage google-cloud-bigquery pyarrow"
      }
    }

    initialization_action {
      script      = "gs://${google_storage_bucket.scripts.name}/init/bootstrap.sh"
      timeout_sec = 300
    }
  }

  depends_on = [
    google_project_service.services,
    google_storage_bucket.staging,
    google_storage_bucket.temp,
    google_storage_bucket.scripts,
    google_storage_bucket_object.bootstrap_script,
    google_service_account.pipeline_sa,
    google_project_iam_member.sa_dataproc_worker,
    google_project_iam_member.sa_dataproc_admin,
    google_project_iam_member.sa_dataproc_editor,
    google_project_iam_member.sa_bigquery_admin,
    google_project_iam_member.sa_storage_admin
  ]
}
