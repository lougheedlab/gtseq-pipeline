import pysam
import re

from pathlib import Path
from typing import TextIO

from ..barcodes import get_i7_barcode_numeral, get_i7_barcode, normalize_i5_coordinate, get_i5_barcode
from ..logger import logger
from ..models import Sample

__all__ = ["fastq_split"]

READ_INDEX_PATTERN = re.compile(r"^[ACGT]{6}\+[ACGT]{6}$")


def fastq_split(samples: list[Sample], fastq_dir: Path) -> dict[int, Path]:
    fq_path = next(fastq_dir.glob("Undetermined_*_R1_*.fastq.gz"), None)
    assert fq_path is not None

    split_dir = fastq_dir / "split"
    split_dir.mkdir(exist_ok=True)

    index_seqs_lookup: dict[str, int] = {
        f"{get_i7_barcode(s.i7_name)}+{get_i5_barcode(s.i5_name)}": i
        for i, s in enumerate(samples)
    }

    logger.info(f"Using index lookup table for %d samples:", len(samples))
    for s, idx in index_seqs_lookup.items():
        logger.info(f"%s: %d --> %s", s.rjust(30), idx, samples[idx])

    sample_files: dict[int, Path] = {}
    sample_file_handles: dict[int, TextIO] = {}

    logger.info(f"Splitting reads from {fq_path}")
    try:
        with pysam.FastxFile(str(fq_path)) as fq:
            for read in fq:
                read_index = read.comment.split(":")[-1]
                if not READ_INDEX_PATTERN.match(read_index):
                    logger.debug(
                        f"Could not find read index sequences in read {read.name} {read.comment}; skipping read"
                    )
                    continue

                if read_index not in index_seqs_lookup:
                    logger.debug(f"Could not find read index {read_index} in lookup table; skipping read")
                    continue

                si = index_seqs_lookup[read_index]
                s = samples[si]

                if si not in sample_files:
                    i7 = get_i7_barcode_numeral(s.i7_name)
                    i5 = normalize_i5_coordinate(s.i5_name)
                    new_sample_file = split_dir / f"GTSeq_{i7}_{i5}_{s.plate}_{s.name}.fastq"
                    sample_files[si] = new_sample_file
                    sample_file_handles[si] = open(new_sample_file, mode="w")

                fh = sample_file_handles[si]
                fh.write(str(read) + "\n")

    finally:
        for v in sample_file_handles.values():
            v.close()

    return sample_files
