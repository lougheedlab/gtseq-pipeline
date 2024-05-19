import subprocess
from pathlib import Path

from ..models import Params, Sample

__all__ = ["fastq_align"]


def fastq_align(
    params: Params,
    run_work_dir: Path,
    samples: list[Sample],
    sample_files: dict[str, Path],
    ref_genome: Path,
) -> dict[str, Path]:
    align = run_work_dir / "align"

    sample_bams: dict[str, Path] = {}

    for sample in samples:
        fq = sample_files[sample.name]
        sorted_bam = align / f"GTSeq_{sample.name}.bam"

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
                ("samtools", "sort", "-@", str(params.processes)),
                stdin=bam_p.stdin,
                stdout=fh,
            )

        subprocess.check_call(("samtools", "index", str(sorted_bam)))

        sample_bams[sample.name] = sorted_bam

    return sample_bams
