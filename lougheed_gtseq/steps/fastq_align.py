import subprocess
from pathlib import Path

from ..barcodes import get_i7_barcode_numeral, normalize_i5_coordinate
from ..models import Params, Sample

__all__ = ["fastq_align"]


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
        i7 = get_i7_barcode_numeral(sample.i7_name)
        i5 = normalize_i5_coordinate(sample.i5_name)
        sorted_bam = align / f"GTSeq_{i7}_{i5}_{sample.plate}_{sample.name}.bam"

        align_p = subprocess.Popen(
            (
                "bwa",
                "mem",
                "-t",
                str(params.processes),
                str(ref_genome),
                str(fq),
            ),
            stdout=subprocess.PIPE,
        )

        bam_p = subprocess.Popen(
            ("samtools", "view", "-Sb", "-"),
            stdin=align_p.stdout,
            stdout=subprocess.PIPE,
        )

        with open(sorted_bam, "wb") as fh:
            subprocess.check_call(
                ("samtools", "sort", "-@", str(params.processes), "-"),
                stdin=bam_p.stdout,
                stdout=fh,
            )

        subprocess.check_call(("samtools", "index", str(sorted_bam)))

        sample_bams[si] = sorted_bam

    return sample_bams
