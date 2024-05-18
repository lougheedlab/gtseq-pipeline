from datetime import datetime
from pathlib import Path

from .steps.download_ref import download_genome_if_needed
from .steps.fastq_generate import fastq_generate
from .steps.fastq_split import fastq_split
from .steps.fastq_align import fastq_align
from .steps.call_alleles import call_alleles


def run_pipeline(species: str, work_dir: Path, run: Path):
    dt = datetime.now().isoformat().replace(":", "_").split(".")[0]
    run_id = f"run_{dt}"

    run_work_dir = work_dir / run_id
    run_work_dir.mkdir()

    # 1. Re-generate FASTQ using bcl2fastq so that we get index sequences in read names
    fastq_generate(run, run_work_dir)

    # 2. Split FASTQ by sample
    fastq_split()  # TODO

    # 3. Download the reference genome, if needed
    ref_genome = download_genome_if_needed(species, work_dir)

    # 4. Align sample FASTQs to the reference genome
    fastq_align()  # TODO

    # 5. Call alleles for the species panel and generate a VCF
    call_alleles()  # TODO
