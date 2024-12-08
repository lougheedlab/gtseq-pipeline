import shutil
import subprocess
from pathlib import Path

from ..models import Params

__all__ = ["call_alleles"]


def call_alleles(
    params: Params,
    run_work_dir: Path,
    sample_bams: dict[int, Path],
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

    pileup_p = subprocess.Popen(
        (
            "bcftools",
            "mpileup",
            "-f",
            str(ref_genome),
            "-T",
            str(allele_file),
            "--annotate",
            "AD,DP",
            "--bam-list",
            str(bam_list),
        ),
        stdout=subprocess.PIPE,
    )

    vcf_name = params.vcf.name
    vcf_run_out = run_work_dir / vcf_name

    subprocess.check_call(
        (
            "bcftools",
            "call",
            "-mv",
            "-C",
            "alleles",
            "-T",
            str(allele_file),
            "--format-fields",
            "gq",
            "-o",
            str(vcf_run_out),
        ),
        stdin=pileup_p.stdout,
    )

    # Copy the VCF output from the run work directory to the final location
    shutil.copy(vcf_run_out, params.vcf, follow_symlinks=True)
