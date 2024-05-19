import subprocess
from pathlib import Path

from ..models import Params, Sample

__all__ = ["call_alleles"]


def call_alleles(
    params: Params,
    run_work_dir: Path,
    samples: list[Sample],
    sample_bams: dict[str, Path],
    ref_genome: Path,
):
    allele_file = Path(__file__).parent.parent / "alleles" / f"{params.species}.tsv"
    assert allele_file.exists()

    genotypes_dir = run_work_dir / "genotypes"
    genotypes_dir.mkdir()

    bam_list = genotypes_dir / "bams.txt"

    with open(bam_list, "w") as fh:
        for f in sample_bams.values():
            fh.write(f"{f}\n")
