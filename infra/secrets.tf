locals {
  sa_key = jsondecode(base64decode(google_service_account_key.pipeline_sa_key.private_key))
}

resource "null_resource" "dlt_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/../.dlt"
  }
}

resource "local_file" "dlt_secrets" {
  depends_on      = [null_resource.dlt_dir]
  filename        = "${path.module}/../.dlt/secrets.toml"
  file_permission = "0600"

  content = <<-EOT
    [destination.filesystem]
    bucket_url = "gs://${google_storage_bucket.raw.name}"

    [destination.filesystem.credentials]
    project_id   = "${var.project_id}"
    private_key  = "${replace(local.sa_key.private_key, "\n", "\\n")}"
    client_email = "${google_service_account.pipeline_sa.email}"
  EOT
}