import csv
from pathlib import Path

from lougheed_gtseq.models import Sample

__all__ = ["load_samples"]


def load_samples(sample_csv: Path) -> list[Sample]:
    samples: list[Sample] = []

    with open(sample_csv) as fh:
        reader = csv.DictReader(fh)

        row: dict[str, str]
        for row in reader:
            norm_row = {k.lower().replace(" ", "_"): v for k, v in row.items()}
            samples.append(
                Sample(
                    name=norm_row["sample_name"],
                    plate=norm_row["plate_id"],
                    i7_name=norm_row["i7_name"],
                    i5_name=norm_row["i5_name"],
                )
            )

    return samples
