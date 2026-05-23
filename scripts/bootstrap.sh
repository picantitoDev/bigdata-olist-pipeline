#!/bin/bash
set -euxo pipefail

echo ">>> Instalando dependencias basicas..."

# Instalar dependencias basicas
pip install --upgrade pip

pip install \
  google-cloud-storage==2.14.0 \
  google-cloud-bigquery==3.14.0 \
  pyarrow==14.0.0 \
  pandas==2.1.0 \
  pyyaml==6.0.1 \
  scikit-learn==1.3.0 \
  xgboost==2.0.0 \
  matplotlib==3.8.0 \
  seaborn==0.13.0

echo ">>> Bootstrap completado."