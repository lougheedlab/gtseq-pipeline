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
            samples.append(
                Sample(
                    name=row["Sample_name"],
                    plate=row["Plate_ID"],
                    i7_name=row["i7_name"],
                    i5_name=row["i5_name"],
                )
            )

    return samples
