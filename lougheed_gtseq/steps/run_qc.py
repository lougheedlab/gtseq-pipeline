import pysam
import re
import shutil
import subprocess
import uuid

from pathlib import Path

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
    drop_failed: bool,
) -> None:
    vf = pysam.VariantFile(str(vcf))

    sample_genotypes: dict[str, list[tuple[str, str]]] = {}
    sample_p_called: dict[str, float] = {}

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

        success_samples = []
        success_props = []
        fail_props = []

        for ss, sg in sample_genotypes.items():
            prop_called = sum(1 for gg in sg if "." not in gg) / len(sg)
            sample_p_called[ss] = prop_called
            if prop_called >= min_prop:
                success_samples.append(ss)
                success_props.append(prop_called)
            else:
                fail_props.append(prop_called)

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

        logger.info(f"[QC] # success = {len(success_props)}")
        logger.info(f"[QC]     - avg % called (successes) = {sum(success_props) / len(success_props) * 100:.1f}")
        logger.info(f"[QC] # fails = {len(sample_genotypes) - len(success_props)}")
        logger.info(f"[QC]     - avg % called (fails) = {sum(fail_props) / len(fail_props) * 100:.1f}")
        logger.info(f"[QC] success rate: {len(success_props) / len(sample_genotypes) * 100:.1f}%")

    finally:
        samples_reheader_file.unlink(missing_ok=True)
        vcf_out_tmp.unlink(missing_ok=True)
