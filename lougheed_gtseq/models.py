from pathlib import Path
from pydantic import BaseModel

__all__ = ["Params", "Sample"]


class Params(BaseModel):
    # Required input information
    species: str
    work_dir: Path
    run: Path
    samples: Path

    # Output
    vcf: Path

    # Other parameters
    processes: int


class Sample(BaseModel):
    name: str
    plate: str
    i7_name: str
    i5_name: str
