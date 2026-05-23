# VARIABLES PRINCIPALES DE GCP

variable "project_id" {
  description = "ID del proyecto en Google Cloud Platform"
  type        = string
}

variable "region" {
  description = "Región utilizada para los recursos de GCP"
  type        = string
  default     = "US"
}

variable "environment" {
  description = "Nombre del entorno (dev, staging o prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Nombre corto del proyecto usado en labels"
  type        = string
  default     = "olist-data-platform"
}

# VARIABLES DE GOOGLE CLOUD STORAGE
variable "gcs_raw_bucket_name" {
  description = "Nombre del bucket GCS para datos raw de Olist"
  type        = string
}

variable "gcs_processed_bucket_name" {
  description = "Nombre del bucket GCS para datos procesados de Olist"
  type        = string
}

# VARIABLES DE BIGQUERY

variable "bq_raw_dataset" {
  description = "Dataset raw de BigQuery para datos originales"
  type        = string
  default     = "olist_raw"
}

variable "bq_staging_dataset" {
  description = "Dataset staging de BigQuery para modelos limpios y tipados"
  type        = string
  default     = "olist_staging"
}

variable "bq_intermediate_dataset" {
  description = "Dataset intermediate de BigQuery para transformaciones intermedias"
  type        = string
  default     = "olist_intermediate"
}

variable "bq_marts_dataset" {
  description = "Dataset marts de BigQuery para tablas analíticas finales"
  type        = string
  default     = "olist_marts"
}

# VARIABLES DE DATAPROC

variable "dataproc_cluster_name" {
  description = "Nombre del cluster Dataproc"
  type        = string
}

variable "master_machine_type" {
  description = "Tipo de máquina para el nodo master"
  type        = string
}

variable "worker_machine_type" {
  description = "Tipo de máquina para los workers"
  type        = string
}

variable "num_workers" {
  description = "Número de workers del cluster Dataproc"
  type        = number
}

variable "dataproc_image_version" {
  description = "Versión de imagen de Dataproc"
  type        = string
}