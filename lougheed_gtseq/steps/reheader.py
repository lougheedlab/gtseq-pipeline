import subprocess

from logging import Logger
from pathlib import Path
from pysam import VariantFile

from ..models import Sample
from .load_samples import load_samples

__all__ = [
    "reheader_vcf",
    "run_reheader",
]


def reheader_vcf(samples: list[Sample], vcf: Path, logger: Logger):
    """
    Re-headers a VCF from mpileup to normalized sample names with the batch ID present. The list of samples must be the
    same length as the number of sample columns in the VCF.
    :param samples: list of samples to generate new sample names from.
    :param vcf: path to VCF to reheader (in-place)
    :param logger: logger object
    :return:
    """

    vcf_path_str = str(vcf)

    with VariantFile(vcf_path_str) as vf:
        if (n_samples := len(samples)) != (n_vcf := len(vf.header.samples)):
            logger.critical("sample count mismatch between sample CSV (n=%d) and VCF (n=%d)", n_samples, n_vcf)
            exit(1)

    vcf_path_reheader = Path(vcf_path_str + ".reheader")

    with open(vcf_path_reheader, "w") as fh:
        for s in samples:
            fh.write(f"{s.full_name()}\n")

    try:
        subprocess.check_call(("bcftools", "reheader", "--samples", str(vcf_path_reheader), vcf_path_str))
    finally:
        vcf_path_reheader.unlink()


def run_reheader(params, logger: Logger):
    """
    Runs the reheader command-line utility.
    """
    samples = load_samples(params.batch, params.samples, logger)
    reheader_vcf(samples, params.vcf, logger)
