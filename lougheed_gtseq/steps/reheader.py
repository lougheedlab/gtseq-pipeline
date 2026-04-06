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
    with VariantFile(str(vcf)) as vf:
        if (n_samples := len(samples)) != (n_vcf := len(vf.header.samples)):
            logger.critical("sample count mismatch between sample CSV (n=%d) and VCF (n=%d)", n_samples, n_vcf)
            exit(1)

    subprocess.check_call(("bcftools", "reheader", "--samples-list", ",".join(s.full_name() for s in samples)))


def run_reheader(params, logger: Logger):
    """
    Runs the reheader command-line utility.
    """
    samples = load_samples(params.batch, params.samples, logger)
    reheader_vcf(samples, params.vcf, logger)
