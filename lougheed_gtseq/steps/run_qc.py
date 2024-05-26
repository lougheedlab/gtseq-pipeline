import pysam
import re

from pathlib import Path

from ..logger import logger


__all__ = ["run_qc"]

sample_pattern = re.compile(r"./bam/GTSeq_\d{3}_[A-Z]\d{2}_PL_\d_([a-zA-Z0-9_\-]+).sorted.bam")

MIN_DP = 6
MIN_GQ = 18
N_SNPS = 322
CALLED_PROPORTION = 0.5


def run_qc(vcf: Path, vcf_out: Path | None) -> None:
    vf = pysam.VariantFile(str(vcf))

    sample_genotypes: dict[str, list[tuple[str, str]]] = {}

    for s in vf.header.samples:
        sample_id = sample_pattern.match(s).group(1)

        if "control" not in sample_id:
            sample_genotypes[sample_id] = []

    if vcf_out is None:
        out_name = str(vcf.stem) + f"_QC_minDP_{MIN_DP}_minGQ_{MIN_GQ}.vcf"
        vcf_out = vcf.parent / out_name

    vfo = pysam.VariantFile(str(vcf_out), mode="w", header=vf.header)

    logger.info(f"QC: # samples = {len(sample_genotypes)}")

    for variant in vf.fetch():
        new_rec = variant.copy()

        lookup = (variant.ref, *variant.alts)

        for s, sv in variant.samples.items():
            sample_id = sample_pattern.match(s).group(1)

            if "control" in sample_id:
                continue

            if sv["DP"] >= MIN_DP and sv["GQ"] > MIN_GQ:
                gt = tuple(lookup[i] for i in sv["GT"])
            else:
                gt = (".", ".")
                new_rec.samples[s]["GT"] = (None, None)

            sample_genotypes[sample_id].append(gt)

        vfo.write(new_rec)

    prop_calleds = []

    for ss, sg in sample_genotypes.items():
        prop_called = sum(1 for gg in sg if "." not in gg) / len(sg)
        if prop_called > CALLED_PROPORTION:
            prop_calleds.append(prop_called)

    logger.info(
        f"QC: # success = {len(prop_calleds)} | avg % called = {sum(prop_calleds) / len(prop_calleds) * 100:.1f}")
