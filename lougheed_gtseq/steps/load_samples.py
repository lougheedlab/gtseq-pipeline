import csv
import re
import traceback
from logging import Logger
from pathlib import Path

from lougheed_gtseq.models import Sample

__all__ = ["load_samples"]


RE_VARIABLE_SPACED_DASH = re.compile(r"\s*[-_]\s*")
RE_MULTI_SPACE = re.compile(r"\s+")


def load_samples(sample_csv: Path, logger: Logger) -> list[Sample]:
    samples: list[Sample] = []

    with open(sample_csv) as fh:
        reader = csv.DictReader(fh)

        row: dict[str, str]
        for ri, row in enumerate(reader):
            # normalize keys + get rid of strange characters like zero-width spaces (which have somehow snuck in!)
            norm_row = {
                k.lower().replace(" ", "_").strip().encode("ascii", "ignore").decode("utf-8"): v for k, v in row.items()
            }
            try:
                samples.append(
                    Sample(
                        name=RE_MULTI_SPACE.sub(
                            RE_VARIABLE_SPACED_DASH.sub(norm_row["sample_name"].replace("/", "_"), "-"), " "
                        ),
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
                exit(1)

    return samples
