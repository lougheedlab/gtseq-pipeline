from datetime import datetime

from .models import Params
from .steps.load_samples import load_samples
from .steps.download_ref import download_genome_if_needed
from .steps.fastq_generate import fastq_generate
from .steps.fastq_split import fastq_split
from .steps.fastq_align import fastq_align
from .steps.call_alleles import call_alleles

__all__ = ["run_pipeline"]


def run_pipeline(params: Params):
    dt = datetime.now().isoformat().replace(":", "_").split(".")[0]
    run_id = f"run_{dt}"

    run_work_dir = params.work_dir / run_id
    run_work_dir.mkdir()

    # 1. Load samples from sample sheet
    samples = load_samples(params.samples)

    # 2. Re-generate FASTQ using bcl2fastq so that we get index sequences in read names
    fastq_generate(params.run, run_work_dir)

    # 3. Split FASTQ by sample
    fastq_split(samples)  # TODO

    # 4. Download the reference genome, if needed
    ref_genome = download_genome_if_needed(params)

    # 5. Align sample FASTQs to the reference genome
    fastq_align(params, samples)

    # 6. Call alleles for the species panel and generate a VCF
    call_alleles()  # TODO
