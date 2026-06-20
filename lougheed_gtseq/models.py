from pathlib import Path
from pydantic import BaseModel, Field

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
    batch: str
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
    continue_run: Path | None

    # Other parameters
    genomes: Path | None
    processes: int


class Sample(BaseModel):
    sample_id: str
    batch: str
    plate: int = Field(..., gt=0, lt=12)
    i7: int | None = Field(..., gt=0, lt=17)  # 001, 002, 003, ..., 016
    i5: str | None = Field(..., pattern=r"^[A-H](0[0-9]|1[0-2])$")  # A01, ..., H12

    def full_name(self) -> str:
        return f"{self.sample_id}_{self.batch}_plate_{self.plate}_{str(self.i7).zfill(3)}_{self.i5}"
