import subprocess
from pathlib import Path

__all__ = ["fastq_generate"]


def fastq_generate(run: Path, run_work_dir: Path):
    fastq_dir = run_work_dir / "fastq"
    fastq_dir.mkdir()

    subprocess.run(("bcl2fastq", "-R", str(run), "-p", "8", "-o", str(fastq_dir) + "/"))
