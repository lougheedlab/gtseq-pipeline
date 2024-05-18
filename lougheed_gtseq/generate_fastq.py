import subprocess
from pathlib import Path

__all__ = ["generate_fastq"]


def generate_fastq(run: Path, run_work_dir: Path):
    fastq_dir = run_work_dir / "fastq"
    fastq_dir.mkdir()

    subprocess.run(("bcl2fastq", "-R", str(run), "-p", "8", "-o", str(fastq_dir) + "/"))
