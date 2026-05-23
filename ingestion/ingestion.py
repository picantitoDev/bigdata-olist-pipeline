import logging
import shutil
import zipfile
from pathlib import Path

from tenacity import retry, stop_after_attempt, wait_fixed

log = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def download_dataset(dataset: str, dest: Path) -> Path:
    """
    Descarga y extrae un dataset de Kaggle.

    Retorna:
        Ruta que contiene los archivos CSV extraídos.
    """
    import kaggle

    if dest.exists():
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=True)

    log.info("Descargando dataset: %s", dataset)

    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(dataset, path=dest, unzip=False)

    zips = list(dest.glob("*.zip"))

    if not zips:
        raise FileNotFoundError(
            f"No se encontró ningún archivo ZIP después de descargar el dataset en {dest}"
        )

    zip_file = zips[0]

    log.info("Extrayendo: %s", zip_file.name)

    with zipfile.ZipFile(zip_file, "r") as zf:
        zf.extractall(dest)

    zip_file.unlink()

    csvs = sorted(dest.glob("*.csv"))

    if not csvs:
        raise FileNotFoundError("No se encontraron archivos CSV después de la extracción")

    log.info("Se encontraron %d archivos CSV", len(csvs))

    for csv in csvs:
        log.info("  - %s", csv.name)

    return dest
