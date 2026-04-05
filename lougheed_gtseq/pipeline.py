import pickle
from datetime import datetime
from pathlib import Path
from typing import Callable

from .logger import logger
from .models import Params
from .steps.load_samples import load_samples
from .steps.download_ref import download_genome_if_needed
from .steps.fastq_generate import fastq_generate
from .steps.fastq_split import fastq_split
from .steps.fastq_align import fastq_align
from .steps.call_alleles import call_alleles
from .steps.run_qc import run_qc
from .steps.call_sex_markers import call_sex_markers

__all__ = ["run_pipeline"]


def step(name, call: Callable, work_dir: Path, only_if: bool | None = None):
    if not only_if:
        logger.info("step %s: not needed")
        return None

    done_file = work_dir / f"{name}.done"
    if done_file.exists():
        logger.info("step %s: already done", name)
        with open(done_file, "rb") as fh:
            return pickle.load(fh)
    else:
        logger.info("step %s: executing", name)
        res = call()
        with open(done_file, "wb") as fh:
            pickle.dump(res, fh)
        return res


def run_pipeline(params: Params):
    dt = datetime.now().isoformat().replace(":", "_").split(".")[0]
    run_id = f"run_{dt}"

    if params.continue_run:
        run_work_dir = params.continue_run
    else:
        run_work_dir = params.work_dir / run_id
        run_work_dir.mkdir()

    fastq_dir = run_work_dir / "fastq"
    fastq_dir.mkdir(exist_ok=True)

    # 1. Load samples from sample sheet
    logger.info("Loading samples from sample sheet: %s", params.samples)
    samples = load_samples(params.samples, logger)

    # 2. If R2 is not set: Re-generate FASTQ using bcl2fastq so that we get index sequences in read names
    step(
        "fastq_generate", lambda: fastq_generate(params, fastq_dir), run_work_dir, only_if=isinstance(params.run, Path)
    )

    # 3. Split FASTQ by sample
    sample_fastqs = step(
        "fastq_split",
        lambda: fastq_split(samples, fastq_dir, r1_r2=params.run if isinstance(params.run, tuple) else None),
        run_work_dir,
    )

    # 4. Download the reference genome, if needed
    ref_genome = download_genome_if_needed(params)

    # 5. Align sample FASTQs to the reference genome
    sample_bams = step(
        "fastq_align", lambda: fastq_align(params, run_work_dir, samples, sample_fastqs, ref_genome), run_work_dir
    )

    # 6. Call alleles for the species panel and generate a VCF
    step("call_alleles", lambda: call_alleles(params, run_work_dir, sample_bams, ref_genome), run_work_dir)

    # 7. Run quality control steps on the VCF and generate a second, derived, quality-controlled VCF
    step(
        "run_qc",
        lambda: run_qc(
            params.work_dir,
            params.vcf,
            None,  # infer second output filename from first output filename
            params.min_dp,
            params.min_gq,
            params.min_called_prop,
            params.het_sigma,
            params.drop_failed_samples,
        ),
        run_work_dir,
    )

    # 8. (Optional) call sex-linked markers
    if params.call_sex:
        logger.info("Calling sex-linked markers and generating CSV: %s", params.sex_calls)
        call_sex_markers(params, run_work_dir, samples, sample_fastqs)
