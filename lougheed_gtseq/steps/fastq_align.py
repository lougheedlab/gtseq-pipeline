import pysam
import subprocess
from pathlib import Path

from ..barcodes import get_i7_barcode_numeral, normalize_i5_coordinate
from ..logger import logger
from ..models import Params, Sample

__all__ = ["fastq_align"]


def align_fastq_to_bam(ref_genome: Path, fq: Path, sorted_bam: Path, processes: int):
    align_p = subprocess.Popen(
        (
            "bwa",
            "mem",
            "-t",
            str(processes),
            str(ref_genome),
            str(fq),
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    bam_p = subprocess.Popen(
        ("samtools", "view", "-Sb", "-"),
        stdin=align_p.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    with open(sorted_bam, "wb") as fh:
        subprocess.check_call(
            ("samtools", "sort", "-@", str(processes), "-"),
            stdin=bam_p.stdout,
            stdout=fh,
            stderr=subprocess.DEVNULL,
        )

    subprocess.check_call(("samtools", "index", str(sorted_bam)))


def fastq_align(
    params: Params,
    run_work_dir: Path,
    samples: list[Sample],
    sample_files: dict[int, Path],
    ref_genome: Path,
) -> dict[int, Path]:
    align = run_work_dir / "align"
    align.mkdir(exist_ok=True)

    sample_bams: dict[int, Path] = {}

    for si, sample in enumerate(samples):
        fq = sample_files[si]
        with pysam.FastxFile(str(fq)) as fqf:
            n_reads = sum(1 for _ in fqf)

        logger.info(f"Aligning %d reads for sample: %s", n_reads, sample)

        i7 = get_i7_barcode_numeral(sample.i7_name)
        i5 = normalize_i5_coordinate(sample.i5_name)
        sorted_bam = align / f"GTSeq_{i7}_{i5}_{sample.plate}_{sample.name}.bam"

        # Run the alignment -> compress -> sort task
        align_fastq_to_bam(ref_genome, fq, sorted_bam, params.processes)

        sample_bams[si] = sorted_bam

    return sample_bams
