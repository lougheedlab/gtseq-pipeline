import requests
import shutil
import subprocess
from pathlib import Path

from lougheed_gtseq.logger import logger
from lougheed_gtseq.models import Params

__all__ = ["download_genome_if_needed"]

REFERENCE_GENOME_URLS = {
    "polar": (
        "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/687/225/GCF_000687225.1_UrsMar_1.0/"
        "GCF_000687225.1_UrsMar_1.0_genomic.fna.gz"
    ),
}

REFERENCE_GENOME_FILE_NAMES = {
    "polar": "UrsMar_1.0_genomic.fna.gz",
}


def download_genome_if_needed(params: Params) -> Path:
    species = params.species
    work_dir = params.work_dir

    if species not in REFERENCE_GENOME_URLS:
        raise ValueError(f"Invalid species: {species}")

    genomes_folder = work_dir / "ref"
    genomes_folder.mkdir(exist_ok=True)

    genome_file = genomes_folder / REFERENCE_GENOME_FILE_NAMES[species]

    if genome_file.exists():  # TODO: validate checksum and index
        logger.info(f"Already have genome for species '{species}'")
        return genome_file  # already have genome, so return early - nothing to do

    logger.info(f"Attempting to download genome for species '{species}'")

    genome_url = REFERENCE_GENOME_URLS[species]
    with requests.get(genome_url, stream=True) as r:
        with open(genome_file, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)

    logger.info(f"Finished downloading genome to path: {genome_file}")

    logger.info(f"Re-compressing genome as bgzip: {genome_file}")
    subprocess.check_call(("gunzip", str(genome_file)))
    subprocess.check_call(("bgzip", "-@", str(params.processes), str(genome_file).replace(".gz", "")))

    logger.info(f"Indexing downloaded genome: {genome_file}")
    subprocess.check_call(("bwa", "index", genome_file))

    return genome_file
