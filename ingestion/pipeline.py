import logging

import dlt

from .config import DATASET_NAME, DOWNLOAD_DIR, KAGGLE_DATASET, PIPELINE_NAME
from .ingestion import download_dataset
from .source import olist_source

log = logging.getLogger(__name__)


def create_pipeline() -> dlt.Pipeline:
    """
    Crea el pipeline de dlt apuntando al destino filesystem (GCS).
    """
    return dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination="filesystem",
        dataset_name=DATASET_NAME,
    )


def run():
    """
    Orquesta la descarga, creación del pipeline y carga a GCS.
    """
    data_dir = download_dataset(KAGGLE_DATASET, DOWNLOAD_DIR)

    pipeline = create_pipeline()

    log.info("Iniciando pipeline dlt -> GCS")

    load_info = pipeline.run(
        olist_source(data_dir),
        write_disposition="replace",
        loader_file_format="parquet",
    )

    log.info("Pipeline completado correctamente")
    log.info(load_info)

    return load_info
