import shutil

import requests
from pathlib import Path

from .logger import logger

__all__ = ["download_genome_if_needed"]

REFERENCE_GENOME_URLS = {
    "polar": (
        "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/687/225/GCA_000687225.1_UrsMar_1.0/"
        "GCA_000687225.1_UrsMar_1.0_genomic.fna.gz"
    ),
}

REFERENCE_GENOME_FILE_NAMES = {
    "polar": "UrsMar_1.0_genomic.fna.gz",
}


def download_genome_if_needed(species: str, workdir: Path):
    if species not in REFERENCE_GENOME_URLS:
        raise ValueError(f"Invalid species: {species}")

    genomes_folder = workdir / "ref"
    genomes_folder.mkdir(exist_ok=True)

    genome_file = genomes_folder / REFERENCE_GENOME_FILE_NAMES[species]

    if genome_file.exists():  # TODO: validate checksum
        logger.info(f"Already have genome for species '{species}'")
        return  # already have genome, so return early - nothing to do

    logger.info(f"Attempting to download genome for species '{species}'")

    genome_url = REFERENCE_GENOME_URLS[species]
    with requests.get(genome_url, stream=True) as r:
        with open(genome_file, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)

    logger.info(f"Finished downloading genome to path: {genome_file}")
