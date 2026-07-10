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

resource "null_resource" "keys_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/../keys"
  }
}

resource "local_file" "sa_json_file" {
  depends_on = [null_resource.keys_dir]
  content    = base64decode(google_service_account_key.pipeline_sa_key.private_key)
  filename   = "${path.module}/../keys/google-creds.json"
}

resource "local_file" "streamlit_secrets" {
  depends_on      = [null_resource.dlt_dir]
  filename        = "${path.module}/../dashboard/.streamlit/secrets.toml"
  file_permission = "0600"

  content = <<-EOT
    [gcp_service_account]
    type                        = "service_account"
    project_id                  = "${var.project_id}"
    private_key_id              = "${local.sa_key.private_key_id}"
    private_key                 = "${replace(local.sa_key.private_key, "\n", "\\n")}"
    client_email                = "${google_service_account.pipeline_sa.email}"
    client_id                   = "${local.sa_key.client_id}"
    auth_uri                    = "https://accounts.google.com/o/oauth2/auth"
    token_uri                   = "https://oauth2.googleapis.com/token"
  EOT
}

resource "null_resource" "streamlit_secrets_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/../dashboard/.streamlit"
  }
}