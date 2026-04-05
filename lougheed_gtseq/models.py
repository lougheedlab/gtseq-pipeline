from pathlib import Path
from pydantic import BaseModel

__all__ = ["SexCallingParams", "Params", "Sample"]


class SexCallingParams(BaseModel):
    # Sex-linked marker calling parameters
    call_sex: bool
    gtseq_scripts: Path
    sex_calls: Path


class Params(SexCallingParams):
    # Required input information
    species: str
    work_dir: Path
    run: Path | tuple[Path, Path]  # Illumina machine output directory or tuple of (R1 fastq, R2 fastq)
    samples: Path

    # QC parameters
    min_dp: int
    min_gq: int
    min_called_prop: float
    het_sigma: int
    drop_failed_samples: bool

    # Output
    vcf: Path
    sex_calls: Path | None  # override to make optional

    # Continuation
    continue_dir: Path | None

    # Other parameters
    genomes: Path | None
    processes: int


class Sample(BaseModel):
    name: str
    plate: str
    i7_name: str
    i5_name: str
