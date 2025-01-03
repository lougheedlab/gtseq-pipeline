from datetime import datetime

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


def run_pipeline(params: Params):
    dt = datetime.now().isoformat().replace(":", "_").split(".")[0]
    run_id = f"run_{dt}"

    run_work_dir = params.work_dir / run_id
    run_work_dir.mkdir()

    # 1. Load samples from sample sheet
    logger.info("Loading samples from sample sheet: %s", params.samples)
    samples = load_samples(params.samples)

    # 2. Re-generate FASTQ using bcl2fastq so that we get index sequences in read names
    logger.info("Generating FASTQ with bcl2fastq")
    fastq_dir = fastq_generate(params, run_work_dir)

    # 3. Split FASTQ by sample
    logger.info("Splitting FASTQ by sample")
    sample_fastqs = fastq_split(samples, fastq_dir)

    # 4. Download the reference genome, if needed
    ref_genome = download_genome_if_needed(params)

    # 5. Align sample FASTQs to the reference genome
    logger.info("Aligning sample FASTQs to reference genome")
    sample_bams = fastq_align(params, run_work_dir, samples, sample_fastqs, ref_genome)

    # 6. Call alleles for the species panel and generate a VCF
    logger.info("Calling sample SNPs and generating a batch VCF: %s", params.vcf)
    call_alleles(params, run_work_dir, sample_bams, ref_genome)

    # 7. Run quality control steps on the VCF and generate a second, derived, quality-controlled VCF
    logger.info("Running quality control steps and generating a batch QCed VCF")
    run_qc(
        params.work_dir,
        params.vcf,
        None,  # infer second output filename from first output filename
        params.min_dp,
        params.min_gq,
        params.min_called_prop,
        params.het_sigma,
        params.drop_failed_samples,
    )

    # 8. (Optional) call sex-linked markers
    if params.call_sex:
        logger.info("Calling sex-linked markers and generating CSV: %s", params.sex_calls)
        call_sex_markers(params, run_work_dir, samples, sample_fastqs)
