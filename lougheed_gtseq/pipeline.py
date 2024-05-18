from datetime import datetime
from pathlib import Path

from .download_ref import download_genome_if_needed
from .generate_fastq import generate_fastq

# Download reference if needed
# Split FASTA
# Align to reference
# Call alleles
# Rewrite VCF headers


def run_pipeline(species: str, work_dir: Path, run: Path):
    dt = datetime.now().isoformat().replace(":", "_").split(".")[0]
    run_id = f"run_{dt}"

    run_work_dir = work_dir / run_id
    run_work_dir.mkdir()

    download_genome_if_needed(species, work_dir)
    generate_fastq(run, run_work_dir)
