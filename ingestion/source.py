import logging
from pathlib import Path

import dlt
from dlt.sources.filesystem import filesystem, read_csv

log = logging.getLogger(__name__)


@dlt.source(name="brazilian_ecommerce")
def olist_source(data_dir: Path):
    """
    Crea un recurso dlt por cada archivo CSV en data_dir.
    """
    for csv_file in sorted(data_dir.glob("*.csv")):

        table_name = (
            csv_file.stem
            .replace("-", "_")
            .replace("olist_", "")
            .replace("_dataset", "")
        )

        log.info(
            "Registrando recurso: %s -> tabla: %s",
            csv_file.name,
            table_name,
        )

        yield (
            filesystem(bucket_url=str(data_dir), file_glob=csv_file.name)
            | read_csv()
        ).with_name(table_name)
