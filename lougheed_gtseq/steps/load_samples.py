import csv
import traceback
from logging import Logger
from pathlib import Path

from lougheed_gtseq.models import Sample

__all__ = ["load_samples"]


def load_samples(sample_csv: Path, logger: Logger) -> list[Sample]:
    samples: list[Sample] = []

    with open(sample_csv) as fh:
        reader = csv.DictReader(fh)

        row: dict[str, str]
        for ri, row in enumerate(reader):
            norm_row = {k.lower().replace(" ", "_").strip(): v for k, v in row.items()}
            try:
                samples.append(
                    Sample(
                        name=norm_row["sample_name"],
                        plate=norm_row["plate_id"],
                        i7_name=norm_row["i7_name"],
                        i5_name=norm_row["i5_name"],
                    )
                )
            except KeyError:
                logger.critical(
                    "row %d: missing one of (sample_name, plate_id, i7_name, i5_name) in CSV record (%s)",
                    ri,
                    ", ".join(norm_row.keys()),
                )
                traceback.print_exc()

    return samples
