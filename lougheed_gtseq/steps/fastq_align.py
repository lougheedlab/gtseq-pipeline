import subprocess

from ..models import Params, Sample

__all__ = ["fastq_align"]


def fastq_align(params: Params, samples: list[Sample]):
    for sample in samples:
        subprocess.run((
            "bwa", "mem", "-t", str(params.processes),  # TODO
        ))
        # sam to bam & sort & index
