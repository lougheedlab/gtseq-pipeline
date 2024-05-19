import subprocess
from pathlib import Path

from ..models import Params

__all__ = ["fastq_generate"]


def fastq_generate(params: Params, run_work_dir: Path) -> Path:
    fastq_dir = run_work_dir / "fastq"
    fastq_dir.mkdir()

    subprocess.run(
        (
            "bcl2fastq",
            "-R",
            str(params.run),
            "-p",
            str(params.processes),
            "-o",
            str(fastq_dir) + "/",
        )
    )

    return fastq_dir
