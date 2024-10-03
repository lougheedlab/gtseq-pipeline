import numpy as np
import pysam
import termplotlib as tpl
from pathlib import Path

__all__ = ["run_snp_success"]


def run_snp_success(vcf: Path):
    with pysam.VariantFile(str(vcf)) as vf:
        sps = []
        for variant in vf.fetch():
            success_percent = (
                sum(1 for samp in variant.samples.values() if samp["GT"][0] is not None) / len(variant.samples) * 100
            )
            print(f"{variant.contig.rjust(14)} {str(variant.pos).ljust(9)} {success_percent:.1f}%")
            sps.append(success_percent)

    sps_counts, sps_edges = np.histogram(sps, bins=20)

    prop_fig = tpl.figure()
    prop_fig.hist(sps_counts, sps_edges, orientation="horizontal", force_ascii=False)
    prop_fig.show()
