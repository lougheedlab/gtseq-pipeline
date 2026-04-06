import matplotlib.pyplot as plt
import numpy as np
import pysam
import termplotlib as tpl
from pathlib import Path

__all__ = ["run_snp_success"]


def run_snp_success(vcf: Path):
    n_samples = 0
    with pysam.VariantFile(str(vcf)) as vf:
        sps = []
        for variant in vf.fetch():
            n_samples = max(n_samples, len(variant.samples))
            success_num = sum(1 for samp in variant.samples.values() if samp["GT"][0] is not None)
            success_denom = len(variant.samples)
            success_percent = success_num / success_denom * 100
            print(
                f"{variant.contig.rjust(14)} {str(variant.pos).ljust(9)} {success_percent:.1f}% "
                f"({success_num} / {success_denom})"
            )
            sps.append(success_percent)

    sps_counts, sps_edges = np.histogram(sps, bins=20)

    prop_fig = tpl.figure()
    prop_fig.hist(sps_counts, sps_edges, orientation="horizontal", force_ascii=False)
    prop_fig.show()

    plt.title(f"SNP call rate across {len(sps)} SNPs and {n_samples} samples")

    plt.stairs(sps_counts, sps_edges, fill=True)
    plt.xlabel("SNP call success %")
    plt.ylabel("# SNPs")
    plt.show()
