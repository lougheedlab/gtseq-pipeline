import sys
from csv import DictReader, DictWriter
from pathlib import Path

__all__ = ["combine_sex_markers"]


def combine_sex_markers(files: list[Path]):
    """
    Combines sex genotypes from multiple different batches into a single file.
    :param files: A list of CSV files, output from Nate Campbell's GTseq pipeline.
    """
    records = []

    for file in files:
        with open(file, "r") as fh:
            reader = DictReader(fh)
            for record in reader:
                if "" in record:
                    del record[""]
                records.append(record)

    records.sort(key=lambda r: r["Sample"])

    writer = DictWriter(sys.stdout, fieldnames=list(records[0].keys()))
    writer.writerows(records)
