import matplotlib.pyplot as plt
import numpy as np
import pysam
import re
import shutil
import subprocess
import termplotlib as tpl
import uuid

from pathlib import Path
from typing import Literal

from ..logger import logger


__all__ = ["run_qc"]

sample_pattern = re.compile(r"GT[sS]eq_\d+_[A-Z\d]+_(PL|plate)_\d+_(?P<sample>[a-zA-Z0-9_\-#?]+)\..*\.bam")


def run_qc(
    work_dir: Path,
    vcf: Path,
    vcf_out: Path | None,
    min_dp: int,
    min_gq: int,
    min_prop: float,
    het_sigma: int,
    drop_failed: bool,
) -> None:
    vf = pysam.VariantFile(str(vcf))

    sample_genotypes: dict[str, list[tuple[str, str]]] = {}

    for s in vf.header.samples:
        if "control" in s.lower():  # TODO: parametrize
            logger.info(f"Skipping control sample: {s}")
            continue

        sample_genotypes[s] = []

    if vcf_out is None:
        out_name = str(vcf.stem) + f"_QC_minDP_{min_dp}_minGQ_{min_gq}.vcf"
        vcf_out_tmp = vcf.parent / f".tmp_{out_name}"
        vcf_out = vcf.parent / out_name
    else:
        vcf_out_tmp = vcf_out.parent / f".tmp_{str(uuid.uuid4())[:12]}.vcf"

    if not len(sample_genotypes):
        logger.error("No samples were found, exiting.")
        exit(1)

    logger.info(f"[QC] # samples = {len(sample_genotypes)}")
    logger.info(f"[QC] params: {min_dp=}, {min_gq=}, {min_prop=}, {drop_failed=}")

    with pysam.VariantFile(str(vcf_out_tmp), mode="w", header=vf.header) as vfo:

        for variant in vf.fetch():
            new_rec = variant.copy()

            lookup = (variant.ref, *variant.alts)

            for s, sv in variant.samples.items():
                if s not in sample_genotypes:
                    continue

                # sample_id = raw_sample_to_sample_id[s]

                if sv["DP"] and sv["DP"] >= min_dp and sv["GQ"] and sv["GQ"] > min_gq:
                    gt = tuple(lookup[i] for i in sv["GT"])
                else:
                    gt = (".", ".")
                    new_rec.samples[s]["GT"] = (None, None)

                sample_genotypes[s].append(gt)

            vfo.write(new_rec)

    # -- Whole-sample QC -----------------------------------------------------------------------------------------------

    # dict of [sample ID, (failure reason, failed value)]
    failed_samples: dict[str, tuple[Literal["prop_called", "heterozygosity"], float]] = {}

    sample_n_called: dict[str, int] = {}
    sample_p_called: dict[str, float] = {}
    sample_het: dict[str, float] = {}

    props = []

    # QC step: proportion called

    for ss, sg in sample_genotypes.items():
        n_called = sum(1 for gg in sg if "." not in gg)
        sample_n_called[ss] = n_called

        prop_called = n_called / len(sg)
        sample_p_called[ss] = prop_called

        props.append(prop_called)

        if not prop_called >= min_prop:
            failed_samples[ss] = ("prop_called", prop_called)

    # QC step: heterozygosity

    het_props = []

    for ss, sg in filter(lambda x: x[0] not in failed_samples, sample_genotypes.items()):
        n_hets = sum(1 for gg in sg if "." not in gg and len(set(gg)) > 1)
        prop_het = n_hets / sample_n_called[ss]
        het_props.append(prop_het)
        sample_het[ss] = prop_het

    het_prop_mean = np.mean(het_props)
    het_prop_sd = np.std(het_props)
    het_lb = het_prop_mean - het_sigma * het_prop_sd
    het_ub = het_prop_mean + het_sigma * het_prop_sd

    for ss, sg in filter(lambda x: x[0] not in failed_samples, sample_genotypes.items()):
        if not het_lb <= sample_het[ss] <= het_ub:  # 2 sigma of mean calculated pre-het-filtering
            failed_samples[ss] = ("heterozygosity", sample_het[ss])

    # Calculate final set of successful samples:
    success_samples = [ss for ss in sample_genotypes.keys() if ss not in failed_samples]

    # Save failed samples to text file
    with open(f"{vcf_out}.failed-samples.csv", "w") as fh:
        fh.write(f'"sample","failure reason","failure value"\n')
        for fs, fr in failed_samples.items():
            fh.write(f'"{fs}","{fr[0]}","{fr[1]}"\n')

    # QC plots:

    prop_title = f"Proportion-called distribution (fail: <{min_prop * 100:.1f}%)"
    logger.info(f"[QC] {prop_title}")
    prop_counts, prop_edges = np.histogram(props, bins=20)
    prop_fig = tpl.figure()
    prop_fig.hist(prop_counts, prop_edges, orientation="horizontal", force_ascii=False)
    prop_fig.show()

    prop_fig_g = plt.figure()
    plt.title(prop_title)
    plt.stairs(prop_counts, prop_edges, fill=True)
    plt.xlabel("proportion of SNPs called")
    plt.ylabel("# samples")
    plt.axvline(min_prop, color="#1111CC")
    prop_fig_g.savefig(f"{vcf}.prop_called.png", dpi=220)

    het_title = f"Heterozygosity distribution (before heterozygosity filtering; fail: <{het_lb:.3f} | >{het_ub:.3f})"
    logger.info(f"[QC] {het_title}")
    logger.info(f"[QC]   Heterozygosity: mean={np.mean(het_props):.3f}; stdev={np.std(het_props):.3f}")
    het_counts, het_bin_edges = np.histogram(het_props, bins=25)
    het_fig = tpl.figure()
    het_fig.hist(het_counts, het_bin_edges, orientation="horizontal", force_ascii=False)
    het_fig.show()

    het_fig_g = plt.figure(figsize=(8, 4))
    plt.title(het_title)
    plt.stairs(het_counts, het_bin_edges, fill=True)
    plt.xlabel("proportion of SNPs that are heterozygous")
    plt.ylabel("# samples")
    plt.axvline(het_lb, color="#1111CC")
    plt.axvline(het_ub, color="#CC1111")
    het_fig_g.savefig(f"{vcf}.het.png", dpi=220)

    # Write final VCF and clean up:

    samples_reheader_file = work_dir / f".tmp_samples_{str(uuid.uuid4())[:12]}.txt"

    try:

        if drop_failed:
            with open(vcf_out, "w") as fh:
                subprocess.check_call(
                    ("bcftools", "view", "-s", ",".join(success_samples), str(vcf_out_tmp)),
                    stdout=fh,
                )
        else:
            shutil.move(vcf_out_tmp, vcf_out)

        logger.info(f"[QC] # success = {len(success_samples)}")
        logger.info(f"[QC] # fails = {len(failed_samples)}")
        logger.info(f"[QC] success rate: {len(success_samples) / len(sample_genotypes) * 100:.1f}%")

    finally:
        samples_reheader_file.unlink(missing_ok=True)
        vcf_out_tmp.unlink(missing_ok=True)
