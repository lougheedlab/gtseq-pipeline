from pathlib import Path
from pydantic import BaseModel

__all__ = ["Params", "Sample"]


class Params(BaseModel):
    # Required input information
    species: str
    work_dir: Path
    run: Path
    samples: Path

    # QC parameters
    min_dp: int
    min_gq: int
    min_called_prop: float
    drop_failed_samples: bool

    # Output
    vcf: Path

    # Other parameters
    processes: int


class Sample(BaseModel):
    name: str
    plate: str
    i7_name: str
    i5_name: str
